#!/bin/sh

python manage.py migrate
manage.py process_game_events
