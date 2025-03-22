"""Support for referencing Pipeline packages in forms and widgets."""

from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.functional import cached_property

from .collector import default_collector
from .conf import settings
from .packager import Packager


class PipelineFormMediaProperty:
    """A property that converts Pipeline packages to lists of files.

    This is used behind the scenes for any Media classes that subclass
    :py:class:`PipelineFormMedia`. When accessed, it converts any Pipeline
    packages into lists of media files and returns or forwards on lookups to
    that list.
    """

    def __init__(self, get_media_files_func, media_cls, extra_files):
        """Initialize the property.

        Args:
            get_media_files_func (callable):
                The function to call to generate the media files.

            media_cls (type):
                The Media class owning the property.

            extra_files (object):
                Files listed in the original ``css`` or ``js`` attribute on
                the Media class.
        """
        self._get_media_files_func = get_media_files_func
        self._media_cls = media_cls
        self._extra_files = extra_files

    @cached_property
    def _media_files(self):
        """The media files represented by the property."""
        return self._get_media_files_func(self._media_cls, self._extra_files)

    def __get__(self, *args, **kwargs):
        """Return the media files when accessed as an attribute.

        This is called when accessing the attribute directly through the
        Media class (for example, ``Media.css``). It returns the media files
        directly.

        Args:
            *args (tuple, unused):
                Unused positional arguments.

            **kwargs (dict, unused):
                Unused keyword arguments.

        Returns:
            object:
            The list or dictionary containing the media files definition.
        """
        return self._media_files

    def __getattr__(self, attr_name):
        """Return an attribute on the media files definition.

        This is called when accessing an attribute that doesn't otherwise
        exist in the property's dictionary. The call is forwarded onto the
        media files definition.

        Args:
            attr_name (unicode):
                The attribute name.

        Returns:
            object:
            The attribute value.

        Raises:
            AttributeError:
                An attribute with this name could not be found.
        """
        return getattr(self._media_files, attr_name)

    def __iter__(self):
        """Iterate through the media files definition.

        This is called when attempting to iterate over this property. It
        iterates over the media files definition instead.

        Yields:
            object:
            Each entry in the media files definition.
        """
        return iter(self._media_files)


class PipelineFormMediaMetaClass(type):
    """Metaclass for the PipelineFormMedia class.

    This is responsible for converting CSS/JavaScript packages defined in
    Pipeline into lists of files to include on a page. It handles access to the
    :py:attr:`css` and :py:attr:`js` attributes on the class, generating a
    list of files to return based on the Pipelined packages and individual
    files listed in the :py:attr:`css`/:py:attr:`css_packages` or
    :py:attr:`js`/:py:attr:`js_packages` attributes.
    """

    def __new__(cls, name, bases, attrs):
        """Construct the class.

        Args:
            name (bytes):
                The name of the class.

            bases (tuple):
                The base classes for the class.

            attrs (dict):
                The attributes going into the class.

        Returns:
            type:
            The new class.
        """
        new_class = super().__new__(cls, name, bases, attrs)

        # If we define any packages, we'll need to use our special
        # PipelineFormMediaProperty class. We use this instead of intercepting
        # in __getattribute__ because Django does not access them through
        # normal property access. Instead, grabs the Media class's __dict__
        # and accesses them from there. By using these special properties, we
        # can handle direct access (Media.css) and dictionary-based access
        # (Media.__dict__['css']).
        if "css_packages" in attrs:
            new_class.css = PipelineFormMediaProperty(
                cls._get_css_files, new_class, attrs.get("css") or {}
            )

        if "js_packages" in attrs:
            new_class.js = PipelineFormMediaProperty(
                cls._get_js_files, new_class, attrs.get("js") or []
            )

        return new_class

    def _get_css_files(cls, extra_files):
        """Return all CSS files from the Media class.

        Args:
            extra_files (dict):
                The contents of the Media class's original :py:attr:`css`
                attribute, if one was provided.

        Returns:
            dict:
            The CSS media types and files to return for the :py:attr:`css`
            attribute.
        """
        packager = Packager()
        css_packages = getattr(cls, "css_packages", {})

        return {
            media_target: cls._get_media_files(
                packager=packager,
                media_packages=media_packages,
                media_type="css",
                extra_files=extra_files.get(media_target, []),
            )
            for media_target, media_packages in css_packages.items()
        }

    def _get_js_files(cls, extra_files):
        """Return all JavaScript files from the Media class.

        Args:
            extra_files (list):
                The contents of the Media class's original :py:attr:`js`
                attribute, if one was provided.

        Returns:
            list:
            The JavaScript files to return for the :py:attr:`js` attribute.
        """
        return cls._get_media_files(
            packager=Packager(),
            media_packages=getattr(cls, "js_packages", {}),
            media_type="js",
            extra_files=extra_files,
        )

    def _get_media_files(cls, packager, media_packages, media_type, extra_files):
        """Return source or output media files for a list of packages.

        This will go through the media files belonging to the provided list
        of packages referenced in a Media class and return the output files
        (if Pipeline is enabled) or the source files (if not enabled).

        Args:
            packager (pipeline.packager.Packager):
                The packager responsible for media compilation for this type
                of package.

            media_packages (list of unicode):
                The list of media packages referenced in Media to compile or
                return.

            extra_files (list of unicode):
                The list of extra files to include in the result. This would
                be the list stored in the Media class's original :py:attr:`css`
                or :py:attr:`js` attributes.

        Returns:
            list:
            The list of media files for the given packages.
        """
        source_files = list(extra_files)

        if not settings.PIPELINE_ENABLED and settings.PIPELINE_COLLECTOR_ENABLED:
            default_collector.collect()

        for media_package in media_packages:
            package = packager.package_for(media_type, media_package)

            if settings.PIPELINE_ENABLED:
                source_files.append(staticfiles_storage.url(package.output_filename))
            else:
                source_files += packager.compile(package.paths)

        return source_files


class PipelineFormMedia(metaclass=PipelineFormMediaMetaClass):
    """Base class for form or widget Media classes that use Pipeline packages.

    Forms or widgets that need custom CSS or JavaScript media on a page can
    define a standard :py:class:`Media` class that subclasses this class,
    listing the CSS or JavaScript packages in :py:attr:`css_packages` and
    :py:attr:`js_packages` attributes. These are formatted the same as the
    standard :py:attr:`css` and :py:attr:`js` attributes, but reference
    Pipeline package names instead of individual source files.

    If Pipeline is enabled, these will expand to the output files for the
    packages. Otherwise, these will expand to the list of source files for the
    packages.

    Subclasses can also continue to define :py:attr:`css` and :py:attr:`js`
    attributes, which will be returned along with the other output/source
    files.

    Example:

        from django import forms
        from pipeline.forms import PipelineFormMedia


        class MyForm(forms.Media):
            ...

            class Media(PipelineFormMedia):
                css_packages = {
                    'all': ('my-form-styles-package',
                            'other-form-styles-package'),
                    'print': ('my-form-print-styles-package',),
                }

                js_packages = ('my-form-scripts-package',)
                js = ('some-file.js',)
    """
