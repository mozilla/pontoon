import re
from raygun4py import raygunmsgs


def ignore_exceptions(ignored_exceptions, message):
    if message.get_error().get_classname() in ignored_exceptions:
        return None

    return message


def filter_keys(filtered_keys, object):
    iteration_target = object

    if isinstance(object, raygunmsgs.RaygunMessage):
        iteration_target = object.__dict__

    for key in iter(iteration_target.keys()):
        if isinstance(iteration_target[key], dict):
            iteration_target[key] = filter_keys(filtered_keys, iteration_target[key])
        else:
            for filter_key in filtered_keys:
                if key in filtered_keys:
                    iteration_target[key] = '<filtered>'
                elif '*' in filter_key:
                    sanitised_key = filter_key.replace('*', '')

                    if sanitised_key in key:
                        iteration_target[key] = '<filtered>'


    return iteration_target


def execute_grouping_key(grouping_key_callback, message):
    if grouping_key_callback is not None:
        grouping_key = grouping_key_callback(message)

        if grouping_key is not None and isinstance(grouping_key, str) and 0 < len(grouping_key) <= 100:
            return grouping_key

    return None


def camelcase_to_snakecase(key):
    "Turns camelCaseStrings into snake_case_strings."
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', key)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snakecase_dict(d):
    return dict([
        (camelcase_to_snakecase(k), v) for k, v in d.items()
    ])
