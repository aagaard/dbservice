#!/bin/bash

if [ -z "$VIRTUAL_ENV" ]
then
    echo 'virtualenv not active' >&2
    exit 127
fi

cd `dirname $0`

# drop/recreate local database
dropdb dbservice

########### USING CURRENT MIGRATIONS ######
./manage.py migrate

# create superuser
echo ./manage.py createsuperuser
./manage.py createsuperuser
