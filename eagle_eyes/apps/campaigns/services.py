from dataclasses import dataclass
from typing import List
from eagle_eyes.apps.campaigns.models import Campaign, CampaignState
from eagle_eyes.apps.campaigns.models import Action, Event
from eagle_eyes.apps.referral.models import Referral
from eagle_eyes.apps.eagleusers.services import UserService
from django.utils.dateparse import parse_datetime
from datetime import timedelta
from django.utils import timezone
from django.utils.dateparse import parse_duration
from copy import deepcopy
from django.core.cache import cache
import json


class CampaignStateService:

    @classmethod
    def generate_state_template(cls, campaign: Campaign) -> List:
        stage_list = []
        for stage in campaign.stages.prefetch_related(
            'reward_criterias'
        ).order_by('index').all():

            criteria_dict = {}
            for rc in stage.reward_criterias.all():
                rc_key = str(rc.pk)
                criteria_dict[rc_key] = {
                    'user_value': 0,
                    'done': False,
                    'started': None,
                    'finished': None,
                    'duration_seconds': None,
                }
            stage_list.append({
                'index': stage.index,
                'criteria': criteria_dict,
                'done': False,
                'started': None,
                'finished': None,
                'duration_seconds': None
            })

        return {
            "stages": stage_list
        }

    @classmethod
    def inject_campaign_config(cls, campaign_state: CampaignState, campaign: Campaign = None):
        if campaign is None:
            campaign = campaign_state.campaign

        # Iterate over campaign stages & criteria and inject configs
        for stage_index, stage in enumerate(list(
            campaign.stages.prefetch_related(
                'reward_criterias__action__vertical'
            ).order_by('index').all().cache()
        )):
            # Inject stage config
            campaign_state = deepcopy(campaign_state)
            campaign_state.state['stages'][stage_index]['title'] = stage.title
            campaign_state.state['stages'][stage_index]['delay'] = str(stage.delay)

            # Inject criteria config
            rcs = stage.reward_criterias.all().cache()
            for rc in rcs:
                rc_key = str(rc.pk)
                campaign_state.state['stages'][stage_index]['criteria'][rc_key]['action'] = rc.action.title
                campaign_state.state['stages'][stage_index]['criteria'][rc_key]['vertical'] = rc.action.vertical.name
                campaign_state.state['stages'][stage_index]['criteria'][rc_key]['param'] = rc.param
                campaign_state.state['stages'][stage_index]['criteria'][rc_key]['title'] = rc.title
                campaign_state.state['stages'][stage_index]['criteria'][rc_key]['hyperlink'] = rc.hyperlink
                campaign_state.state['stages'][stage_index]['criteria'][rc_key]['criteria_value'] = rc.value

        return campaign_state

    @classmethod
    def get_or_create(cls, user_id: str, campaign: Campaign) -> CampaignState:
        campaign_state, _ = CampaignState.objects.get_or_create(
            user_id=user_id,
            campaign=campaign,
            defaults={
                'state': cls.generate_state_template(campaign=campaign)
            }
        )
        return campaign_state

    @classmethod
    def get_or_create_in_memory(cls, user_id: str, campaign: Campaign, fetch_campaign: bool = False) -> CampaignState:
        try:
            if fetch_campaign:
                campaign_state = CampaignState.objects.select_related('campaign')\
                    .get(user_id=user_id, campaign=campaign)
            else:
                campaign_state = CampaignState.objects.get(user_id=user_id, campaign=campaign)
        except CampaignState.DoesNotExist:
            campaign_state = CampaignState(
                user_id=user_id,
                campaign=campaign,
                state=cls.generate_state_template(campaign=campaign)
            )
        return campaign_state

    @classmethod
    def has_win_chance(cls, campaign_state: CampaignState) -> bool:
        campaign = campaign_state.campaign
        stages = campaign_state.state['stages']
        if not stages:
            return False
        checkpoints = campaign.checkpoints.order_by('percentage')
        threshold = 100.0 if not checkpoints else checkpoints[0].percentage
        min_stage_index = CampaignStateService.get_min_stage_index(campaign_state, threshold, campaign_state)

        # the simple case if the user has not done any stage for the campaign
        if not stages[0]['done']:
            total_delay = sum(
                (parse_duration(stage['delay']) for stage in stages[:min_stage_index]),
                timedelta()
            )
            return timezone.now() + total_delay + timedelta(minutes=10) < campaign.end_date

        # get the current stage
        current_stage = max(
            [stage for stage in stages if stage['done']],
            key=lambda stage: stage['index']
        )
        current_stage_index = stages.index(current_stage)

        # if the user has reached the minimum stage, they have a win chance
        if current_stage_index >= min_stage_index:
            return True

        total_delay = sum(
            (parse_duration(stage['delay']) for stage in stages[current_stage_index+1: min_stage_index]),
            timedelta()
        )
        # differentiates between the two cases:
        # 1- user is allowed to do the actions of their next stage
        # 2- user should wait untill the delay days for his current stage is finished
        fastest_finish_time = max(
            parse_datetime(current_stage['finished']) + parse_duration(current_stage['delay']),
            timezone.now()
        ) + total_delay

        return fastest_finish_time + timedelta(minutes=10) < campaign.end_date

    @staticmethod
    def get_current_percentage(campaign_state, campaign_state_with_config=None):
        if campaign_state_with_config is None:
            campaign_state_with_config = CampaignStateService.inject_campaign_config(campaign_state)
        progress_type = campaign_state.campaign.progress_type
        state = campaign_state_with_config.state
        user_value = 0
        total_value = 0
        if progress_type == str(Campaign.ProgressType.STAGE_STATE):
            user_value = len([stage for stage in state["stages"] if stage["done"]])
            total_value = len([stage for stage in state["stages"]])
        if progress_type == str(Campaign.ProgressType.REWARD_CRITERIA_STATE):
            for stage in state["stages"]:
                user_value += len([value for _, value in stage["criteria"].items() if value["done"]])
                total_value += len(stage["criteria"])
        if progress_type == str(Campaign.ProgressType.REWARD_CRITERIA_VALUE):
            for stage in state["stages"]:
                for _, value in stage["criteria"].items():
                    user_value += value["user_value"]
                    total_value += value["criteria_value"]
        if progress_type == str(Campaign.ProgressType.MIN_CRITERIA_VALUE):
            user_value = None
            count = 0
            for stage in state["stages"]:
                for _, value in stage["criteria"].items():
                    count += 1
                    user_value = value["user_value"] if user_value is None else min(user_value, value["user_value"])
                    total_value += value["criteria_value"]
            user_value *= count
        return round(user_value / total_value * 100)

    @staticmethod
    def get_min_stage_index(campaign_state, threshold, campaign_state_with_config=None):
        if campaign_state_with_config is None:
            campaign_state_with_config = CampaignStateService.inject_campaign_config(campaign_state)
        state = campaign_state_with_config.state
        campaign_id = campaign_state_with_config.campaign.id
        key = f"min_stage_index:{campaign_id}"
        min_index = cache.get(key)
        if min_index is not None:
            return int(min_index)
        progress_type = campaign_state.campaign.progress_type
        stage_value = 0
        total_value = 0
        if progress_type == str(Campaign.ProgressType.STAGE_STATE):
            total_value = len(state["stages"])
            for index, stage in enumerate(state["stages"]):
                stage_value += 1
                if int(stage_value / total_value * 100) >= threshold:
                    min_index = index
                    break
        elif progress_type == str(Campaign.ProgressType.REWARD_CRITERIA_STATE):
            total_value = sum(len(stage["criteria"]) for stage in state["stages"])
            for index, stage in enumerate(state["stages"]):
                stage_value += len(stage["criteria"])
                if int(stage_value / total_value * 100) >= threshold:
                    min_index = index
                    break
        elif progress_type == str(Campaign.ProgressType.REWARD_CRITERIA_VALUE):
            total_value = sum(value["criteria_value"] for stage in state["stages"]
                              for _, value in stage["criteria"].items())
            for index, stage in enumerate(state["stages"]):
                for _, value in stage["criteria"].items():
                    stage_value += value["criteria_value"]
                if int(stage_value / total_value * 100) >= threshold:
                    min_index = index
                    break
        elif progress_type == str(Campaign.ProgressType.MIN_CRITERIA_VALUE):
            total_value = sum(value["criteria_value"] for stage in state["stages"]
                              for _, value in stage["criteria"].items())
            for index, stage in enumerate(state["stages"]):
                for _, value in stage["criteria"].items():
                    stage_value += value["criteria_value"]
                if int(stage_value / total_value * 100) >= threshold:
                    min_index = index
                    break
        cache.set(campaign_id, min_index, timeout=60*60)
        return min_index

    @staticmethod
    def get_current_checkpoint(user_id, campaign):
        campaign_state = CampaignStateService.get_or_create_in_memory(user_id, campaign)
        campaign_state = CampaignStateService.inject_campaign_config(campaign_state, campaign)
        percentage = CampaignStateService.get_current_percentage(campaign_state, campaign_state)
        checkpoints = campaign.checkpoints.all()
        done_checkpoints = [checkpoint for checkpoint in checkpoints if checkpoint.percentage <= percentage]
        if not done_checkpoints:
            return None
        current_checkpoint = max(done_checkpoints, key=lambda x: x.percentage)
        return current_checkpoint

    @staticmethod
    def is_referee(campaign_state, campaign=None):
        if campaign is None:
            campaign = campaign_state.campaign
        if campaign.campaign_type != str(Campaign.CampaignType.REFEREE):
            return False
        phone_number = UserService.phone_number(campaign_state.user_id)
        return Referral.objects.filter(referee_phone_number=phone_number).exists()


class LoggingService:

    @staticmethod
    def create_log_template(event):
        return {
            "user_id": event.event_obj.user,
            "vertical": event.vertical_name,
            "action": event.action_title,
            "params": event.event_obj.params,
            "date_time": event.event_obj.date_time.isoformat(),
            "inserted": "false",
            "processed": "false",
            "logtime": timezone.now().isoformat(),
        }

    @staticmethod
    def save_logs(logger, logs):
        for log in logs:
            logger.info(json.dumps(log))


@dataclass(frozen=True)
class EventData:
    event_obj: Event
    vertical_name: str
    action_title: str


def parse_event(msg) -> EventData:
    event_date = parse_datetime(msg.value.get('date_time'))
    vertical_name = msg.value.get('vertical')
    action_title = msg.value.get('action')
    params = msg.value.get('params')
    user_id = msg.value.get('user_id')

    # Get action data from db
    action = Action.objects.get(title=action_title, vertical__name=vertical_name)

    # Insert event into db
    event = Event(
        user=user_id,
        action=action,
        params=params,
        date_time=event_date
    )

    event_data = EventData(
        event_obj=event,
        vertical_name=vertical_name,
        action_title=action_title
    )

    return event_data
