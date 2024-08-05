#!/bin/sh

python manage.py migrate
python manage.py process_campaign_events
