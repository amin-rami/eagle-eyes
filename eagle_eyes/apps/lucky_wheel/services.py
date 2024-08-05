import datetime
import random
import jwt
from dataclasses import dataclass
from functools import lru_cache
from os import getenv

from django.core.cache import cache
from django.core.validators import RegexValidator
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request

from eagle_eyes.utils import Persian
from eagle_eyes.apps.behsa.v1.behsa_apis import BehsaApi
from eagle_eyes.apps.behsa.v1.exceptions import (DataNotValid,
                                                 InvalidValidateToken,
                                                 UserAlreadyAttempted,
                                                 )
from eagle_eyes.apps.lucky_wheel.models import LuckyWheel, UserReward
from eagle_eyes.apps.campaigns.models import CampaignState


@lru_cache
def get_behsa():
    return BehsaApi()


behsa_api = get_behsa()
phone_validator = RegexValidator(regex=r"^[9]\d{9}$")


@dataclass
class PhoneDetail:
    number: str = ""
    is_mci: bool = False


@dataclass
class UserDetail:
    phone_detail: PhoneDetail
    salt_token: str = ""


class LuckyWheelService:
    @staticmethod
    def list_slices(campaign_id):
        return LuckyWheel.objects.filter(campaign_id=campaign_id, active=True)

    @staticmethod
    def validate_user_campaign(user_id, campaign_id):
        campaign_state = CampaignState.objects.filter(campaign_id=campaign_id, user_id=user_id).first()
        if campaign_state is None or not campaign_state.done:
            raise PermissionDenied(detail="User has not done all camapign requirements")

        count = UserReward.objects.filter(user_id=user_id, slice__campaign_id=campaign_id).count()
        if count >= 1:
            raise PermissionDenied(detail="Limit for winning this camapign has exceeded")
        return True

    @staticmethod
    def check_active_rewards(request, salt_token=None):
        auth_token = request.headers.get('x_auth_token')
        salt_token = request.headers.get('x_salt_token') if salt_token is None else salt_token
        inquiry = behsa_api.chance_inquiry(auth_token, salt_token)
        if inquiry["data"]["packageInfo"] is None:
            return True
        behsa_active_date = inquiry["data"]["packageInfo"]['ACTIVE_DATE'].split(" ")
        behsa_date = Persian(behsa_active_date[0]).gregorian_string()
        last_reward = datetime.datetime.strptime(behsa_date, "%Y-%m-%d")
        today = datetime.date.today()
        if (last_reward + datetime.timedelta(days=1)).date() <= today:
            return True
        raise UserAlreadyAttempted()

    @staticmethod
    def get_valid_phone_detail(auth_token, salt_token) -> PhoneDetail:
        resp = behsa_api.verify_current_status(auth_token, salt_token)
        return PhoneDetail(resp['phone_number'], not resp['non_mci'])

    # TODO enable typeguard on check_validate
    @staticmethod
    def behsa_validate(request: Request) -> UserDetail:
        phone_number = request.data.get('phone_number')
        auth_token = request.headers.get('x_auth_token')
        user_agent = request.headers.get('user_agent')
        lucky_access = request.headers.get('x_lucky_access')
        if not ((user_agent and user_agent.lower().startswith("okhttp")) or lucky_access):
            raise DataNotValid()
        salt_token = behsa_api.salt(auth_token)
        phone_detail = LuckyWheelService.get_valid_phone_detail(auth_token, salt_token)

        if phone_number != phone_detail.number or not phone_detail.is_mci:
            raise DataNotValid()
        return UserDetail(phone_detail, salt_token)

    @staticmethod
    def create_token(payload, expire: int = 60) -> str:
        if not payload.get('exp'):
            payload['exp'] = datetime.datetime.now(tz=datetime.timezone.utc) \
                + datetime.timedelta(seconds=expire)
        return jwt.encode(payload, getenv("JWT_SIGNING_KEY"), algorithm="RS256")

    @staticmethod
    def decode_token(token: str):
        try:
            return jwt.decode(token, getenv("JWT_VERIFYING_KEY"), algorithms=["RS256"])
        except Exception:
            raise InvalidValidateToken()

    @staticmethod
    def validate_token(token):
        data = LuckyWheelService.decode_token(token)
        redis_token = cache.get(f"authorize:{data['user_id']}")
        if redis_token != token:
            raise InvalidValidateToken()
        cache.delete(f"authorize:{data['user_id']}")
        return data

    @staticmethod
    def allocate_reward(wheel_slices) -> LuckyWheel:
        return random.choices(wheel_slices, weights=[wheel_slice.chance for wheel_slice in wheel_slices])[0]

    @staticmethod
    def create_user_reward(user_id, reward):
        UserReward.objects.get_or_create(
            user_id=user_id,
            slice=reward,
            date_time=timezone.now(),
        )
