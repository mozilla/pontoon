# Pontoon

##### (Guide for building and deploying pontoon in a dev environment)

### Build the container under windows:

###### get code and prepare the build

- git checkout: C:\Projekte\pontoon\latest: https://github.com/mozilla/pontoon.git
- three files need to be replaced by those in this folder

###### build

- open a powershell in checkout folder and switch to wsl using the `wsl` command
- in WSL: connect windows local docker: `export DOCKER_HOST="tcp://localhost:2375"`
- run the build: `make build`

### The database setup:

For a first time setup we recommend starting the container, or at least the database migration script (python manage.py migrate) with a higher privilege user such as the "postgres" superuser. Then for all consecutive runs use the dedicated pontoon user which creation is described below.

- create a dedicated database

```
-- meant to be executed on the mandatory postgress database "postgres"
CREATE DATABASE pontoon;
```

- create a poonton database user and roll. Assign the user to its roll

```
-- meant to be executed on the mandatory postgress database "postgres"
CREATE USER "pontoon" WITH PASSWORD "h29xlKIN4nrTGyFLsKf1";
CREATE ROLE "pontoon-all";
GRANT "pontoon-all" TO "pontoon";
```

- additionally: add the database "postgres" superuser to this roll so he can see the tables easily in SQL-Clients such as pgAdmin.

```
-- meant to be executed on the mandatory postgress database "postgres"
GRANT "pontoon-all" TO "postgres";
```

- in case the "postgres" superuser or another higher privilege user was used to initially execute the migration script as mentioned above make sure to change the owner of each table within the poonton database:

```
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

### The container:

###### Test the container locally and init the database

- tag the container for easier usage:
- for testing run the container like this:
  ```
  docker run -d -p 8000:8000 -p 3000:3000 -e DJANGO_LOGIN=true -e DJANGO_DEBUG=false -e DJANGO_DEV=false -e ALLOWED_HOSTS=127.0.0.1 -e CI=true -e DATABASE_URL=postgres://<postgres-user>:<password>@<db-ip-or-hostname>:5432/<pontoon-db-name> -e SECRET_KEY=a3cafccbafe39db54f2723f8a6f804c34753679a0f197b5b33050d784129d570 -e SITE_URL=http://127.0.0.1:8000 --name pontoon corp/imagename:pontoon-prod-31.01.20
  ```
  The SSH_KEY and KNOWN_HOSTS environment variables are both base64 encoded, but may be omitted here and set/created manually (without base64 encoding) inside the running container. But for the prod environment they need to be passed to guarantee unattended deployment.
  If the environment variable SYNC_INTERVAL is defined a shell script will call sync_projects using this interval in minutes.
- get a bash into the container: `docker exec -it pontoon bash`
  useful commands:

  - check open ports (8000 and 3000 should be open): `ss -lntu`
  - check running processes: `ps -A`
  - show simple startup log of run_webapp.sh: `cat /app/run_webapp.log`

  ##### first time only, with newly created database:

  create an admin user: `python ./manage.py createsuperuser --user=<username> --email=<yourEmail@address>`

  ##### for each project:

  - create project using the web ui, see: https://mozilla-l10n.github.io/documentation/tools/pontoon/adding_new_project.html

- further **administration** via Django: http://127.0.0.1:8000/__a/__

#### NOTES:

- don't try to run pontoon in a subfolder domain, like apigee does. (e.g. https://mydomain.com/pontoon/). It seems only to support running on domain level: **https://mydomain.com/~~pontoon/~~**
  you may use subdomains --> https://pontoon.mydomain.com/

### deployment on k8s:

For a k8s deplyoment example yaml see the k8s-pontoon-example.yaml in this folder

#### TODO:

- "_Pontoon sends email when users request projects to be enabled for teams, or teams to be added to projects_" 
  **e-mails are not yet tested in the image**

---

### Useful commands

- for git access you need to create the _SSH_KEY_: `ssh-keygen -t rsa -b 4096 -C "<yourEmail@address>"`
  - find the public key to be entered in guthub: `cat /root/.ssh/id_rsa.pub`
  - the private key to be base64 encoded as _SSH_KEY_: `cat /root/.ssh/id_rsa`
- after the first git sync you also geht the _known_hosts_ file:
  - to be base64 encoded as _KNOWN_HOSTS_: `cat /root/.ssh/known_hosts`

* first manually sync a single project by reading locales from git source code only: `python manage.py sync_projects --projects=<projectname> --no-commit`
* syncing all projects with writing changes to the soruce code `python manage.py sync_projects`.
  This is done by shell script every 30 minutes (evn var SYNC_INTERVAL)
* to see if the sync works look at: http://127.0.0.1:8000/__sync/log/__

