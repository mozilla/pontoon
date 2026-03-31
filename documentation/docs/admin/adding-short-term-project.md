# Adding a New Short-Term Project

Short-term projects are things like newsletters, marketing campaigns, surveys… They do not have a repository, and data is instead stored only in Pontoon’s database.

The process to create a short-term project is very similar to that of a regular one.

## Create the project in Pontoon STAGE instance

First you want to test that everything works using Pontoon staging server.

Access Pontoon’s [admin console](https://pontoon.allizom.org/admin/) on the **stage server** and click **ADD NEW PROJECT**.

* Name: name of the project (it will be displayed in Pontoon’s project selector).
* Slug: used in URLs, will be generated automatically based on the repository’s name.
* Locales:

  * Select at least one locale. To make things faster it’s possible to copy supported locales from an existing project.
  * You can uncheck the `Locales can opt-in` checkbox to prevent localizers from requesting this specific project.

* Data Source: select `Database` in the list of options. This will hide the *Repositories* section and show a *Strings* section instead.
* Strings: you can enter the initial set of strings here. Strings must be separated by new lines. If you leave this empty, you’ll be able to enter strings as a batch again after creating the project. Strings must be in `en-US`, and they will become the entities on that project. A resource named `database` will automatically be created.
* For every other option, please refer to the [new project documentation](adding-new-project.md).

Click **SAVE PROJECT** at the bottom of the page, and you’re done!

## Create the project in Pontoon PROD instance

At this point you need to repeat the same steps on the **production server**.

Access Pontoon’s [admin console](https://pontoon.mozilla.org/admin/), add the same information you used on the staging server and make sure to select all supported locales for this project.

The new project will immediately appear in the [public list of Projects](https://pontoon.mozilla.org/projects/).

## Managing strings

After you have created your project, you will be able to manage its source strings. On the admin project page (that you can find from the [admin console](https://pontoon.mozilla.org/admin/)), under the *Strings* section, you will find two links. The one called **MANAGE STRINGS** will lead you to a page where all strings are listed. There you can edit the string content, edit the string comment, add new strings (use the **NEW STRING** button) or remove existing strings (use the trashbin icon under the comment input). Once you’re done editing, click the **SAVE STRINGS** button to save your changes.

## Downloading translations

On the project’s admin page and on the Manage Strings page, you’ll find a **DOWNLOAD STRINGS** link. Clicking it will download a CSV file that contains all the translations in all enabled locales. The file format looks as follow:

```CSV
Source, fr, de
Hello, Salut, Hallo
World, Monde, Welt
```
