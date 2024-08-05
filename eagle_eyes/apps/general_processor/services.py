from eagle_eyes.apps.campaigns.models import Action, Event
from django.utils.dateparse import parse_datetime
from dataclasses import dataclass


@dataclass
class GeneralEvent:
    event: Event
    ad_id: str


class GeneralProcessorService:

    @staticmethod
    def parse_event(message):
        event_date = parse_datetime(message.value.get('date_time'))
        vertical_name = message.value.get('vertical')
        action_title = message.value.get('action')
        params = message.value.get('params')
        user_id = message.value.get('user_id')
        ad_id = message.value.get('ad_id')

        action = Action.objects.get(title=action_title, vertical__name=vertical_name)

        event = Event(
            user=user_id,
            action=action,
            params=params,
            date_time=event_date
        )

        general_event = GeneralEvent(event=event, ad_id=ad_id)
        return general_event
