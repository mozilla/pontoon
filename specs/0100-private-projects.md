- Feature Name: Private Projects
- Created: 2020-02-10
- Associated Bug: https://bugzilla.mozilla.org/show_bug.cgi?id=1602490

# Summary

Add an option to make a project "private", restricting who can see it and interact with it.

# Motivation

It can be useful in some cases to be able to hide a project from users. For example, when a superuser creates a new project, they might want to make sure that everything is correctly set up before exposing it — running sync, verifying that it is enabled for the right locales, etc. In such a case, the project being not visible from non-superusers is enough. Once the superuser is done with configuration, they simply make the project public.

For a different use-case, let's consider an agency working with several clients. They have a number of projects created on Pontoon, and they want to have specific localizers working on specific projects. It would be beneficial for them to be able to restrict seeing a project to only a defined list of users. This requires being able to mark a project as private, and also having a configuration option to select a list of users who will be able to see, and interact, with that project. That would allow a clear separation of projects, reducing the risk of localizers translating the wrong set of projects.

# Feature explanation

When creating or editing a project, a superadmin has two new options:

- a simple selectbox to make the project private or public (private by default);
- a formset controlling which users can see the project when it is private.

The "selected users" formset is visible only when the project is marked as private. It has three elements:

- a list of users, showing who currently has access (or will upon saving). Clicking a user in the list removes that user from the list;
- a search input, used to look for a specific user in the database and adding that user to the list;
- a "copy from project" button, allowing to copy the selected users list from an existing project.

Locale managers and localizers of a project always have access to it, regardless of whether they are in the selected users list or not.

On the administration page of a project that is marked as private, we show a warning that the project is private and must be made public to enable translation by all users.

On each dashboard listing projects (`/projects/`, `/{locale}/`), private projects will not appear unless the user is authenticated and is in the list of selected users. Private projects will not appear on the Permissions tab of the team dashboard (`/{locale}/permissions/`).

Pages related to a project (`/projects/{project}/`, `\{locale}/{project}/`, `/{locale}/{project}/{resource}/`) will return a 404 Not Found error unless the user is authenticated and is in the list of selected users. That should also be the case for back-end endpoints used to modify data, as a user should not be able to interact at all with a private project if they are not selected for that project.

All instances of the "latest activity" feature, throughout the website, should also filter out private projects for which the user is not selected. However, data from private projects doesn't need to be removed from Translation Memory. Those projects would be private but not "secret", so it's fine if data is exposed, as long as only a defined set of people can create and modify that data.

# Roles

| Role | Impact |
| -- | -- |
| Locale Manager | Can see all private projects of locales they are managing |
| Translator | Can see all private projects of locales they are translating |
| Contributor | Cannot access private projects unless they are given explicit permission |

# Drawbacks

This feature risks creating confusion amongst users for Pontoon instances that are usually open to all users (like Mozilla's). It can happen if some users of a local community have access to a project, and others do not. In such instances, private projects should be used only for the sake of configuration, after what they should always be public or marked as obsolete.

# Mockup

![](0100/mockup.png)
