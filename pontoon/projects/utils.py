def filter_users_by_project_visibility(project, users):
    """Return users that can view/access the project."""
    if project.visibility == "public":
        return users
    return users.filter(is_superuser=True)
