from django import template
from django.template.base import token_kwargs

from csp.utils import build_script_tag

register = template.Library()


def _unquote(s):
    """Helper func that strips single and double quotes from inside strings"""
    return s.replace('"', "").replace("'", "")


@register.tag(name="script")
def script(parser, token):
    # Parse out any keyword args
    token_args = token.split_contents()
    kwargs = token_kwargs(token_args[1:], parser)

    nodelist = parser.parse(("endscript",))
    parser.delete_first_token()

    return NonceScriptNode(nodelist, **kwargs)


class NonceScriptNode(template.Node):
    def __init__(self, nodelist, **kwargs):
        self.nodelist = nodelist
        self.script_attrs = {}
        for k, v in kwargs.items():
            self.script_attrs[k] = self._get_token_value(v)

    def _get_token_value(self, t):
        return _unquote(t.token) if getattr(t, "token", None) else None

    def render(self, context):
        output = self.nodelist.render(context).strip()
        request = context.get("request")
        nonce = request.csp_nonce if hasattr(request, "csp_nonce") else ""
        self.script_attrs.update({"nonce": nonce, "content": output})

        return build_script_tag(**self.script_attrs)
