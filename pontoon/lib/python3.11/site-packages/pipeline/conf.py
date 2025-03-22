import os
import shlex
from collections.abc import MutableMapping

from django.conf import settings as _settings
from django.core.signals import setting_changed
from django.dispatch import receiver

DEFAULTS = {
    "PIPELINE_ENABLED": not _settings.DEBUG,
    "PIPELINE_COLLECTOR_ENABLED": True,
    "PIPELINE_ROOT": _settings.STATIC_ROOT,
    "PIPELINE_URL": _settings.STATIC_URL,
    "SHOW_ERRORS_INLINE": _settings.DEBUG,
    "CSS_COMPRESSOR": "pipeline.compressors.yuglify.YuglifyCompressor",
    "JS_COMPRESSOR": "pipeline.compressors.yuglify.YuglifyCompressor",
    "COMPILERS": [],
    "STYLESHEETS": {},
    "JAVASCRIPT": {},
    "TEMPLATE_NAMESPACE": "window.JST",
    "TEMPLATE_EXT": ".jst",
    "TEMPLATE_FUNC": "template",
    "TEMPLATE_SEPARATOR": "_",
    "DISABLE_WRAPPER": False,
    "JS_WRAPPER": "(function() {\n%s\n}).call(this);",
    "CSSTIDY_BINARY": "/usr/bin/env csstidy",
    "CSSTIDY_ARGUMENTS": "--template=highest",
    "YUGLIFY_BINARY": "/usr/bin/env yuglify",
    "YUGLIFY_CSS_ARGUMENTS": "--terminal",
    "YUGLIFY_JS_ARGUMENTS": "--terminal",
    "YUI_BINARY": "/usr/bin/env yuicompressor",
    "YUI_CSS_ARGUMENTS": "",
    "YUI_JS_ARGUMENTS": "",
    "CLOSURE_BINARY": "/usr/bin/env closure",
    "CLOSURE_ARGUMENTS": "",
    "UGLIFYJS_BINARY": "/usr/bin/env uglifyjs",
    "UGLIFYJS_ARGUMENTS": "",
    "TERSER_BINARY": "/usr/bin/env terser",
    "TERSER_ARGUMENTS": "--compress",
    "CSSMIN_BINARY": "/usr/bin/env cssmin",
    "CSSMIN_ARGUMENTS": "",
    "COFFEE_SCRIPT_BINARY": "/usr/bin/env coffee",
    "COFFEE_SCRIPT_ARGUMENTS": "",
    "BABEL_BINARY": "/usr/bin/env babel",
    "BABEL_ARGUMENTS": "",
    "LIVE_SCRIPT_BINARY": "/usr/bin/env lsc",
    "LIVE_SCRIPT_ARGUMENTS": "",
    "TYPE_SCRIPT_BINARY": "/usr/bin/env tsc",
    "TYPE_SCRIPT_ARGUMENTS": "",
    "SASS_BINARY": "/usr/bin/env sass",
    "SASS_ARGUMENTS": "",
    "STYLUS_BINARY": "/usr/bin/env stylus",
    "STYLUS_ARGUMENTS": "",
    "LESS_BINARY": "/usr/bin/env lessc",
    "LESS_ARGUMENTS": "",
    "MIMETYPES": (
        (("text/coffeescript"), (".coffee")),
        (("text/less"), (".less")),
        (("text/javascript"), (".js")),
        (("text/typescript"), (".ts")),
        (("text/x-sass"), (".sass")),
        (("text/x-scss"), (".scss")),
    ),
    "EMBED_MAX_IMAGE_SIZE": 32700,
    "EMBED_PATH": r"[/]?embed/",
}


class PipelineSettings(MutableMapping):
    """
    Container object for pipeline settings
    """

    def __init__(self, wrapped_settings):
        self.settings = DEFAULTS.copy()
        self.settings.update(wrapped_settings)

    def __getitem__(self, key):
        value = self.settings[key]
        if key.endswith(("_BINARY", "_ARGUMENTS")):
            if isinstance(value, (str,)):
                return tuple(shlex.split(value, posix=(os.name == "posix")))
            return tuple(value)
        return value

    def __setitem__(self, key, value):
        self.settings[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.settings)

    def __len__(self):
        return len(self.settings)

    def __getattr__(self, name):
        return self.__getitem__(name)


settings = PipelineSettings(_settings.PIPELINE)


@receiver(setting_changed)
def reload_settings(**kwargs):
    if kwargs["setting"] == "PIPELINE":
        settings.update(kwargs["value"])
