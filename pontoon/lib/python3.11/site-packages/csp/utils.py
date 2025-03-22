import copy
import re
from collections import OrderedDict
from itertools import chain

from django.conf import settings
from django.utils.encoding import force_str


def from_settings():
    return {
        # Fetch Directives
        "child-src": getattr(settings, "CSP_CHILD_SRC", None),
        "connect-src": getattr(settings, "CSP_CONNECT_SRC", None),
        "default-src": getattr(settings, "CSP_DEFAULT_SRC", ["'self'"]),
        "script-src": getattr(settings, "CSP_SCRIPT_SRC", None),
        "script-src-attr": getattr(settings, "CSP_SCRIPT_SRC_ATTR", None),
        "script-src-elem": getattr(settings, "CSP_SCRIPT_SRC_ELEM", None),
        "object-src": getattr(settings, "CSP_OBJECT_SRC", None),
        "style-src": getattr(settings, "CSP_STYLE_SRC", None),
        "style-src-attr": getattr(settings, "CSP_STYLE_SRC_ATTR", None),
        "style-src-elem": getattr(settings, "CSP_STYLE_SRC_ELEM", None),
        "font-src": getattr(settings, "CSP_FONT_SRC", None),
        "frame-src": getattr(settings, "CSP_FRAME_SRC", None),
        "img-src": getattr(settings, "CSP_IMG_SRC", None),
        "manifest-src": getattr(settings, "CSP_MANIFEST_SRC", None),
        "media-src": getattr(settings, "CSP_MEDIA_SRC", None),
        "prefetch-src": getattr(settings, "CSP_PREFETCH_SRC", None),
        "worker-src": getattr(settings, "CSP_WORKER_SRC", None),
        # Document Directives
        "base-uri": getattr(settings, "CSP_BASE_URI", None),
        "plugin-types": getattr(settings, "CSP_PLUGIN_TYPES", None),
        "sandbox": getattr(settings, "CSP_SANDBOX", None),
        # Navigation Directives
        "form-action": getattr(settings, "CSP_FORM_ACTION", None),
        "frame-ancestors": getattr(settings, "CSP_FRAME_ANCESTORS", None),
        "navigate-to": getattr(settings, "CSP_NAVIGATE_TO", None),
        # Reporting Directives
        "report-uri": getattr(settings, "CSP_REPORT_URI", None),
        "report-to": getattr(settings, "CSP_REPORT_TO", None),
        "require-sri-for": getattr(settings, "CSP_REQUIRE_SRI_FOR", None),
        # trusted Types Directives
        "require-trusted-types-for": getattr(settings, "CSP_REQUIRE_TRUSTED_TYPES_FOR", None),
        "trusted-types": getattr(settings, "CSP_TRUSTED_TYPES", None),
        # Other Directives
        "upgrade-insecure-requests": getattr(settings, "CSP_UPGRADE_INSECURE_REQUESTS", False),
        "block-all-mixed-content": getattr(settings, "CSP_BLOCK_ALL_MIXED_CONTENT", False),
    }


def build_policy(config=None, update=None, replace=None, nonce=None):
    """Builds the policy as a string from the settings."""

    if config is None:
        config = from_settings()
        # Be careful, don't mutate config as it could be from settings

    update = update if update is not None else {}
    replace = replace if replace is not None else {}
    csp = {}

    for k in set(chain(config, replace)):
        if k in replace:
            v = replace[k]
        else:
            v = config[k]
        if v is not None:
            v = copy.copy(v)
            if not isinstance(v, (list, tuple)):
                v = (v,)
            csp[k] = v

    for k, v in update.items():
        if v is not None:
            if not isinstance(v, (list, tuple)):
                v = (v,)
            if csp.get(k) is None:
                csp[k] = v
            else:
                csp[k] += tuple(v)

    report_uri = csp.pop("report-uri", None)

    policy_parts = {}
    for key, value in csp.items():
        # flag directives with an empty directive value
        if len(value) and value[0] is True:
            policy_parts[key] = ""
        elif len(value) and value[0] is False:
            pass
        else:  # directives with many values like src lists
            policy_parts[key] = " ".join(value)

    if report_uri:
        report_uri = map(force_str, report_uri)
        policy_parts["report-uri"] = " ".join(report_uri)

    if nonce:
        include_nonce_in = getattr(settings, "CSP_INCLUDE_NONCE_IN", ["default-src"])
        for section in include_nonce_in:
            policy = policy_parts.get(section, "")
            policy_parts[section] = ("{} {}".format(policy, "'nonce-%s'" % nonce)).strip()

    return "; ".join([f"{k} {val}".strip() for k, val in policy_parts.items()])


def _default_attr_mapper(attr_name, val):
    if val:
        return f' {attr_name}="{val}"'
    else:
        return ""


def _bool_attr_mapper(attr_name, val):
    # Only return the bare word if the value is truthy
    # ie - defer=False should actually return an empty string
    if val:
        return f" {attr_name}"
    else:
        return ""


def _async_attr_mapper(attr_name, val):
    """The `async` attribute works slightly different than the other bool
    attributes. It can be set explicitly to `false` with no surrounding quotes
    according to the spec."""
    if val in [False, "False"]:
        return f" {attr_name}=false"
    elif val:
        return f" {attr_name}"
    else:
        return ""


# Allow per-attribute customization of returned string template
SCRIPT_ATTRS = OrderedDict()
SCRIPT_ATTRS["nonce"] = _default_attr_mapper
SCRIPT_ATTRS["id"] = _default_attr_mapper
SCRIPT_ATTRS["src"] = _default_attr_mapper
SCRIPT_ATTRS["type"] = _default_attr_mapper
SCRIPT_ATTRS["async"] = _async_attr_mapper
SCRIPT_ATTRS["defer"] = _bool_attr_mapper
SCRIPT_ATTRS["integrity"] = _default_attr_mapper
SCRIPT_ATTRS["nomodule"] = _bool_attr_mapper

# Generates an interpolatable string of valid attrs eg - '{nonce}{id}...'
ATTR_FORMAT_STR = "".join([f"{{{a}}}" for a in SCRIPT_ATTRS])


_script_tag_contents_re = re.compile(
    r"""<script        # match the opening script tag
            [\s|\S]*?> # minimally match attrs and spaces in opening script tag
    ([\s|\S]+)         # greedily capture the script tag contents
    </script>          # match the closing script tag
""",
    re.VERBOSE,
)


def _unwrap_script(text):
    """Extract content defined between script tags"""
    matches = re.search(_script_tag_contents_re, text)
    if matches and len(matches.groups()):
        return matches.group(1).strip()

    return text


def build_script_tag(content=None, **kwargs):
    data = {}
    # Iterate all possible script attrs instead of kwargs to make
    # interpolation as easy as possible below
    for attr_name, mapper in SCRIPT_ATTRS.items():
        data[attr_name] = mapper(attr_name, kwargs.get(attr_name))

    # Don't render block contents if the script has a 'src' attribute
    c = _unwrap_script(content) if content and not kwargs.get("src") else ""
    attrs = ATTR_FORMAT_STR.format(**data).rstrip()
    return f"<script{attrs}>{c}</script>".strip()
