#!/bin/bash

cd `dirname $0`

kill -HUP $(cat gunicorn.pid)
