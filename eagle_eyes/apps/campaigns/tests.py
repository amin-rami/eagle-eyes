import json
from eagle_eyes.apps.campaigns.management.commands.process_campaign_events import process_event
from eagle_eyes.apps.campaigns.models import (
    Action,
    ActionParameter,
    Event,
    RewardCriteria,
    Campaign,
    CampaignState,
    Vertical,
    Stage,
    CampaignCheckpoint,
)
from eagle_eyes.apps.campaigns.services import CampaignStateService
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from django.test import TestCase, Client
from django.utils.dateparse import parse_datetime
import uuid


class CampaignStateDetailsTest(TestCase):
    @patch('eagle_eyes.apps.campaigns.models.Campaign.image', new_callable=str)
    def setUp(self, mock_image):
        # create a vertical
        self.vertical = Vertical.objects.create(
            name='media'
        )

        # create two actions for the vertical
        self.download = Action.objects.create(
            title='download',
            vertical=self.vertical
        )

        self.comment = Action.objects.create(
            title='comment',
            vertical=self.vertical
        )

        self.norooz = Campaign.objects.create(
            title='Norooz',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=10),
        )

        self.stage0_norooz = Stage.objects.create(
            campaign=self.norooz,
            index=0
        )

        self.rc1_norooz = RewardCriteria.objects.create(
            stage=self.stage0_norooz,
            action=self.comment,
            value=5
        )

        self.rc2_norooz = RewardCriteria.objects.create(
            stage=self.stage0_norooz,
            action=self.download,
            value=1
        )

        self.yalda = Campaign.objects.create(
            title='Yalda',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=1),
        )

        self.ramezan = Campaign.objects.create(
            title='Ramezan',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=1),
        )

        self.stage0_yalda = Stage.objects.create(
            campaign=self.yalda,
            index=1
        )

        self.rc1_yalda = RewardCriteria.objects.create(
            stage=self.stage0_yalda,
            action=self.comment,
            value=10
        )

        RewardCriteria.objects.create(
            stage=Stage.objects.create(
                campaign=self.ramezan,
                index=0
            ),
            action=self.download,
            value=10
        )

        self.user_id = str(uuid.uuid4())

        event = Event(
            user=self.user_id,
            action=self.comment,
            date_time=timezone.now()
        )

        process_event(event)

    def test_invalid_campaign_id(self):
        """ Test output when campaign_id is invalid """
        url = reverse(
            'campaigns:campaign_state_list',
            kwargs={'version': 'v1'}
        )
        params = {'campaign_id': self.norooz.id + 100}
        headers = {'X-User-ID': self.user_id}
        response = self.client.get(url, params, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_invalid_user_id(self):
        """ Test output when user_id is invalid """
        url = reverse(
            'campaigns:campaign_state_list',
            kwargs={'version': 'v1'}
        )
        params = {'campaign_id': self.norooz.id}
        headers = {'X-User-ID': str(uuid.uuid4())}
        response = self.client.get(url, params, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    @patch('eagle_eyes.apps.campaigns.serializers.CampaignStateListSerializer.get_image_path', lambda x, y: '')
    def test_valid_data(self):
        """ Test output for a valid data """
        url = reverse(
            'campaigns:campaign_state_list',
            kwargs={'version': 'v1'}
        )
        params = {'campaign_id': self.norooz.id}
        headers = {'X-User-ID': self.user_id}
        response = self.client.get(url, params, headers=headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['campaign'], self.norooz.id)
        self.assertEqual(response.data[0]['user_id'], self.user_id)

    @patch('eagle_eyes.apps.campaigns.serializers.CampaignStateListSerializer.get_image_path', lambda x, y: '')
    def test_show_all_active_campaigns(self):
        """ Test if API returns all `active` campaigns """
        url = reverse(
            'campaigns:campaign_state_list',
            kwargs={'version': 'v1'}
        )
        headers = {'X-User-ID': self.user_id}
        response = self.client.get(url, headers=headers)
        self.assertEqual(len(response.data), 3)
        # We should have persisted state in just 2 of 3 campaigns
        self.assertEqual(len([state for state in response.data if state["id"] is not None]), 2)
        self.assertEqual(len([state for state in response.data if state["id"] is None]), 1)


class EventListTestCase(TestCase):
    # set-up initial data for test
    def setUp(self):
        # create two vertical named media and sports
        media = Vertical.objects.create(name='media')
        sports = Vertical.objects.create(name='sports')

        # create "comment" action for media vertical and "watch a video" action for sports vertical
        action_comment = Action.objects.create(
            title='comment',
            vertical=media
        )
        ActionParameter.objects.create(
            action=action_comment,
            key='param1',
            value_type=ActionParameter.ParamValueType.INT
        )
        ActionParameter.objects.create(
            action=action_comment,
            key='param2',
            value_type=ActionParameter.ParamValueType.STR
        )
        ActionParameter.objects.create(
            action=action_comment,
            key='param3',
            value_type=ActionParameter.ParamValueType.FLOAT
        )

        action_watch = Action.objects.create(
            title='watch a video',
            vertical=sports
        )
        ActionParameter.objects.create(
            action=action_watch,
            key='param4',
            value_type=ActionParameter.ParamValueType.INT
        )
        ActionParameter.objects.create(
            action=action_watch,
            key='param5',
            value_type=ActionParameter.ParamValueType.FLOAT
        )

    @patch("eagle_eyes.apps.campaigns.views.get_streamer")
    def test_correct_data(self, get_streamer_mock):
        """test the output for a correct input data"""
        client = Client()
        headers = {'X-User-ID': str(uuid.uuid4())}
        response = client.post(
            reverse('campaigns:event_list', kwargs={"version": "v1"}),
            {
                'vertical': 'media',
                'action': 'comment',
            },
            headers=headers
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['vertical'], 'media')
        self.assertEqual(response.json()['action'], 'comment')

    @patch("eagle_eyes.apps.campaigns.views.get_streamer")
    def test_correct_data_with_date_time(self, get_streamer_mock):
        """test the output for a correct input data with an extra date_time field"""
        client = Client()
        data_datetime = '2023-01-12 09:44:46.185312+00:00'
        headers = {'X-User-ID': str(uuid.uuid4())}
        response = client.post(
            reverse('campaigns:event_list', kwargs={"version": "v1"}),
            {
                'vertical': 'media',
                'action': 'comment',
                'date_time': data_datetime
            },
            headers=headers
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['vertical'], 'media')
        self.assertEqual(response.json()['action'], 'comment')
        self.assertNotEqual(response.json()['date_time'], data_datetime)

    @patch("eagle_eyes.apps.campaigns.views.get_streamer")
    def test_invalid_action_params(self, get_streamer_mock):
        """test API response for invalid action parameters"""

        parameters = {
            'param1': '12',
            'wrong_param': 15.33,
            'param3': '12.5'
        }
        headers = {'X-User-ID': str(uuid.uuid4())}
        response = self.client.post(
            reverse('campaigns:event_list', kwargs={"version": "v1"}),
            {
                'vertical': 'media',
                'action': 'comment',
                'params': json.dumps(parameters)
            },
            headers=headers
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("eagle_eyes.apps.campaigns.views.get_streamer")
    def test_valid_action_params(self, get_streamer_mock):
        """test API response for valid action parameters"""

        parameters = {
            'param4': '1255',
            'param5': 1,
        }
        headers = {'X-User-ID': str(uuid.uuid4())}
        response = self.client.post(
            reverse('campaigns:event_list', kwargs={"version": "v1"}),
            {
                'vertical': 'sports',
                'action': 'watch a video',
                'params': json.dumps(parameters)
            },
            headers=headers
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_correct_vertical_wrong_action(self):
        """test the output for input data with correct vertical field and wrong action field"""
        headers = {'X-User-ID': str(uuid.uuid4())}
        client = Client()
        response = client.post(
            reverse('campaigns:event_list', kwargs={"version": "v1"}),
            {
                'vertical': 'media',
                'action': 'WRONG ACTION',
            },
            headers=headers
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_vertical_correct_action(self):
        """test output for input data with wrong vertical field and correct action field"""
        client = Client()
        response = client.post(
            reverse('campaigns:event_list', kwargs={"version": "v1"}),
            {
                'user_id': str(uuid.uuid4()),
                'vertical': 'WRONG VERTICAL',
                'action': 'watch a video',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_displaced_data(self):
        """test output with displaced input data"""
        client = Client()
        response = client.post(
            reverse('campaigns:event_list', kwargs={"version": "v1"}),
            {
                'user_id': str(uuid.uuid4()),
                'vertical': 'sports',
                'action': 'comment',
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("eagle_eyes.apps.campaigns.views.get_streamer")
    def test_valid_parameter_types(self, streamer_patch):
        response = self.client.post(
            reverse('campaigns:event_list', kwargs={"version": "v1"}),
            {
                'user_id': str(uuid.uuid4()),
                'vertical': 'media',
                'action': 'comment',
                'params': json.dumps({
                    'param1': 10,
                    'param2': 'Milad',
                    'param3': 12.5,
                })
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch("eagle_eyes.apps.campaigns.views.get_streamer")
    def test_invalid_parameter_types(self, streamer_patch):
        response = self.client.post(
            reverse('campaigns:event_list', kwargs={"version": "v1"}),
            {
                'user_id': str(uuid.uuid4()),
                'vertical': 'media',
                'action': 'comment',
                'params': json.dumps({
                    'param1': 'invalid_integer',
                    'param2': 'Milad',
                    'param3': 12.5,
                })
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProcessEventTestCase(TestCase):
    @patch('eagle_eyes.apps.campaigns.models.Campaign.image', new_callable=str)
    def setUp(self, mock_image) -> None:
        # Create sample vertical, actions, campaign, RewardCriteria and events
        ava_vertical = Vertical.objects.create(name='ava')

        self.query_action = Action.objects.create(title="query", vertical=ava_vertical)
        self.play_music_action = Action.objects.create(title="play_music", vertical=ava_vertical)
        self.like_action = Action.objects.create(title="like", vertical=ava_vertical)
        self.comment_action = Action.objects.create(title="comment", vertical=ava_vertical)

        self.yalda_campaign = Campaign.objects.create(
            title='Yalda',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=1),
            image='',
        )

        self.stage0 = Stage.objects.create(
            campaign=self.yalda_campaign,
            index=0
        )

        self.rc1 = RewardCriteria.objects.create(
            stage=self.stage0,
            action=self.query_action,
            value=1
        )
        self.rc1_key = str(self.rc1.pk)
        self.rc2 = RewardCriteria.objects.create(
            stage=self.stage0,
            action=self.play_music_action,
            value=3
        )
        self.rc2_key = str(self.rc2.pk)
        self.rc3 = RewardCriteria.objects.create(
            stage=self.stage0,
            action=self.like_action,
            value=1
        )
        self.rc3_key = str(self.rc3.pk)
        self.rc4 = RewardCriteria.objects.create(
            stage=self.stage0,
            action=self.comment_action,
            value=1
        )
        self.rc4_key = str(self.rc4.pk)

    def test_process_events(self):
        user_id = str(uuid.uuid4())
        event_1 = Event(user=user_id, action=self.query_action, date_time=timezone.now())
        process_event(event_1)
        campaign_state = CampaignState.objects.get(campaign=self.yalda_campaign, user_id=user_id)
        self.assertFalse(campaign_state.done)
        self.assertEqual(campaign_state.started, event_1.date_time)
        self.assertIsNone(campaign_state.finished)
        self.assertIsNone(campaign_state.duration)
        self.assertTrue(campaign_state.state["stages"][0]['criteria'][self.rc1_key]["done"])
        self.assertEqual(
            campaign_state.state["stages"][0]['criteria'][self.rc1_key]["started"],
            event_1.date_time.isoformat()
        )
        self.assertEqual(
            campaign_state.state["stages"][0]['criteria']
            [self.rc1_key]["finished"], event_1.date_time.isoformat()
        )
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc1_key]["duration_seconds"], 0)
        event_2 = Event(user=user_id, action=self.play_music_action, date_time=timezone.now())
        process_event(event_2)
        event_3 = Event(user=user_id, action=self.play_music_action, date_time=timezone.now())
        process_event(event_3)
        event_4 = Event(user=user_id, action=self.play_music_action, date_time=timezone.now())
        process_event(event_4)
        campaign_state = CampaignState.objects.get(campaign=self.yalda_campaign, user_id=user_id)
        self.assertFalse(campaign_state.done)
        self.assertEqual(campaign_state.started, event_1.date_time)
        self.assertIsNone(campaign_state.finished)
        self.assertIsNone(campaign_state.duration)
        self.assertTrue(campaign_state.state["stages"][0]['criteria'][self.rc2_key]["done"])
        self.assertEqual(
            campaign_state.state["stages"][0]['criteria'][self.rc2_key]["started"],
            event_2.date_time.isoformat())
        self.assertEqual(
            campaign_state.state["stages"][0]['criteria'][self.rc2_key]["finished"],
            event_4.date_time.isoformat())
        self.assertEqual(
            campaign_state.state["stages"][0]['criteria'][self.rc2_key]["duration_seconds"],
            (event_4.date_time - event_2.date_time).seconds
        )
        event_5 = Event(user=user_id, action=self.like_action, date_time=timezone.now())
        process_event(event_5)
        event_6 = Event(user=user_id, action=self.comment_action, date_time=timezone.now())
        process_event(event_6)
        campaign_state = CampaignState.objects.get(campaign=self.yalda_campaign, user_id=user_id)
        self.assertTrue(campaign_state.done)
        self.assertEqual(campaign_state.started, event_1.date_time)
        self.assertEqual(campaign_state.finished, event_6.date_time)
        self.assertEqual(campaign_state.duration, event_6.date_time - event_1.date_time)


class ActionParamsTest(TestCase):

    def setUp(self):
        self.vertical_media = Vertical.objects.create(name='media')

        self.action_watch = Action.objects.create(
            title='watch a video',
            vertical=self.vertical_media
        )
        ActionParameter.objects.create(
            action=self.action_watch,
            key='duration',
            value_type=ActionParameter.ParamValueType.FLOAT
        )

        self.campaign_norooz = Campaign.objects.create(
            title='Norooz',
            description='Some description about Norooz campaign',
            start_date=timezone.now(),
            end_date=timezone.now()+timedelta(days=10),
            image='',
        )

        self.stage0 = Stage.objects.create(
            campaign=self.campaign_norooz,
            index=0
        )

        self.rc1 = RewardCriteria.objects.create(
            stage=self.stage0,
            action=self.action_watch,
            param='duration',
            value=20
        )
        self.rc1_key = str(self.rc1.pk)

        self.rc2 = RewardCriteria.objects.create(
            stage=self.stage0,
            action=self.action_watch,
            value=2
        )
        self.rc2_key = str(self.rc2.pk)

        self.rc3 = RewardCriteria.objects.create(
            stage=self.stage0,
            action=self.action_watch,
            value=5
        )
        self.rc3_key = str(self.rc3.pk)

    def test_params(self):
        """Test some scenarios for action parameters"""

        user_id = str(uuid.uuid4())

        # duration parameter is not set, so we just count the event
        event1 = Event.objects.create(
            user=user_id,
            action=self.action_watch,
            params={},
            date_time=timezone.now()
        )
        # duration parameter is set to a numeric value, so its value must be summed
        event2 = Event.objects.create(
            user=user_id,
            action=self.action_watch,
            params={'duration': 14.5},
            date_time=timezone.now()
        )
        # duration parameter is set to a numeric value, so its value must bu summed
        event3 = Event.objects.create(
            user=user_id,
            action=self.action_watch,
            params={'duration': 15.5},
            date_time=timezone.now()
        )
        # duration parameter is set to a non-numeric value, so we just count the event
        event4 = Event.objects.create(
            user=user_id,
            action=self.action_watch,
            params={
                'movie_uuid': 'd8f50f07-276c-4586-ac0f-0fae58ec9471'
            },
            date_time=timezone.now()
        )

        process_event(event1)

        campaign_state = CampaignState.objects.get(
            campaign=self.campaign_norooz,
            user_id=user_id
        )

        self.assertEqual(campaign_state.done, False)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc1_key]['done'], False)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc2_key]['done'], False)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc3_key]['done'], False)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc1_key]['user_value'], 0)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc2_key]['user_value'], 1)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc3_key]['user_value'], 1)

        process_event(event2)

        campaign_state = CampaignState.objects.get(
            campaign=self.campaign_norooz,
            user_id=user_id
        )

        self.assertEqual(campaign_state.done, False)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc1_key]['done'], False)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc2_key]['done'], True)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc3_key]['done'], False)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc1_key]['user_value'], 14.5)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc2_key]['user_value'], 2)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc3_key]['user_value'], 2)

        process_event(event3)

        campaign_state = CampaignState.objects.get(
            campaign=self.campaign_norooz,
            user_id=user_id
        )

        self.assertEqual(campaign_state.done, False)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc1_key]['done'], True)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc2_key]['done'], True)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc3_key]['done'], False)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc1_key]['user_value'], 30)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc2_key]['user_value'], 2)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc3_key]['user_value'], 3)

        process_event(event4)
        process_event(event4)

        campaign_state = CampaignState.objects.get(
            campaign=self.campaign_norooz,
            user_id=user_id
        )

        self.assertEqual(campaign_state.done, True)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc1_key]['done'], True)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc2_key]['done'], True)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc3_key]['done'], True)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc1_key]['user_value'], 30)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc2_key]['user_value'], 2)
        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc3_key]['user_value'], 5)


class StageTest(TestCase):

    @patch('eagle_eyes.apps.campaigns.models.Campaign.image', new_callable=str)
    def setUp(self, mock_image):
        # create a vertical
        self.vertical = Vertical.objects.create(
            name='media'
        )

        # create two actions for the vertical
        self.watch = Action.objects.create(
            title='watch',
            vertical=self.vertical
        )
        ActionParameter.objects.create(
            action=self.watch,
            key='duration',
            value_type=ActionParameter.ParamValueType.FLOAT
        )

        self.comment = Action.objects.create(
            title='comment',
            vertical=self.vertical
        )

        self.norooz = Campaign.objects.create(
            title='Norooz',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=10),
            image='',
        )

        self.stage0_norooz = Stage.objects.create(
            campaign=self.norooz,
            index=0,
            delay=timedelta(days=1)
        )

        self.rc1_norooz = RewardCriteria.objects.create(
            stage=self.stage0_norooz,
            action=self.watch,
            param='duration',
            value=30
        )
        self.rc1_norooz_key = str(self.rc1_norooz.pk)

        self.stage1_norooz = Stage.objects.create(
            campaign=self.norooz,
            index=1
        )

        self.rc2_norooz = RewardCriteria.objects.create(
            stage=self.stage1_norooz,
            action=self.comment,
            value=2
        )
        self.rc2_norooz_key = str(self.rc2_norooz.pk)

    def test_stage_delay_days(self):
        """ Test if delay days for stage works """

        user_id = user_id = str(uuid.uuid4())

        event1 = Event.objects.create(
            user=user_id,
            action=self.watch,
            params={'duration': 40},
            date_time=timezone.now()
        )
        process_event(event1)

        event2 = Event.objects.create(
            user=user_id,
            action=self.comment,
            params={},
            date_time=timezone.now()
        )
        process_event(event2)

        campaign_state = CampaignState.objects.get(
            campaign=self.norooz,
            user_id=user_id
        )

        self.assertEqual(campaign_state.state["stages"][0]['criteria'][self.rc1_norooz_key]['user_value'], 40)
        self.assertIsNotNone(campaign_state.state["stages"][0]['criteria'][self.rc1_norooz_key]['finished'])
        self.assertEqual(campaign_state.state["stages"][1]['criteria'][self.rc2_norooz_key]['user_value'], 0)

        event3 = Event.objects.create(
            user=user_id,
            action=self.comment,
            params={},
            date_time=parse_datetime(campaign_state.state['stages'][0]['finished']) + timedelta(days=1, seconds=1)
        )

        process_event(event3)

        campaign_state = CampaignState.objects.get(
            campaign=self.norooz,
            user_id=user_id
        )

        self.assertEqual(campaign_state.state["stages"][1]['criteria'][self.rc2_norooz_key]['user_value'], 1)


class WinChanceTest(TestCase):
    @patch('eagle_eyes.apps.campaigns.models.Campaign.image', new_callable=str)
    @patch('eagle_eyes.apps.campaigns.models.CampaignCheckpoint.image', new_callable=str)
    def setUp(self, mock_image, mock_ch_image) -> None:
        media = Vertical.objects.create(name='media')
        like_media = Action.objects.create(title='like', vertical=media)
        comment_media = Action.objects.create(title='comment', vertical=media)
        scroll_media = Action.objects.create(title='scroll', vertical=media)

        norooz = Campaign.objects.create(
            title='Norooz',
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1, minutes=20),
            image='',
        )

        # first stage
        stage1 = Stage.objects.create(
            campaign=norooz,
            title='s1',
            index=0,
            delay=timedelta(days=1)
        )
        RewardCriteria.objects.create(
            stage=stage1,
            action=like_media,
            value=2,
            title='title'
        )
        RewardCriteria.objects.create(
            stage=stage1,
            action=comment_media,
            value=2,
            title='title'
        )

        # second stage
        stage2 = Stage.objects.create(
            campaign=norooz,
            title='s2',
            index=1,
            delay=timedelta(days=1)
        )
        RewardCriteria.objects.create(
            stage=stage2,
            action=like_media,
            value=2,
            title='title'
        )
        RewardCriteria.objects.create(
            stage=stage2,
            action=comment_media,
            value=2,
            title='title'
        )
        RewardCriteria.objects.create(
            stage=stage2,
            action=scroll_media,
            value=2,
            title='title'
        )

        # third stage
        stage3 = Stage.objects.create(
            campaign=norooz,
            title='s3',
            index=2,
            delay=timedelta(days=1)
        )
        RewardCriteria.objects.create(
            stage=stage3,
            action=like_media,
            value=2,
            title='title'
        )
        RewardCriteria.objects.create(
            stage=stage3,
            action=comment_media,
            value=2,
            title='title'
        )

        # forth stage
        stage4 = Stage.objects.create(
            campaign=norooz,
            title='s4',
            index=3,
            delay=timedelta(days=1)
        )
        RewardCriteria.objects.create(
            stage=stage4,
            action=like_media,
            value=2,
            title='title'
        )
        RewardCriteria.objects.create(
            stage=stage4,
            action=comment_media,
            value=2,
            title='title'
        )
        RewardCriteria.objects.create(
            stage=stage4,
            action=scroll_media,
            value=2,
            title='title'
        )

        CampaignCheckpoint.objects.create(
            campaign=norooz,
            image='',
            text_done='done text',
            text_undone='undone text',
            percentage=70
        )
        CampaignCheckpoint.objects.create(
            campaign=norooz,
            image='',
            text_done='done text',
            text_undone='undone text',
            percentage=90
        )
        self.late_first_stage_done_user = str(uuid.uuid4())
        cs1 = CampaignStateService.get_or_create(
            user_id=self.late_first_stage_done_user,
            campaign=norooz
        )
        cs1.state['stages'][0]['done'] = True
        cs1.state['stages'][0]['finished'] = timezone.now().isoformat()
        cs1.save()

        self.not_late_first_stage_done_user = str(uuid.uuid4())
        cs2 = CampaignStateService.get_or_create(
            user_id=self.not_late_first_stage_done_user,
            campaign=norooz
        )
        cs2.state['stages'][0]['done'] = True
        cs2.state['stages'][0]['finished'] = (timezone.now() - timedelta(days=1)).isoformat()
        cs2.save()

        self.all_done_user = str((uuid.uuid4))
        cs3 = CampaignStateService.get_or_create(
            user_id=self.all_done_user,
            campaign=norooz
        )
        for stage in cs3.state['stages']:
            stage['done'] = True
            stage['finished'] = timezone.now().isoformat()
        cs3.save()

    def test_new_user(self):
        url = reverse(
            'campaigns:campaign_state_list',
            kwargs={'version': 'v1'}
        )
        headers = {'user_id': str(uuid.uuid4())}
        response = self.client.get(url, headers=headers)
        data = response.json()
        self.assertEqual(data[0]['has_win_chance'], False)

    def test_late_first_stage_done_user(self):
        url = reverse(
            'campaigns:campaign_state_list',
            kwargs={'version': 'v1'}
        )
        headers = {'X-User-ID': self.late_first_stage_done_user}
        response = self.client.get(url, headers)
        data = response.json()
        self.assertEqual(data[0]['has_win_chance'], False)

    def test_not_late_first_stage_done_user(self):
        url = reverse(
            'campaigns:campaign_state_list',
            kwargs={'version': 'v1'}
        )
        headers = {'X-User-ID': self.not_late_first_stage_done_user}
        response = self.client.get(url, headers=headers)
        data = response.json()
        self.assertEqual(data[0]['has_win_chance'], True)

    def test_all_done_user(self):
        url = reverse(
            'campaigns:campaign_state_list',
            kwargs={'version': 'v1'}
        )
        headers = {'X-User-ID': self.all_done_user}
        response = self.client.get(url, headers=headers)
        data = response.json()
        self.assertEqual(data[0]['has_win_chance'], True)
