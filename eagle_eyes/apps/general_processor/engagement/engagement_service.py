from eagle_eyes.apps.general_processor.models import Tracker, EngagementState
from eagle_eyes.apps.general_processor.services import GeneralEvent
from django.utils import timezone
import os
import requests
from eagle_eyes.apps.general_processor.engagement.configs import (
    ADTRACE_AUTHORIZATION,
    ZAREBIN_APP_TOKEN,
    ENGAGEMENT_EVENT_TOKEN,
    ADTRACE_URL,
)
from eagle_eyes.apps.general_processor.engagement.logger import log_api_call
from eagle_eyes.apps.general_processor.engagement.metrics import adtrace_requests


class ProcessingService:
    @staticmethod
    def process_event(general_event: GeneralEvent):
        event = general_event.event
        ad_id = general_event.ad_id

        trackers = Tracker.objects.filter(
            start_date__lte=event.date_time, end_date__gte=event.date_time
        ).cache()
        user_id = event.user

        for tracker in trackers:
            criterias = tracker.engagement_criterias.all().cache()
            criterias = [
                criteria
                for criteria in criterias
                if criteria.action == event.action
                or criteria.action in event.action.parent_actions.all()
            ]
            if not criterias:
                continue

            user_state = StateService.get_or_create_state(tracker, user_id)
            if user_state.done:
                if not user_state.sent:
                    StateService.update_send_state(user_state, ad_id)
                continue

            for criteria in criterias:
                id = f"{criteria.id}"
                if user_state.state[id]["done"]:
                    continue
                user_state.state[id]["user_value"] += 1
                user_state.state[id]["done"] = (
                    user_state.state[id]["user_value"]
                    >= user_state.state[id]["criteria_value"]
                )

            if all(
                criteria_state["done"] for _, criteria_state in user_state.state.items()
            ):
                user_state.done = True
                user_state.finished = timezone.now()
                user_state.duration = user_state.finished - user_state.started
                StateService.update_send_state(user_state, ad_id)
            user_state.save()


class StateService:
    @staticmethod
    def get_or_create_state(tracker, user_id):
        engagement_state, _ = EngagementState.objects.get_or_create(
            tracker=tracker,
            user_id=user_id,
            defaults={
                "started": timezone.now(),
                "done": False,
                "state": StateService.generate_state_template(tracker),
            },
        )
        return engagement_state

    @staticmethod
    def generate_state_template(tracker):
        criterias = tracker.engagement_criterias.all()
        state = {
            f"{criteria.id}": {
                "user_value": 0,
                "criteria_value": criteria.value,
                "done": False,
                "sent": False,
            }
            for criteria in criterias
        }
        return state

    @staticmethod
    def send_engagement_event(ad_id):
        headers = {"Authorization": ADTRACE_AUTHORIZATION}
        data = {
            "app_token": ZAREBIN_APP_TOKEN,
            "os_name": "android",
            "event_token": ENGAGEMENT_EVENT_TOKEN,
            "gps_adid": ad_id,
        }
        proxy = os.getenv("BEHSA_PROXY")
        proxies = {"https": proxy, "http": proxy}
        url = ADTRACE_URL
        resp = requests.post(url, json=data, headers=headers, proxies=proxies)
        log_api_call('adtrace', resp)
        adtrace_requests.labels(resp.status_code).inc()
        return resp

    @staticmethod
    def update_send_state(engagement_state, ad_id):
        resp = StateService.send_engagement_event(ad_id)
        if resp.status_code == 200:
            engagement_state.sent = True
            engagement_state.save()
        return resp
