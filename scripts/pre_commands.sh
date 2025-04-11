#!/bin/sh
echo "Pre script running"
python /app/manage.py makemigrations --noinput
python /app/manage.py makemigrations core --noinput
echo "Running database migrations..."
python /app/manage.py migrate --noinput
