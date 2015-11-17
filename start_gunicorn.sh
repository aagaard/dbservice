#!/bin/bash

cd `dirname $0`

. ~/.virtualenvs/dbservice/bin/activate

GUNICORN_IPV4_ADDRESS=127.0.0.1:8001
GUNICORN_IPV6_ADDRESS=[::1]:8001
TIMEOUT=120

# number of processor cores + 1
WORKER_THREADS=$(($(grep -c '^processor' /proc/cpuinfo) + 1))

PIDFILE=gunicorn.pid

if [ -f $PIDFILE ]
then
    kill -TERM $(cat $PIDFILE)
    rm $PIDFILE
fi

DJANGO_SETTINGS_MODULE=dbservice.settings.dev \
gunicorn \
--backlog=2048 \
--timeout=120 \
--graceful-timeout=120 \
--pid=$PIDFILE \
--bind=$GUNICORN_IPV4_ADDRESS \
--bind=$GUNICORN_IPV6_ADDRESS \
--daemon \
--log-level=debug \
--log-syslog \
--worker-class=gaiohttp \
dbservice.wsgi:application

# You may gracefully reload the application with
# kill -HUP $(cat gunicorn.pid)
# and stop gunicorn with
# kill -TERM $(cat gunicorn.pid)
# (for convenience, a stop_gunicorn.sh script is provided...)
