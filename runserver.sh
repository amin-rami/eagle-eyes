#!/bin/sh

python manage.py migrate
gunicorn eagle_eyes.wsgi --bind 0.0.0.0:8000
