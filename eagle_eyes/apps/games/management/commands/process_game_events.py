import json
import logging
from datetime import timedelta
from typing import Tuple

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from kafka import KafkaConsumer

from eagle_eyes.apps.campaigns.models import Event
from eagle_eyes.apps.campaigns.services import parse_event
from eagle_eyes.settings import (
    EVENT_PROCESSOR_BATCH_SIZE,
    EVENT_PROCESSOR_BATCH_TIMEOUT_SECONDS,
    KAFKA_BOOTSTRAP_SERVERS, KAFKA_EVENT_TOPIC
)
from eagle_eyes.settings.project import KAFKA_GAME_EVENT_CONSUMER_GROUP
from eagle_eyes.apps.games.models import UserState
from prometheus_client import start_http_server
from eagle_eyes.apps.games import services


def update_game_state(game_state: dict, game_id: int) -> dict:
    if not game_state:
        level_total_plays = services.get_level_total_plays(current_level=0)
        state = {
            "id": game_id,
            "label": services.get_label(current_level=0),
            "level": 0,
            "played": 1,
            "remaining": level_total_plays - 1,
            "progress": 1 / level_total_plays
        }
    else:
        level = game_state.get("level")
        level_total_plays = services.get_level_total_plays(current_level=level)
        played = game_state.get("played") + 1
        if played == level_total_plays:
            level = level + 1
            level_total_plays = services.get_level_total_plays(current_level=level)
            played = 0
        state = {
            "id": game_id,
            "label": services.get_label(current_level=level),
            "level": level,
            "played": played,
            "remaining": level_total_plays - played,
            "progress": played / level_total_plays
        }
    return state


def update_user_state(user_state: UserState) -> Tuple[str, int, int]:
    played = user_state.played + 1
    level = 0
    for _, game_state in user_state.game_states.items():
        level += game_state.get("level")
    label = services.get_label(current_level=level)
    return label, level, played


def process_game_event(event: Event):

    # events backward compatibility (or just ignore it!)
    if len(str(event.user)) != 36:
        return

    user_state, _ = UserState.objects.get_or_create(user_id=event.user)

    if event.action.title != "play_game":
        return

    try:
        game_id = int(event.params.get("game_id"))
    except Exception:
        logging.warning(f"Ignored game event because of invalid game_id: {event.params.get('game_id')}")
        return
    game_state = user_state.game_states.get(f"{game_id}")

    # Update game state
    user_state.game_states[f"{game_id}"] = update_game_state(game_state, game_id)
    # Update global state
    user_state.label, user_state.level, user_state.played = update_user_state(user_state)

    user_state.save()


class Command(BaseCommand):
    help = 'Starts the game events processor'

    def handle(self, *args, **kwargs):
        # Start a web server to expose prometheus metrics
        start_http_server(8001)

        consumer = KafkaConsumer(
            KAFKA_EVENT_TOPIC,
            group_id=KAFKA_GAME_EVENT_CONSUMER_GROUP,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            enable_auto_commit=False
        )

        events = []
        batch_size = int(EVENT_PROCESSOR_BATCH_SIZE)
        batch_timeout = timedelta(seconds=int(EVENT_PROCESSOR_BATCH_TIMEOUT_SECONDS))
        start_time = timezone.now()

        while True:
            msg_pack = consumer.poll(update_offsets=False)

            new_events = [parse_event(item) for _, records in msg_pack.items() for item in records]
            new_events = [event.event_obj for event in new_events if event.vertical_name == 'game']
            events.extend(new_events)

            if len(events) < batch_size and timezone.now() - start_time < batch_timeout:
                continue
            logging.info(f"Started processing event batch of size {len(events)}")
            if len(events) == 0:
                start_time = timezone.now()
                consumer.commit()
                continue
            with transaction.atomic():
                # Process events to update user state in games
                for event in events:
                    process_game_event(event=event)
                # Reset batch state
                events.clear()
                start_time = timezone.now()
                # Commit the consumer offset
                consumer.commit()

            logging.info("Done!")
