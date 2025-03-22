import os
import shutil
import subprocess
from tempfile import NamedTemporaryFile

from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files.base import ContentFile
from django.utils.encoding import force_str

from pipeline.conf import settings
from pipeline.exceptions import CompilerError
from pipeline.utils import set_std_streams_blocking, to_class


class Compiler:
    def __init__(self, storage=None, verbose=False):
        if storage is None:
            storage = staticfiles_storage
        self.storage = storage
        self.verbose = verbose

    @property
    def compilers(self):
        return [to_class(compiler) for compiler in settings.COMPILERS]

    def compile(self, paths, compiler_options={}, force=False):
        def _compile(input_path):
            for compiler in self.compilers:
                compiler = compiler(verbose=self.verbose, storage=self.storage)
                if compiler.match_file(input_path):
                    try:
                        infile = self.storage.path(input_path)
                    except NotImplementedError:
                        infile = finders.find(input_path)
                    project_infile = finders.find(input_path)
                    outfile = compiler.output_path(infile, compiler.output_extension)
                    outdated = compiler.is_outdated(project_infile, outfile)
                    compiler.compile_file(
                        project_infile,
                        outfile,
                        outdated=outdated,
                        force=force,
                        **compiler_options,
                    )

                    return compiler.output_path(input_path, compiler.output_extension)
            else:
                return input_path

        try:
            import multiprocessing
            from concurrent import futures
        except ImportError:
            return list(map(_compile, paths))
        else:
            with futures.ThreadPoolExecutor(
                max_workers=multiprocessing.cpu_count()
            ) as executor:
                return list(executor.map(_compile, paths))


class CompilerBase:
    def __init__(self, verbose, storage):
        self.verbose = verbose
        self.storage = storage

    def match_file(self, filename):
        raise NotImplementedError

    def compile_file(self, infile, outfile, outdated=False, force=False):
        raise NotImplementedError

    def save_file(self, path, content):
        return self.storage.save(path, ContentFile(content))

    def read_file(self, path):
        file = self.storage.open(path, "rb")
        content = file.read()
        file.close()
        return content

    def output_path(self, path, extension):
        path = os.path.splitext(path)
        return ".".join((path[0], extension))

    def is_outdated(self, infile, outfile):
        if not os.path.exists(outfile):
            return True

        try:
            return os.path.getmtime(infile) > os.path.getmtime(outfile)
        except OSError:
            return True


class SubProcessCompiler(CompilerBase):
    def execute_command(self, command, cwd=None, stdout_captured=None):
        """Execute a command at cwd, saving its normal output at
        stdout_captured. Errors, defined as nonzero return code or a failure
        to start execution, will raise a CompilerError exception with a
        description of the cause. They do not write output.

        This is file-system safe (any valid file names are allowed, even with
        spaces or crazy characters) and OS agnostic (existing and future OSes
        that Python supports should already work).

        The only thing weird here is that any incoming command arg item may
        itself be a tuple. This allows compiler implementations to look clean
        while supporting historical string config settings and maintaining
        backwards compatibility. Thus, we flatten one layer deep.
         ((env, foocomp), infile, (-arg,)) -> (env, foocomp, infile, -arg)
        """
        argument_list = []
        for flattening_arg in command:
            if isinstance(flattening_arg, (str,)):
                argument_list.append(flattening_arg)
            else:
                argument_list.extend(flattening_arg)

        # The first element in argument_list is the program that will be
        # executed; if it is '', then a PermissionError will be raised.
        # Thus empty arguments are filtered out from argument_list
        argument_list = list(filter(None, argument_list))
        stdout = None
        try:
            # We always catch stdout in a file, but we may not have a use for it.
            temp_file_container = (
                cwd or os.path.dirname(stdout_captured or "") or os.getcwd()
            )
            with NamedTemporaryFile(
                "wb", delete=False, dir=temp_file_container
            ) as stdout:
                compiling = subprocess.Popen(
                    argument_list, cwd=cwd, stdout=stdout, stderr=subprocess.PIPE
                )
                _, stderr = compiling.communicate()
                set_std_streams_blocking()

            if compiling.returncode != 0:
                stdout_captured = None  # Don't save erroneous result.
                raise CompilerError(
                    f"{argument_list!r} exit code {compiling.returncode}\n{stderr}",
                    command=argument_list,
                    error_output=force_str(stderr),
                )

            # User wants to see everything that happened.
            if self.verbose:
                with open(stdout.name, "rb") as out:
                    print(out.read())
                print(stderr)
        except OSError as e:
            stdout_captured = None  # Don't save erroneous result.
            raise CompilerError(e, command=argument_list, error_output=str(e))
        finally:
            # Decide what to do with captured stdout.
            if stdout:
                if stdout_captured:
                    shutil.move(
                        stdout.name, os.path.join(cwd or os.curdir, stdout_captured)
                    )
                else:
                    os.remove(stdout.name)
