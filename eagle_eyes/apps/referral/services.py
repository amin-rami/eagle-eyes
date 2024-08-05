from django.utils import timezone
from eagle_eyes.apps.campaigns.dependencies import get_streamer
from eagle_eyes.apps.eagleusers.services import UserService


class MutualEventServices():

    @staticmethod
    def send_mutual_event(referral, referrer_event, referee_event):
        referrer_event_data = {
            **referrer_event,
            "date_time": str(timezone.now()),
            "params": {},
        }
        referee_event_data = {
            **referee_event,
            "date_time": str(timezone.now()),
            "params": {},
        }

        referrer_user_id = UserService.user_id(referral.referrer_phone_number)
        referee_user_id = UserService.user_id(referral.referee_phone_number)

        referrer_data = {"user_id": referrer_user_id, **referrer_event_data}
        referee_data = {"user_id": referee_user_id, **referee_event_data}

        get_streamer().send(data=referrer_data)
        get_streamer().send(data=referee_data)
