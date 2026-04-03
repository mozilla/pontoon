# Contributing

## Source code

Pontoon source code is available on
[GitHub](https://github.com/mozilla/pontoon).

## Issues

Our work is tracked in
[GitHub](https://github.com/mozilla/pontoon/issues).

[Report a new issue](https://github.com/mozilla/pontoon/issues/new){ .md-button }

## Docker

While the front-end (JavaScript) build and tests use the host
environment for development, the back-end systems (Python/Django,
databases, etc.) run in Docker containers. For production use, also the
front-end is built in a container. Thus Pontoon requires fewer things to
get started and you're guaranteed to have the same server setup as
everyone else.

If you're not familiar with [Docker](https://docs.docker.com/) and
[docker-compose](https://docs.docker.com/compose/overview/), it's worth
reading up on.

## JavaScript setup

For working on the front-end, you need the latest versions of Node.js
and npm ([installation
instructions](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)).
Parts of the front-end use [npm
workspaces](https://docs.npmjs.com/cli/v7/using-npm/workspaces), which
are not supported by earlier npm versions.

## Database

If you have a database dump, you can load it into your PostgreSQL
database.

Make sure you backup your existing database first:

``` shell
$ make dumpdb
```

And then load the dump:

``` shell
$ make loaddb DB_DUMP_FILE=path/to/my/dump
```

Note that your database container needs to be running while you do that.
You can start just the postgresql container by running:

``` shell
$ docker-compose up -d postgresql
```

## Interactive shell

If you need to run specific commands, that are not covered by our
`Makefile`, you can start an interactive
shell inside a Pontoon container:

``` shell
$ make shell
```

`make shell-root` is also available to log
in as `root`, instead of the default
`pontoon` user.

## Browser Support

The list of browsers supported by Pontoon is defined in the
`"browserslist"` entry of the root
package.json, and contains by default:

``` bash
Firefox >= 78
Chrome >= 80
Edge >= 91
Safari >= 13.1
```

## Code style

We use code formatters so that we do not have to fight over code style.
You are free to write code however you like, because in the end the
formatter is the one that will format it. We thus don't need to pay
attention to style during code reviews, and are free from those
never-ending code style discussions.

To format the Python and the JavaScript code at once you can use:

``` shell
$ make format
```

Code formatting is explained in more detail in the following sections.

To run the required linters on the Python and the JavaScript code at
once you can use:

``` shell
$ make lint
```

## Python code conventions

Our Python code is automatically formatted using
[ruff](https://docs.astral.sh/ruff/). We enforce that in our Continuous
Integration, so you will need to run ruff on your code before sending it
for review.

You can run ruff locally either as an [add-on in your code
editor](https://docs.astral.sh/ruff/integrations/#vs-code-official), or
as a [git pre-hook
commit](https://docs.astral.sh/ruff/integrations/#pre-commit).
Alternatively, you can format your code using:

``` shell
$ make ruff
```

In the rare case when you cannot fix an error, use `# noqa` to make the
linter ignore that error (see
[documentation](https://docs.astral.sh/ruff/linter/#error-suppression)).
Note that in most cases, it is better to fix the issues than ignoring
them.

## JavaScript code conventions

Our JavaScript code is automatically formatted using
[Prettier](https://prettier.io/docs/en/index.html). We enforce that in
our Continuous Integration, so you will need to run prettier on your
code before sending it for review.

You can run prettier locally either as an [add-on in your code
editor](https://prettier.io/docs/en/editors.html), or as a [git pre-hook
commit](https://prettier.io/docs/en/precommit.html). Alternatively, you
can format your code using:

``` shell
$ make prettier
```

Additionally, there are linting rules that are defined in our
`eslint.config.mjs` file. To run the linter, do:

``` shell
$ make eslint
```

In the rare case when you cannot fix an eslint error, use
`// eslint-disable` to make the linter ignore that error. Note that in
most cases, it is better to fix the issues than ignore them.

For more specifics about the `translate` folder, look at the README.md
file there.

## Git conventions

The first line is a summary of the commit. It should start with one of
the following:

    Fix #1234

or:

    #1234

The first, when it lands, will cause the issue to be closed. The second
one just adds a cross-reference.

After that, the commit should explain *why* the changes are being made
and any notes that future readers should know for context or be aware
of.

We follow [The seven rules of a great Git commit
message](https://chris.beams.io/posts/git-commit/#seven-rules):

1.  Separate subject from body with a blank line
2.  Limit the subject line to 50 characters
3.  Capitalize the subject line
4.  Do not end the subject line with a period
5.  Use the imperative mood in the subject line
6.  Wrap the body at 72 characters
7.  Use the body to explain what and why vs. how

## Pull requests

Pull request summary should indicate the issue the pull request
addresses.

Pull request descriptions should cover at least some of the following:

1.  What is the issue the pull request is addressing?
2.  Why does this pull request fix the issue?
3.  How should a reviewer review the pull request?
4.  What did you do to test the changes?
5.  Any steps-to-reproduce for the reviewer to use to test the changes

## Code reviews

Pull requests should be reviewed before merging.

Style nits should be covered by linting as much as possible.

Code reviews should review the changes in the context of the rest of the
system.

## Python Dependencies

Direct dependencies for Pontoon are distributed across four files:

1.  `requirements/default.in`: Running Pontoon in production
2.  `requirements/dev.in`: Development
3.  `requirements/test.in`: Testing
4.  `requirements/lint.in`: Linting

In order to pin and hash the direct and indirect dependencies, we use
[uv pip compile](https://docs.astral.sh/uv/#the-pip-interface), which
yields corresponding `*.txt` files. These `*.txt` files contain all
direct and indirect dependencies, and can be used for installation with
`uv pip`. After any change to the `*.in` files, you should run the
following command to update all `requirements/*.txt` files.

``` shell
$ make requirements
```

When adding a new requirement, add it to the appropriate
`requirements/*.in` file. For example, to add the development dependency
`foobar` version 5, add `foobar==5` to `requirements/dev.in`, and then
run the command from above.

Once you are done adding, removing or updating requirements, rebuild
your docker environment:

``` shell
$ make build-server
```

If there are problems, it'll tell you.

To upgrade existing dependencies within the given constraints of the
input files, you can pass options through to the `uv pip compile`
invocations, i.e.

``` shell
$ make requirements opts=--upgrade
```

## Documentation

Documentation for Pontoon is built with [Zensical](https://zensical.org/)
and is available on `http://localhost:8000/docs/`.

To build the docs, run:

``` shell
$ make docs
```

## Running tests

To run the entire test suite, do:

``` shell
$ make test
```

To run only the `translate` tests:

``` shell
$ make test-translate
```

To run only the Python tests:

``` shell
$ make pytest
```

To run specific tests or specify arguments, you'll want to start a shell
in the test container:

``` shell
$ make shell
```

Then you can run tests as you like.

Running all the unittests (make sure you run `./manage.py collectstatic`
first):

``` shell
app@...:/app$ pytest
```

Running a directory of tests:

``` shell
app@...:/app$ pytest pontoon/base/
```

Running a file of tests:

``` shell
app@...:/app$ pytest pontoon/base/tests/test_views.py
```

## Writing tests

Put your tests in the `tests/` directory of the appropriate app in
`pontoon/`.

### Mock usage

[Mock](https://docs.python.org/dev/library/unittest.mock.html) is a
python library for mocks objects. This allows us to write isolated tests
by simulating services besides using the real ones. Best examples are
existing tests which admittedly do mocking different depending on the
context.

Tip! Try to mock in limited context so that individual tests don't
affect other tests. Use context managers instead of monkey patching
imported modules.

## Updating Your Local Instance

When changes are merged into the main Pontoon repository, you'll want to
update your local development instance to reflect the latest version of
the site. You can use Git as normal to pull the latest changes, but if
the changes add any new dependencies or alter the database, you'll want
to install any new libraries and run any new migrations.

If you're unsure what needs to be run, it's safe to just perform all of
these steps, as they don't affect your setup if nothing has changed:

``` shell
# Pull the latest code (assuming you've already checked out main).
git pull origin main

# Install new dependencies or update existing ones.
uv pip install -U --force -r requirements/default.txt

# Run database migrations.
python manage.py migrate
```

## Writing to external repositories from a local instance

[Environment variables](deployment.md#environment-variables) like `SSH_KEY` and
`SSH_CONFIG` have no effect in a Docker setup.

The `~/.ssh` folder of the host system is
mapped automatically to the home folder within the container. In order
to connect to a remote repository via SSH, you need to create a
passwordless SSH key, and configure
`~/.ssh/config` accordingly.

Here's an example for GitHub, assuming the private key file is called
`id_ed25519` (see [GitHub's
instructions](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)
for generating a new key):

```
Host github.com
   User YOUR_USERNAME
   IdentityFile ~/.ssh/id_ed25519
   StrictHostKeyChecking no
```

The project's repository will use the format
`git@github.com:{ORGANIZATION}/{REPOSITORY}.git` for the `URL` field.

An alternative approach for GitHub is to use a [Personal Access Token
(PAT)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens),
and set up the project's `URL` as
`https://` instead of
`git@`. In this case, the `URL` will need
to include both the PAT and username, e.g.
`https://{USER}:{TOKEN}@github.com/{REPOSITORY}`.
