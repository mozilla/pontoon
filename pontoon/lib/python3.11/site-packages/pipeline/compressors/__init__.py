import base64
import os
import posixpath
import re
import subprocess
from itertools import takewhile

from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.encoding import force_str, smart_bytes

from pipeline.conf import settings
from pipeline.exceptions import CompressorError
from pipeline.utils import relpath, set_std_streams_blocking, to_class

URL_DETECTOR = r"""url\((['"]?)\s*(.*?)\1\)"""
URL_REPLACER = r"""url\(__EMBED__(.+?)(\?\d+)?\)"""
NON_REWRITABLE_URL = re.compile(r"^(#|http:|https:|data:|//)")

DEFAULT_TEMPLATE_FUNC = "template"
TEMPLATE_FUNC = r"""var template = function(str){var fn = new Function('obj', 'var __p=[],print=function(){__p.push.apply(__p,arguments);};with(obj||{}){__p.push(\''+str.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/<%=([\s\S]+?)%>/g,function(match,code){return "',"+code.replace(/\\'/g, "'")+",'";}).replace(/<%([\s\S]+?)%>/g,function(match,code){return "');"+code.replace(/\\'/g, "'").replace(/[\r\n\t]/g,' ')+"__p.push('";}).replace(/\r/g,'\\r').replace(/\n/g,'\\n').replace(/\t/g,'\\t')+"');}return __p.join('');");return fn;};"""  # noqa

MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
    ".ttf": "font/truetype",
    ".otf": "font/opentype",
    ".woff": "font/woff",
}
EMBED_EXTS = MIME_TYPES.keys()
FONT_EXTS = [".ttf", ".otf", ".woff"]


class Compressor:
    asset_contents = {}

    def __init__(self, storage=None, verbose=False):
        if storage is None:
            storage = staticfiles_storage
        self.storage = storage
        self.verbose = verbose

    @property
    def js_compressor(self):
        return to_class(settings.JS_COMPRESSOR)

    @property
    def css_compressor(self):
        return to_class(settings.CSS_COMPRESSOR)

    def compress_js(self, paths, templates=None, **kwargs):
        """Concatenate and compress JS files"""
        js = self.concatenate(paths)
        if templates:
            js = js + self.compile_templates(templates)

        if not settings.DISABLE_WRAPPER:
            js = settings.JS_WRAPPER % js

        compressor = self.js_compressor
        if compressor:
            js = getattr(compressor(verbose=self.verbose), "compress_js")(js)

        return js

    def compress_css(self, paths, output_filename, variant=None, **kwargs):
        """Concatenate and compress CSS files"""
        css = self.concatenate_and_rewrite(paths, output_filename, variant)
        compressor = self.css_compressor
        if compressor:
            css = getattr(compressor(verbose=self.verbose), "compress_css")(css)
        if not variant:
            return css
        elif variant == "datauri":
            return self.with_data_uri(css)
        else:
            raise CompressorError(f'"{variant}" is not a valid variant')

    def compile_templates(self, paths):
        compiled = []
        if not paths:
            return ""
        namespace = settings.TEMPLATE_NAMESPACE
        base_path = self.base_path(paths)
        for path in paths:
            contents = self.read_text(path)
            contents = re.sub("\r?\n", "\\\\n", contents)
            contents = re.sub("'", "\\'", contents)
            name = self.template_name(path, base_path)
            compiled.append(
                "{}['{}'] = {}('{}');\n".format(
                    namespace, name, settings.TEMPLATE_FUNC, contents
                )
            )
        if settings.TEMPLATE_FUNC == DEFAULT_TEMPLATE_FUNC:
            compiler = TEMPLATE_FUNC
        else:
            compiler = ""
        return "\n".join(
            [
                "{namespace} = {namespace} || {{}};".format(namespace=namespace),
                compiler,
                "".join(compiled),
            ]
        )

    def base_path(self, paths):
        def names_equal(name):
            return all(n == name[0] for n in name[1:])

        directory_levels = zip(*[p.split(os.sep) for p in paths])
        return os.sep.join(x[0] for x in takewhile(names_equal, directory_levels))

    def template_name(self, path, base):
        """Find out the name of a JS template"""
        if not base:
            path = os.path.basename(path)
        if path == base:
            base = os.path.dirname(path)
        name = re.sub(
            r"^{}[\/\\]?(.*){}$".format(
                re.escape(base), re.escape(settings.TEMPLATE_EXT)
            ),
            r"\1",
            path,
        )
        return re.sub(r"[\/\\]", settings.TEMPLATE_SEPARATOR, name)

    def concatenate_and_rewrite(self, paths, output_filename, variant=None):
        """Concatenate together files and rewrite urls"""
        stylesheets = []
        for path in paths:

            def reconstruct(match):
                quote = match.group(1) or ""
                asset_path = match.group(2)
                if NON_REWRITABLE_URL.match(asset_path):
                    return f"url({quote}{asset_path}{quote})"
                asset_url = self.construct_asset_path(
                    asset_path, path, output_filename, variant
                )
                return f"url({asset_url})"

            content = self.read_text(path)
            # content needs to be unicode to avoid explosions with non-ascii chars
            content = re.sub(URL_DETECTOR, reconstruct, content)
            stylesheets.append(content)
        return "\n".join(stylesheets)

    def concatenate(self, paths):
        """Concatenate together a list of files"""
        # Note how a semicolon is added between the two files to make sure that
        # their behavior is not changed. '(expression1)\n(expression2)' calls
        # `expression1` with `expression2` as an argument! Superfluos semicolons
        # are valid in JavaScript and will be removed by the minifier.
        return "\n;".join([self.read_text(path) for path in paths])

    def construct_asset_path(self, asset_path, css_path, output_filename, variant=None):
        """Return a rewritten asset URL for a stylesheet"""
        public_path = self.absolute_path(
            asset_path,
            os.path.dirname(css_path).replace("\\", "/"),
        )
        if self.embeddable(public_path, variant):
            return "__EMBED__%s" % public_path
        if not posixpath.isabs(asset_path):
            asset_path = self.relative_path(public_path, output_filename)
        return asset_path

    def embeddable(self, path, variant):
        """Is the asset embeddable ?"""
        name, ext = os.path.splitext(path)
        font = ext in FONT_EXTS
        if not variant:
            return False
        if not (
            re.search(settings.EMBED_PATH, path.replace("\\", "/"))
            and self.storage.exists(path)
        ):
            return False
        if ext not in EMBED_EXTS:
            return False
        if not (
            font or len(self.encoded_content(path)) < settings.EMBED_MAX_IMAGE_SIZE
        ):
            return False
        return True

    def with_data_uri(self, css):
        def datauri(match):
            path = match.group(1)
            mime_type = self.mime_type(path)
            data = self.encoded_content(path)
            return f'url("data:{mime_type};charset=utf-8;base64,{data}")'

        return re.sub(URL_REPLACER, datauri, css)

    def encoded_content(self, path):
        """Return the base64 encoded contents"""
        if path in self.__class__.asset_contents:
            return self.__class__.asset_contents[path]
        data = self.read_bytes(path)
        self.__class__.asset_contents[path] = force_str(base64.b64encode(data))
        return self.__class__.asset_contents[path]

    def mime_type(self, path):
        """Get mime-type from filename"""
        name, ext = os.path.splitext(path)
        return MIME_TYPES[ext]

    def absolute_path(self, path, start):
        """
        Return the absolute public path for an asset,
        given the path of the stylesheet that contains it.
        """
        if posixpath.isabs(path):
            path = posixpath.join(staticfiles_storage.location, path)
        else:
            path = posixpath.join(start, path)
        return posixpath.normpath(path)

    def relative_path(self, absolute_path, output_filename):
        """Rewrite paths relative to the output stylesheet path"""
        absolute_path = posixpath.join(settings.PIPELINE_ROOT, absolute_path)
        output_path = posixpath.join(
            settings.PIPELINE_ROOT, posixpath.dirname(output_filename)
        )
        return relpath(absolute_path, output_path)

    def read_bytes(self, path):
        """Read file content in binary mode"""
        file = staticfiles_storage.open(path)
        content = file.read()
        file.close()
        return content

    def read_text(self, path):
        content = self.read_bytes(path)
        return force_str(content)


class CompressorBase:
    def __init__(self, verbose):
        self.verbose = verbose

    def filter_css(self, css):
        raise NotImplementedError

    def filter_js(self, js):
        raise NotImplementedError


class SubProcessCompressor(CompressorBase):
    def execute_command(self, command, content):
        argument_list = []
        for flattening_arg in command:
            if isinstance(flattening_arg, (str,)):
                argument_list.append(flattening_arg)
            else:
                argument_list.extend(flattening_arg)

        pipe = subprocess.Popen(
            argument_list,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if content:
            content = smart_bytes(content)
        stdout, stderr = pipe.communicate(content)
        set_std_streams_blocking()
        if stderr.strip() and pipe.returncode != 0:
            raise CompressorError(force_str(stderr))
        elif self.verbose:
            print(force_str(stderr))
        return force_str(stdout)


class NoopCompressor(CompressorBase):
    def compress_js(self, js):
        return js

    def compress_css(self, css):
        return css
