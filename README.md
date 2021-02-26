## ABOUT

AFinCo (Assistente Financeiro-Contábil), means "Financial-Accounting Assistant".

It was developed to act as a bridge between the cashier and the accountant, assisting both in their jobs.

This app intends to solve some specific needs from the [Property Registry Office of First District of Anápolis/GO, Brazil](https://ri1anapolis.com.br), and it has some integrations with the Escriba Register software, so, this app has a really specific and small scope and may be not useful to many people.

We intend - maybe - to make this a lot more generic to be useful to more people, but we haven't a roadmap to achieve that.

Note: Initially AFINCO was named as `contabil` and because of that there are several references to this name in the code.

## NEW INSTALLS

1. Clone the repo and create the env folder and files:

   ```bash
   git clone https://github.com/ri1anapolis/AFINCO
   cd AFINCO
   touch env/development.env env/production.env
   ```

2. Add the following content to each env file:

   `production.env` and `development.env`

   ```env
   SENTRY_SERVER_NAME=MyServerHostname
   SECRET_KEY=5oM3-N1c&_@nD-L0ng-h45h
   DJANGO_ENVIRONMENT=development
   DJANGO_SECRET_KEY=myAwesomeSecretKey
   DJANGO_LOG_LEVEL=WARN
   AFINCO_LOG_LEVEL=INFO
   AUTH_LDAP_SERVER_URI=ldap://ldapServerIpOrHostname
   AUTH_LDAP_BIND_DN=cn=djangoLdapUserName,cn=Users,dc=myDomain,dc=local
   AUTH_LDAP_BIND_PASSWORD=ldapUserPassword
   AUTH_LDAP_USER_SEARCH_OU=cn=Users,dc=myDomain,dc=local
   MYSQL_DATABASE=afincoDb
   MYSQL_USER=afincoDbUser
   MYSQL_PASSWORD=afincoDbUserPassword
   MYSQL_ROOT_PASSWORD=afincoDbRootPassword
   MYSQL_HOST=dockerDbContainerName
   MYSQL_PORT=dockerDbContainerPort
   REGISTER_HOST=escribaRegisterDbServerHostname
   REGISTER_PORT=escribaRegisterDbPort
   REGISTER_DB=escribaRegisterDb
   REGISTER_USER=escribaRegisterDbUser
   REGISTER_PASSWORD=escribaRegisterDbUserPassword
   ```

   Keep the `MYSQL_HOST=db` and `MYSQL_PORT=3306`, because this values are already saved in the docker-compose files. If you need to change them, change them in the docker-compose files too!

   For non production environments, remove the `MYSQL_...` entries to use SQLite as the database backend.

   Control the logging experience by setting `DJANGO_LOG_LEVEL` to manage the Django logging level and `AFINCO_LOG_LEVEL` to manage the application specifics logging information.

3. Try to initialize the database:

   ```bash
   docker-compose -f docker-compose.yml up db
   ```

   When it finishes to initialize, close the this service and follow next steps.

4. Build the local AFINCO image:

   ```bash
   docker-compose -f docker-compose.yml build
   ```

5. Run the stack:

   ```bash
   docker-compose -f docker-compose.yml up
   ```

6. Test the server response in your browser:

   ```http
   http://my.server:8008
   ```

7. With the server running, create the Afinco super user:
   ```bash
   docker-compose -f docker-compose.yml exec django python manage.py createsuperuser
   ```

### Note:

Omit the `-f docker-compose.yml` part of the command to run it in development environment!

Also in the dev env, it'll require the following commands between steps 6 and 7:

```bash
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py collectstatic --noinput
docker-compose exec django python manage.py compress --force
docker-compose exec django python manage.py sync_roles --reset_user_permissions
```

## UPDATE

We think the most secure way to upgrade AFINCO is running a new instance! We think the better way to do it is cloning the new version to a new folder and do a docker volume backup to a new docker volume

1. Create a docker volume backup from the current version:

   In this step we need to mount the current docker volume and a target folder to a docker image. This [docker doc](https://docs.docker.com/storage/volumes/#backup-a-container) may help you.

   Check the docker volume name in the docker-compose file and choose or create a new folder to save the resulting backup.

   ```bash
   docker run --rm -v contabil_db_storage:/from -v ./backups:/to ubuntu bash -c "cd /from && tar -cvf /to/backup.tar ."
   ```

   Check if tar file exists in the target folder and if it has valid data.

2. Create a new folder to the new AFINCO version:

   ```bash
   mkdir AFINCO_NEW && cd AFINCO_NEW
   git clone https://github.com/ri1anapolis/AFINCO .
   ```

   Remember to copy the env files to this new folder.

3. Create a new docker volume and restore the backup:

   Please note that the docker-compose command will auto generate a new volume if the given volume name couldn't be found. Also note tha it'll look for a volume prefixed with the folder name, so, if the folder name is `contabil` and the given volume name in the `docker-compose.yml` file is `db_storage`, the name of the resulting docker volume should be `contabil_db_storage`!

   Also make sure the backup is accessible to the new location.

   ```bash
   docker volume create contabil_db_storage_new
   docker run --rm -v /path/to/backup/folder:/from -v contabil_db_storage_new:/to ubuntu -c "cd /to && tar -xvf /from/backup.tar --strip 1"
   ```

   Remember to modify the `docker-compose.yml` file to set the new volume name.

   ```bash
   sed -i 's/db_storage/db_storage_new/g' docker-compose.yml
   ```

4. Run the new AFINCO version:

   If everything is fine, the new AFINCO version should go up and run with no problems.

   ```bash
   docker-compose -f docker-compose.yml up
   ```

   **Note**: Make sure the previous version is stopped and deactivated!

Now, the new version is running apart from the previous one, and if anything goes wrong just switch back to the existing stable version.

Once everything is fine, stable and with any problems, just get rid of the old version.

## KNOWN ISSUES

- Access denied to the database

  If theres an existing database being used by the new installation, verify if the password set in the database matches with the password set in the env file.

## ADDITIONAL INFORMATION

- AFINCO comes with two environments: production and development.

  Each environment has dedicated files for environment variables.

- The `docker-compose.yml` is configured to the production environment, however there's a override file that is configured to the development environment.

  Therefore, to run commands to the production environment, call the command with the `-f` argument pointing to the production docker-compose file, as the following:

  ```bash
  docker-compose -f docker-compose.yml some_nice_option
  ```

  If the docker-compose command hasn't the `-f` argument, the command will be targeted to the development environment.
  In fact if the `docker-compose up` command was called, it will run the server in development mode.

## BACKUP AND RESTORE

AFINCO uses [django-dbbackup](https://github.com/django-dbbackup/django-dbbackup) package. See detailed information at the package page.

1. Making backups:

   ```bash
   docker-compose exec django python manage.py dbbackup
   ```

2. Restore the most recent backup:
   ```bash
   docker-compose exec django python manage.py dbrestore
   ```
3. List the available backups:
   ```bash
   docker-compose exec django python manage.py listbackups
   ```

### CONVERT A MYSQL DUMP TO SQLITE3 TO DEVELOPMENT PURPOSES

Sometimes run the application on local machine may be easier and fast than with docker, but to run the app locally you'll need setup a database!
To avoid the need of a MysQL setup use SQLite may be a good option, but to have a full testing/development experience a populated database may be necessary.

To achieve that, use the [mysql2sqlite](https://github.com/dumblob/mysql2sqlite) script to convert a MySQL dump to a SQLite database file.
