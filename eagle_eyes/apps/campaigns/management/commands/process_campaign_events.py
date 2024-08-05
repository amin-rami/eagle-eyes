import json
import logging
from datetime import timedelta
from typing import List
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django_prometheus.conf import NAMESPACE
from django_prometheus.models import model_inserts
from kafka import KafkaConsumer
from prometheus_client import start_http_server, Counter
from eagle_eyes.apps.campaigns.models import Event, Stage, Campaign
from eagle_eyes.settings import (
    EVENT_PROCESSOR_BATCH_SIZE,
    EVENT_PROCESSOR_BATCH_TIMEOUT_SECONDS
)
from eagle_eyes.settings import KAFKA_EVENT_TOPIC, KAFKA_BOOTSTRAP_SERVERS, KAFKA_EVENT_TOPIC_CONSUMER_GROUP
from eagle_eyes.apps.campaigns.services import CampaignStateService, EventData, parse_event
from eagle_eyes.apps.referral.processing import process_mutual_event
from eagle_eyes.apps.campaigns.services import LoggingService


event_inserts = Counter(
    "django_model_inserts_total_by_vertical_action",
    "Number of insert operations on events by vertical and action.",
    ["model", "vertical", "action"],
    namespace=NAMESPACE,
)


def get_stage_idx_in_list(stage, stage_list: list):
    for i, s in enumerate(stage_list):
        if s['index'] == stage.index:
            return i


def count_event_metrics(events: List[EventData], event_metrics):
    for event in events:
        action_title = event.action_title
        vertical_name = event.vertical_name
        if event_metrics.get(vertical_name, {}).get(action_title):
            event_metrics[vertical_name][action_title] += 1
        else:
            event_metrics[vertical_name] = {action_title: 1}


def process_event_v2(event: Event):
    """
    Steps:
        1. Get active campaigns
        2. Get stage with least index that it's start time is reached and has not been done by user of the
            event in step 1 campaigns.
        3. Get criteria of stages in step 2 that their action&parameter match the event action&parameter
            and has not been done.
        4. Update the user_value (user_state) for criteria in step 3.
    """
    pass


def process_event(event: Event):

    # events backward compatibility (or just ignore it!)
    if len(str(event.user)) != 36:
        return

    # filter out campaigns which the user does not have win chance
    campaigns = Campaign.objects.filter(
        start_date__lte=event.date_time,
        end_date__gte=event.date_time
    )
    campaign_states = [CampaignStateService.get_or_create_in_memory(
        user_id=event.user,
        campaign=campaign,
        fetch_campaign=True
        )
        for campaign in campaigns]
    campaign_states_with_config = [
        CampaignStateService.inject_campaign_config(campaign_state, campaign)
        for campaign_state, campaign in zip(campaign_states, campaigns)
    ]
    campaigns = [
        campaign_state_with_config.campaign
        for campaign_state_with_config in campaign_states_with_config
        if CampaignStateService.has_win_chance(campaign_state_with_config)
    ]

    # get reward criteria for this action containing active campaigns
    reward_criterias = [rc for rc in event.action.reward_criterias.select_related('stage__campaign').filter(
        stage__campaign__in=campaigns)]
    reward_criterias.extend(
        [
            rc for parent_action in event.action.parent_actions.all()
            for rc in
            parent_action.reward_criterias.select_related('stage__campaign').filter(stage__campaign__in=campaigns)
        ]
    )

    for rc in reward_criterias:

        rc_key = str(rc.pk)

        # If event parameters does not contain reward_criteria param, and reward_criteria param
        # is not None, then the event is not related to this reward_criteria
        if rc.param is not None and rc.param not in event.params.keys():
            continue

        campaign = rc.stage.campaign
        campaign_state = [cs for cs in campaign_states if cs.campaign == campaign][0]

        # Get index of the stage in state of campaign_state
        stage_idx = get_stage_idx_in_list(rc.stage, campaign_state.state["stages"])

        # If criteria is done, ignore the event
        if campaign_state.state["stages"][stage_idx]['criteria'][rc_key]['done'] is True:
            continue

        # If stages with higher priority are not done yet, Ignore the event
        all_higher_stages_done = all(
            stage['done'] for stage in campaign_state.state["stages"]
            if stage['index'] < rc.stage.index
        )
        if not all_higher_stages_done:
            continue

        # Check if previous stage's delay is passed
        higher_stages = [stage for stage in campaign_state.state["stages"] if stage['index'] < rc.stage.index]

        if len(higher_stages) > 0:
            # Get previous stage (stage with maximum index among all the stages with smaller index than current stage)
            previous_stage_state = max(higher_stages, key=lambda x: x['index'])
            previous_stage = Stage.objects.get(
                campaign=campaign,
                index=previous_stage_state['index']
            )
            if parse_datetime(previous_stage_state['finished']) + previous_stage.delay > event.date_time:
                continue

        # If it is the first time we are updating reward criteria, set the started date
        # Is there a need to check the user_value instead of doing the following check?
        if campaign_state.state["stages"][stage_idx]['criteria'][rc_key]['started'] is None:
            campaign_state.state["stages"][stage_idx]['criteria'][rc_key]['started'] = \
                event.date_time.isoformat()
        else:
            campaign_state.state["stages"][stage_idx]['criteria'][rc_key]['started'] = min(
                parse_datetime(campaign_state.state["stages"][stage_idx]['criteria'][rc_key]['started']),
                event.date_time
            ).isoformat()

        # If it is the first time we are updating stage, set the started date
        if campaign_state.state["stages"][stage_idx]['started'] is None:
            campaign_state.state["stages"][stage_idx]['started'] = event.date_time.isoformat()
        else:
            campaign_state.state["stages"][stage_idx]['started'] = min(
                parse_datetime(campaign_state.state["stages"][stage_idx]['started']),
                event.date_time
            ).isoformat()

        # If it is the first time we are updating the campaign, set the started date
        if campaign_state.started is None:
            campaign_state.started = event.date_time
        else:
            campaign_state.started = min(
                campaign_state.started,
                event.date_time
            )

        # Update user_value for the reward criteria (calculate sum for numeric param values, and count for others)
        if rc.param is None or type(event.params[rc.param]) not in [int, float]:
            campaign_state.state["stages"][stage_idx]['criteria'][rc_key]['user_value'] += 1
        else:
            campaign_state.state["stages"][stage_idx]['criteria'][rc_key]['user_value'] += \
                event.params[rc.param]

        # check if user has done the reward criteria
        if campaign_state.state["stages"][stage_idx]['criteria'][rc_key]['user_value'] >= rc.value \
                and campaign_state.state["stages"][stage_idx]['criteria'][rc_key]['done'] is not True:
            campaign_state.state["stages"][stage_idx]['criteria'][rc_key]['done'] = True
            campaign_state.state["stages"][stage_idx]['criteria'][rc_key]['finished'] = \
                event.date_time.isoformat()
            campaign_state.state["stages"][stage_idx]['criteria'][rc_key]['duration_seconds'] = (
                parse_datetime(campaign_state.state["stages"][stage_idx]['criteria'][rc_key]['finished']) -
                parse_datetime(campaign_state.state["stages"][stage_idx]['criteria'][rc_key]['started'])
            ).seconds

            # Check if all criterias are done for this stage
            all_criterias_done: bool = all(
                criteria['done'] for _, criteria in campaign_state.state["stages"][stage_idx]['criteria'].items()
            )
            if all_criterias_done:
                campaign_state.state["stages"][stage_idx]['done'] = True
                campaign_state.state["stages"][stage_idx]['finished'] = max(
                    parse_datetime(criteria['finished'])
                    for _, criteria in campaign_state.state["stages"][stage_idx]['criteria'].items()
                ).isoformat()
                campaign_state.state["stages"][stage_idx]['duration_seconds'] = (
                    parse_datetime(campaign_state.state["stages"][stage_idx]['finished']) -
                    parse_datetime(campaign_state.state["stages"][stage_idx]['started'])
                ).seconds

            # Check if all stages are done for this campaign
            all_stages_done: bool = all(
                stage['done'] for stage in campaign_state.state["stages"]
            )
            if all_stages_done:
                campaign_state.done = True
                campaign_state.finished = max(
                    parse_datetime(stage['finished']) for stage in campaign_state.state["stages"]
                )
                campaign_state.duration = campaign_state.finished - campaign_state.started

        campaign_state.save()


class Command(BaseCommand):
    help = 'Starts the campaign events processor'

    def handle(self, *args, **kwargs):
        # Start a web server to expose prometheus metrics
        start_http_server(8001)

        consumer = KafkaConsumer(
            KAFKA_EVENT_TOPIC,
            group_id=KAFKA_EVENT_TOPIC_CONSUMER_GROUP,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            enable_auto_commit=False,
        )
        logger = logging.getLogger('event_processor')

        events: List[EventData] = []
        batch_size = int(EVENT_PROCESSOR_BATCH_SIZE)
        batch_timeout = timedelta(seconds=int(EVENT_PROCESSOR_BATCH_TIMEOUT_SECONDS))
        start_time = timezone.now()

        while True:
            event_metrics = dict()
            msg_pack = consumer.poll()
            events.extend([parse_event(item) for _, records in msg_pack.items() for item in records])
            if len(events) < batch_size and timezone.now() - start_time < batch_timeout:
                continue
            logging.info(f"Started processing event batch of size {len(events)}")
            if len(events) == 0:
                start_time = timezone.now()
                continue
            with transaction.atomic():
                # Persist events
                event_logs = [LoggingService.create_log_template(event) for event in events]
                for index, event in enumerate(events):
                    if event.event_obj.user:
                        event_logs[index]["inserted"] = "true"
                        event_logs[index]["processed"] = "true"
                LoggingService.save_logs(logger, event_logs)

                events = [event for event in events if event.event_obj.user]
                Event.objects.bulk_create([event.event_obj for event in events])
                # Count event metrics
                count_event_metrics(events=events, event_metrics=event_metrics)
                # Process events to update user state in active campaigns
                for event in events:
                    process_event(event=event.event_obj)
                    process_mutual_event(event=event.event_obj)
                # Reset batch state
                events_count = len(events)
                events.clear()
                start_time = timezone.now()
                # Commit the consumer offset
                consumer.commit()

            logging.info("Done!")
            # Send metrics of inserted events
            model_inserts.labels('event').inc(events_count)
            for vertical, actions in event_metrics.items():
                for ac_key, ac_value in actions.items():
                    event_inserts.labels(model='event', vertical=vertical, action=ac_key).inc(ac_value)
