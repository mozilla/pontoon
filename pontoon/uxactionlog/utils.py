from pontoon.uxactionlog.models import UXActionLog


def log_ux_action(action_type, experiment=None, data={}):
    """Save a new UX action in the database.

    :arg string action_type: The type of action that was performed.
    :arg string experiment: The name of the experiment as part of which the action has been made.
    :arg json data: Additional action-specific data in JSON serializable structure.

    :returns: None
    """
    action = UXActionLog(action_type=action_type, experiment=experiment, data=data)
    action.save()
