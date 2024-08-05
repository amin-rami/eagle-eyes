import os
import jwt
import json
import requests
from functools import lru_cache
from eagle_eyes.apps.behsa.v1.behsa_apis import BehsaApi
from eagle_eyes.apps.referral_reward import exceptions
from eagle_eyes.apps.campaigns.services import CampaignStateService
from eagle_eyes.apps.referral_reward.models import UserReward, Reward
from eagle_eyes.apps.eagleusers.services import UserService
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from sentry_sdk import capture_exception


BW3_BASE_URL = os.getenv('BW3_BASE_URL')
BW3_TOKEN = os.getenv('BW3_TOKEN')


@lru_cache
def get_behsa():
    return BehsaApi()


behsa_api = get_behsa()


class RewardServices:

    @staticmethod
    def get_rewards_status(user_id, campaign):
        campaign_state = CampaignStateService.get_or_create_in_memory(user_id, campaign)
        campaign_state = CampaignStateService.inject_campaign_config(campaign_state, campaign)
        percentage = CampaignStateService.get_current_percentage(campaign_state, campaign_state)
        checkpoints = campaign.checkpoints.prefetch_related("reward").order_by("percentage").cache().all()
        rewards = [checkpoint.reward.first() for checkpoint in checkpoints]
        checkpoints_done = [percentage >= checkpoint.percentage for checkpoint in checkpoints]
        rewards_claim_status = []
        rewards_claim_date = []
        for index, reward in enumerate(rewards):
            claimed_reward = UserReward.objects.filter(user_id=user_id, reward=reward).first()
            if not checkpoints_done[index]:
                rewards_claim_status.append(False)
                rewards_claim_date.append(None)
                continue
            if claimed_reward is not None:
                rewards_claim_status.append(True)
                rewards_claim_date.append(claimed_reward.date_time)
                continue
            rewards_claim_status.append(False)
            rewards_claim_date.append(None)
        reward_status = [
            {
                "done": checkpoint_done,
                "claimed": claim_status,
                "claim_date": reward_claim_date,
            }
            for checkpoint_done, claim_status, reward_claim_date
            in zip(checkpoints_done, rewards_claim_status, rewards_claim_date)
        ]
        return reward_status

    @staticmethod
    def inject_rewards_config(campaign):
        checkpoints = campaign.checkpoints.prefetch_related("reward").order_by("percentage").cache().all()
        rewards = [checkpoint.reward.first() for checkpoint in checkpoints]
        rewards_configs = [
            {
                "title": reward.title,
                "desc": reward.description,
                "index": reward.index,
                "id": reward.id,
                "image": reward.get_image_url
            }
            for reward in rewards
        ]
        return rewards_configs

    @staticmethod
    def gather_rewards_info(user_id, campaign):
        rewards_status = RewardServices.get_rewards_status(user_id, campaign)
        rewards_config = RewardServices.inject_rewards_config(campaign)
        rewards_info = [
            {**reward_status, **reward_config}
            for reward_status, reward_config in zip(rewards_status, rewards_config)
        ]
        for reward_info in rewards_info:
            if reward_info["done"] and not reward_info["claimed"]:
                reward_token = RewardServices.get_or_create_reward_token(
                    user_id, reward_info["id"])
            else:
                reward_token = None
            reward_info.update({"reward_token": reward_token})
        return rewards_info

    @staticmethod
    def generate_key(user_id, reward_id):
        return f"authorize:{user_id}:{reward_id}"

    @staticmethod
    def get_or_create_reward_token(user_id, reward_id):
        key = RewardServices.generate_key(user_id, reward_id)
        token = cache.get(key)
        if token is not None:
            return token
        phone_number = UserService.phone_number(user_id)
        is_mci = UserService.is_mci(phone_number)
        payload = {
            "user_id": user_id,
            "reward_id": reward_id,
            "phone_number": phone_number,
            "is_mci": is_mci,
        }
        token = jwt.encode(
            payload,
            os.getenv("JWT_SIGNING_KEY"),
            algorithm="RS256",
        )
        cache.set(key, token)
        return token

    @staticmethod
    def decode_token(token):
        try:
            return jwt.decode(token, os.getenv("JWT_VERIFYING_KEY"), algorithms=["RS256"])
        except Exception as exception:
            capture_exception(exception)
            raise exceptions.InvalidToken()

    @staticmethod
    def validate_token(user_id, reward_token):
        data = RewardServices.decode_token(reward_token)
        key = RewardServices.generate_key(user_id, data['reward_id'])
        cached_token = cache.get(key)

        if cached_token is None:
            reward_id = int(data['reward_id'])
            campaign = (
                Reward.objects.select_related('checkpoint__campaign')
                .filter(id=reward_id)
                .cache()
                .first()
                .checkpoint.campaign
            )
            RewardServices.gather_rewards_info(user_id, campaign)
            cached_token = cache.get(key)

        if cached_token != reward_token:
            raise exceptions.TokenOwnerMismatch()
        return data

    @staticmethod
    def create_user_reward(user_id, reward_id, auth_number, is_mci, phone_number=None):
        reward = Reward.objects.get(id=reward_id)
        if not phone_number:
            phone_number = UserService.phone_number(user_id)
        return UserReward(
            user_id=user_id,
            phone_number=phone_number,
            auth_number=auth_number,
            reward=reward,
            date_time=timezone.now(),
            is_mci=is_mci
        )

    @staticmethod
    def check_active_reward(phone_number, reward_id):
        reward = Reward.objects.get(id=reward_id)
        has_active_reward = UserReward.objects.filter(
            auth_number=phone_number,
            reward__offer_id=reward.offer_id,
            date_time__gte=timezone.now() - timedelta(days=1)
        ).exists()
        if has_active_reward:
            raise exceptions.AlreadyActiveReward()

    @staticmethod
    def allocate(user_id: str, offer_id: int, auth_token=None) -> requests.Response:

        if auth_token:
            salt_token = behsa_api.salt(auth_token)
            behsa_api.chance_activation(auth_token, salt_token, offer_id)
        else:
            req = requests.post(
                f'{BW3_BASE_URL}/auth/behsa/activation',
                json.dumps({
                    "userId": user_id,
                    "offerId": offer_id
                }),
                headers={
                    'Authorization': f'Bearer {BW3_TOKEN}',
                    'Content-Type': 'application/json'
                }
            )
            if req.status_code == 401:
                raise exceptions.NotEnoughPermissions()
            if req.status_code >= 400:
                raise exceptions.InvalidToken()
            elif req.status_code != 200:
                raise exceptions.AllocationFailed()
            return req
