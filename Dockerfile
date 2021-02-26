FROM python:3.6-alpine

WORKDIR /usr/src/app

COPY ./app ./
COPY ./Pipfile ./Pipfile
COPY ./Pipfile.lock ./Pipfile.lock

RUN if [ ! -d 'media' ]; then mkdir media; fi
RUN if [ ! -d '/var/backups' ]; then mkdir /var/backups; fi
RUN apk --update --no-cache add build-base openldap-dev python2-dev python3-dev mariadb-dev mariadb-client
RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

CMD [ "gunicorn", "contabil.wsgi", "-b", "0.0.0.0:8008" ]
