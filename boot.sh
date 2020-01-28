#!/bin/sh
# BOOTS A DOCKER CONTAINER
. env/bin/activate
while true; do
    flask db upgrade
    RESULT="$?"
    if [ $RESULT -eq "0" ]; then
        break
    fi
    echo DB upgrade command failed, retrying in 5 secs...
    sleep 5
    done


exec gunicorn -b :5000 --access-logfile - --error-logfile - minitwitter:app