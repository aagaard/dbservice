#!/bin/bash

if [ -z "$VIRTUAL_ENV" ]
then
    echo "ERROR: virtualenv not active"
    exit -1
fi

cd $(dirname $0)

if [ -z "$1" ]
then
    echo "Usage: $0 APP_NAME [...]"
    exit -1
else
    # named/argument models
    ./manage.py graph_models -e -g -o docs/models.pdf "$@"
fi
