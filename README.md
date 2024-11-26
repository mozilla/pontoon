# Description

Pontoon is a translation management system used and developed by the
[Mozilla localization community](https://pontoon.mozilla.org/). It
specializes in open source localization that is driven by the community and
uses version control systems for storing translations.

It specializes in open source localization that is driven by the community and uses version-control systems for storing translations.

# Docs

- [Pontoon User Doc](https://docs.google.com/document/d/1PIr68vmqWcSi9SRGsYDwKy4VaLRq9wek9d9DnAerma8)
- [Pontoon Admin Doc](https://docs.google.com/document/d/12enkYKPpQZFIpvPaWIVMlol0crWmjhgJ7e4xNt_RAvI)

# Local development

Prerequisits:

- pyenv
- nvm

1. Set up local Git repo

```sh
git clone https://github.com/scantrust/pontoon
cd pontoon

# Add the Mozilla Pontoon git repo as remote: upstream
git remote add upstream https://github.com/mozilla/pontoon
```

2. Install dependencies

```sh
pyenv install `pyenv local`
nvm install v18 --lts

python -m venv venv
pip install -r requirements/default.txt
pip install -r requirements/dev.txt
```

3. Start up a postgres database container

```sh
docker-compose up -d postgresql
```

And then execute below SQL command on the new database

```sql
-- meant to be executed on the mandatory postgress database "postgres"
CREATE DATABASE pontoon;

-- meant to be executed on the mandatory postgress database "postgres"
CREATE USER "pontoon" WITH PASSWORD "asdf";
CREATE ROLE "pontoon-all";
GRANT "pontoon-all" TO "pontoon";

-- meant to be executed on the postgress database "pontoon"
DO $$
DECLARE
    tables CURSOR FOR
        SELECT tablename
        FROM pg_tables
        WHERE tablename NOT LIKE 'pg_%' AND tablename NOT LIKE 'sql_%'
        ORDER BY tablename;
BEGIN
    FOR table_record IN tables LOOP
	EXECUTE format('ALTER TABLE %s OWNER TO "pontoon-all"',   table_record.tablename);
        -- RAISE NOTICE 'Tablename: %', table_record.tablename;
    END LOOP;
END$$;
```

4. Create env file

```sh
# Add real value to below vrabiles
KEYCLOAK_CLIENT_ID=""
KEYCLOAK_CLIENT_SECRET=""
GOOGLE_TRANSLATE_API_KEY=""
SSH_KEY=""

cat >> .env <<EOF
# Env Vars
SECRET_KEY=random_key
DJANGO_DEV=True
DJANGO_DEBUG=True
CI=False
DATABASE_URL=postgres://pontoon:asdf@localhost:5555/pontoon
ENABLE_INSIGHTS_TAB=True
SESSION_COOKIE_SECURE=False
SITE_URL=http://localhost:8000
ALLOWED_HOSTS="localhost,127.0.0.1,0.0.0.0,pontoon.scantrust.io,192.168.0.0/16"

AUTHENTICATION_METHOD=keycloak

# Keycloak Authentication
KEYCLOAK_URL=https://keycloak.scantrust.io
KEYCLOAK_REALM=Pontoon
KEYCLOAK_CLIENT_ID=${KEYCLOAK_CLIENT_ID}
KEYCLOAK_CLIENT_SECRET=${KEYCLOAK_CLIENT_SECRET}

GOOGLE_TRANSLATE_API_KEY=${GOOGLE_TRANSLATE_API_KEY}

SSH_KEY="${SSH_KEY}"
KNOWN_HOSTS="
|1|1INgyaCPxmwTuu8P1DTvy6zp3N0=|4Yu0ELWteoeZS5D9Z2SbyAIrLFE= ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEmKSENjQEezOmxkZMy7opKgwFB9nkt5YRrYMjNuG5N87uRgg6CLrbo5wAdT/y6v0mKV0U2w0WZ2YB/++Tpockg=
|1|DSlVMBhVZ5hDQVIMeS0IbQ6jl/Y=|hlAmJsXzR4hOJbKGS2nTT+NA6Us= ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEmKSENjQEezOmxkZMy7opKgwFB9nkt5YRrYMjNuG5N87uRgg6CLrbo5wAdT/y6v0mKV0U2w0WZ2YB/++Tpockg=
|1|YoQH0KUOlpSBALw3KTNem3ptCdw=|DCD0carpoEY34sdwSk4wm+ALfXA= ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEmKSENjQEezOmxkZMy7opKgwFB9nkt5YRrYMjNuG5N87uRgg6CLrbo5wAdT/y6v0mKV0U2w0WZ2YB/++Tpockg=
"
GIT_CONFIG="
[user]
	name = pontoon.scantrust.io
[url \"git@github.com:\"]
	insteadOf = git://github.com/
[url \"git@github.com:\"]
	insteadOf = https://github.com/
"
```

5. Run server locally

```sh
source venv/bin/activate
# Add Keycloak as auth provider
python manage.py update_auth_providers
python manage.py runserver
```

6. Update from the upstream repo - mozilla/pontoon

```sh
git fetch upstream
git rebase -i upstream/main
# After resolve the conflicts (if there is any), pick the commits in the rebase todo list, then
# force push to the origin (force push permission required).
git push -f origin master
# Now you can branch out from here, add changes, commits, and open PR
```

7. Build the image

Run below command in terminal

```sh
# bump the current version
bumpversion patch

# build the image
nvm use v18 && \
    make build-translate && \
    docker build -f ./docker/Dockerfile --build-arg USER_ID=1000 --build-arg GROUP_ID=1000 \
        -t 715161504141.dkr.ecr.eu-west-1.amazonaws.com/pontoon:$(make version) .
```

8. Push the image to AWS ECR

```sh
# Login to AWS ECR
aws ecr get-login-password | docker login -u AWS --password-stdin \
  715161504141.dkr.ecr.eu-west-1.amazonaws.com

# Push the image
docker push 715161504141.dkr.ecr.eu-west-1.amazonaws.com/pontoon:$(make version)
```

# Todos

- [✓] Create Postgres database statefulset in the namespace `apps`
- [✓] Create Docker image of Pontoon and upload to ECR
- [✓] Deploy Pontoon service
- [✓] Integrate Google authentication
- [✓] Create a example project
- [✓] Setup a dedicated Git account for Pontoon's Git Sync (generate a Git
  access token and update pontoon-secret)
- [✓] Solve SSH_KEY not working problem
- [✓] Hide the duplicated localized files in the pontoon projects
- [✓] Migrate backend-api from Transifex to Pontoon
- [✓] Migrate Android STE and IOS STE translations and showcase the workflow to
  the project managers
- [✓] Replace Google Oauth with the production one
- [✓] ~~To download project configuration files, Pontoon requires a http request
  URL. Currently it’s set up to download the raw file from the github private
  repo with a personal access token. It might be worth considering putting the
  config files to S3.~~ Going with hosting configuration files in S3 bucket
  `dl.scantrust.com`.
- [ ] There is an option to download the translation files in the translating
      page of the file. It’s returning 404.
- [✓] ~~Pontoon private projects are not visible to default users, translators
  nor even team managers . Public projects are public to non-login users. So
  it’s probably not a good way.~~ Going with assigning users superuser role in
  Pontoon.
- [✓] Set up Google Translation suggestion in the translating page
- [✓] Hold a knowledge transfer meeting for the translators
- [ ] Requesting a new Team (locale) in a project or a new project in a Team
      (locale) is not working. Need to set up an SMTP account.
- [✓] Add per-project permissions for users
- [✓] Integrate Keycloak auth
- [✓] Fix unauthorized page showing Django debug page instead of login page.
- [✓] Add project action for exporting project translations
- [ ] Correlate Keycloak user groups with user groups in Pontoon
- [✓] Export/import translations in project page
- [✓] Add versioning using bumpversion

# References

- [📚 **Documentation**](https://mozilla-pontoon.readthedocs.io/)
- [Developer Setup using Docker](https://mozilla-pontoon.readthedocs.io/en/latest/dev/setup.html).
