from jinja2 import Environment


def environment(**options):
    env = Environment(**options)
    return env
