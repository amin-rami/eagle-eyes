from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from kafka import KafkaConsumer
import json
from datetime import timedelta

from prometheus_client import start_http_server
from eagle_eyes.apps.general_processor.engagement.engagement_service import ProcessingService
from eagle_eyes.apps.general_processor.services import GeneralProcessorService
from eagle_eyes.apps.general_processor.engagement.configs import (
    KAFKA_EVENT_TOPIC,
    KAFKA_ENGAGEMENT_CONSUMER_GROUP,
    KAFKA_BOOTSTRAP_SERVERS,
    ENGAGEMENT_PROCESSOR_BATCH_SIZE,
    ENGAGEMENT_PROCESSOR_BATCH_TIMEOUT_SECONDS,
)
from eagle_eyes.apps.club.processing import process_club_event


class Command(BaseCommand):
    def handle(self, *args, **options):
        start_http_server(9100)
        consumer = KafkaConsumer(
            KAFKA_EVENT_TOPIC,
            group_id=KAFKA_ENGAGEMENT_CONSUMER_GROUP,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            enable_auto_commit=False,
        )

        events = []
        batch_size = int(ENGAGEMENT_PROCESSOR_BATCH_SIZE)
        batch_timeout = timedelta(
            seconds=int(ENGAGEMENT_PROCESSOR_BATCH_TIMEOUT_SECONDS)
        )
        start_time = timezone.now()

        while True:
            msg_pack = consumer.poll()
            events.extend(
                [
                    GeneralProcessorService.parse_event(item)
                    for _, records in msg_pack.items()
                    for item in records
                ]
            )
            if len(events) < batch_size and timezone.now() - start_time < batch_timeout:
                continue
            if len(events) == 0:
                start_time = timezone.now()
                continue
            with transaction.atomic():
                for event in events:
                    ProcessingService.process_event(event)
                    process_club_event(event.event)

                events.clear()
                start_time = timezone.now()

                consumer.commit()
