#!/bin/sh

python manage.py migrate
python manage.py start_general_processor
