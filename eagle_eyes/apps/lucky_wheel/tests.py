from datetime import timedelta, datetime, date
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from eagle_eyes.apps.campaigns.models import Campaign
from eagle_eyes.apps.lucky_wheel.models import LuckyWheel, UserReward
from eagle_eyes.apps.lucky_wheel.services import UserDetail, PhoneDetail


class LuckyWheelListTestCase(TestCase):

    @patch('eagle_eyes.apps.lucky_wheel.models.LuckyWheel.slice_image', new_callable=str)
    def setUp(self, mocked_imagefield):
        campaign = Campaign.objects.create(
            title='Campaign title',
            description='Campaign description',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=19),
        )
        LuckyWheel.objects.create(
            campaign=campaign,
            title='Slices title1',
            slice_image='',
            behsa_offer_id='1',
            client_index='1',
            chance=1.5,
            limit=1,
            after_spin_title='Sample after spin title',
            after_spin_description='Sample after spin description',
            active=True,
        )
        LuckyWheel.objects.create(
            campaign=campaign,
            title='Slices title2',
            slice_image='',
            behsa_offer_id='2',
            client_index='2',
            chance=1.5,
            limit=1,
            after_spin_title='Sample after spin title',
            after_spin_description='Sample after spin description',
            active=True,
        )
        LuckyWheel.objects.create(
            campaign=campaign,
            title='Slices title3',
            slice_image='',
            behsa_offer_id='3',
            client_index='3',
            chance=1.5,
            limit=1,
            after_spin_title='Sample after spin title',
            after_spin_description='Sample after spin description',
            active=True,
        )

    @patch('eagle_eyes.apps.lucky_wheel.serializers.LuckyWheelSerializer.get_image_path')
    def test_get_functionality(self, get_image_path_mock):
        get_image_path_mock.return_value = '/some-bucket/some-image.jpg'
        campaign_id = Campaign.objects.all()[0].pk

        client = Client()
        response = client.get(
            path=reverse('lucky_wheel:get_slices', kwargs={"version": "v1"}),
            data={'campaign_id': campaign_id}
        )
        data = response.json()[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['campaign'], campaign_id)
        self.assertEqual(data['title'], 'Slices title1')
        self.assertEqual(data['client_index'], 1)
        self.assertEqual(data['after_spin_title'], 'Sample after spin title')
        self.assertEqual(data['after_spin_description'], 'Sample after spin description')


class ValidateTestCase(TestCase):
    @patch('eagle_eyes.apps.lucky_wheel.models.LuckyWheel.slice_image', new_callable=str)
    def setUp(self, mocked_obj1):
        campaign1 = Campaign.objects.create(
            title="title1",
            description="descrption1",
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=5),
        )
        slice1 = LuckyWheel.objects.create(
            campaign=campaign1,
            title='Slices title1',
            slice_image='',
            behsa_offer_id='1',
            client_index='1',
            chance=1.5,
            limit=1,
            after_spin_title='Sample after spin title',
            after_spin_description='Sample after spin description',
            active=True,
        )
        UserReward.objects.create(
            user_id="already_won_user",
            slice=slice1,
            date_time=timezone.now(),
        )

    @staticmethod
    def mocked_chance_inquiry(*args, **kwargs):
        return {'data': {'packageInfo': {'ACTIVE_DATE': "1400/1/1"}}}

    @staticmethod
    def mocked_validate(*args, **kwargs):
        return UserDetail(
            phone_detail=PhoneDetail(
                number="9903997745",
                is_mci=True
                ),
            salt_token="salt_token",
            )

    @staticmethod
    def mocking_function(*args, **kwargs):
        return None

    def test_already_won_user(self):
        campaign1 = Campaign.objects.all()[0]
        client = Client()
        response = client.post(
            path=reverse('lucky_wheel:validate', kwargs={"version": "v1"}),
            data={'campaign_id': campaign1.pk,
                  "user_id": "already_won_user",
                  "phone_number": "9903997745"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('eagle_eyes.apps.behsa.v1.behsa_apis.BehsaApi.chance_inquiry', mocked_chance_inquiry)
    @patch('eagle_eyes.apps.lucky_wheel.services.LuckyWheelService.behsa_validate', mocked_validate)
    @patch('eagle_eyes.utils.Persian.gregorian_string', lambda x: str(date.today()))
    def test_has_active_reward(self):
        campaign1 = Campaign.objects.all()[0]
        client = Client()
        response = client.post(
            path=reverse('lucky_wheel:validate', kwargs={"version": "v1"}),
            data={'campaign_id': campaign1.pk,
                  "user_id": "has_active_reward_user",
                  "phone_number": "9903997745"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('eagle_eyes.apps.behsa.v1.behsa_apis.BehsaApi.chance_inquiry', mocked_chance_inquiry)
    @patch('eagle_eyes.apps.lucky_wheel.services.LuckyWheelService.behsa_validate', mocked_validate)
    @patch('eagle_eyes.utils.Persian.gregorian_string', lambda x: str((datetime.now() - timedelta(days=3)).date()))
    @patch('django.core.cache.cache.set', mocking_function)
    @patch('eagle_eyes.apps.lucky_wheel.services.LuckyWheelService.validate_user_campaign', mocking_function)
    def test_ok_user(self):
        campaign1 = Campaign.objects.all()[0]
        client = Client()
        response = client.post(
            path=reverse('lucky_wheel:validate', kwargs={"version": "v1"}),
            data={'campaign_id': campaign1.pk,
                  "user_id": "OK_User",
                  "phone_number": "9903997745"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['salt_token'], 'salt_token')


class AllocateTestCase(TestCase):
    def setUp(self):
        campaign1 = Campaign.objects.create(
            title="title1",
            description="descrption1",
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=5),
        )
        LuckyWheel.objects.create(
            campaign=campaign1,
            title='Slices title1',
            slice_image='',
            behsa_offer_id='1',
            client_index='1',
            chance=1.5,
            limit=1,
            after_spin_title='Sample after spin title',
            after_spin_description='Sample after spin description',
            active=True,
        )
        LuckyWheel.objects.create(
            campaign=campaign1,
            title='Slices title2',
            slice_image='',
            behsa_offer_id='2',
            client_index='2',
            chance=1.5,
            limit=1,
            after_spin_title='Sample after spin title',
            after_spin_description='Sample after spin description',
            active=True,
        )
        LuckyWheel.objects.create(
            campaign=campaign1,
            title='Slices title3',
            slice_image='',
            behsa_offer_id='3',
            client_index='3',
            chance=1.5,
            limit=1,
            after_spin_title='Sample after spin title',
            after_spin_description='Sample after spin description',
            active=True,
        )
        self.cache_dict = {}

    @staticmethod
    def get_or_update_cache_value(key, value=None, cache_dict={}, **kwargs):
        if value is None:
            return cache_dict[key]
        cache_dict[key] = value

    @staticmethod
    def mocked_behsa_validate(*args, **kwargs):
        return UserDetail(
            salt_token='salt_token',
            phone_detail=PhoneDetail(
                number='9915022215',
                is_mci=True,
            ),
        )

    @staticmethod
    def mocking_function(*args, **kwargs):
        return None

    def test_invalid_token(self):
        campaign = Campaign.objects.all()[0]
        client = Client()
        response = client.get(
            path=reverse('lucky_wheel:allocate', kwargs={"version": "v1"}),
            data={'campaign_id': campaign.pk, 'user_id': 'invalid_token_id'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('eagle_eyes.apps.lucky_wheel.serializers.LuckyWheelSerializer.get_image_path')
    @patch('eagle_eyes.apps.lucky_wheel.services.LuckyWheelService.behsa_validate', mocked_behsa_validate)
    @patch('eagle_eyes.apps.lucky_wheel.services.LuckyWheelService.check_active_rewards', mocking_function)
    @patch('django.core.cache.cache.set', get_or_update_cache_value)
    @patch('django.core.cache.cache.get', get_or_update_cache_value)
    @patch('django.core.cache.cache.delete', mocking_function)
    @patch('eagle_eyes.apps.behsa.v1.behsa_apis.BehsaApi.chance_activation', mocking_function)
    @patch('eagle_eyes.apps.lucky_wheel.services.LuckyWheelService.validate_user_campaign', mocking_function)
    def test_ok_user(self, get_image_path_mock):
        get_image_path_mock.return_value = '/some-bucket/some-image.jpg'
        campaign = Campaign.objects.all()[0]
        user_id = "ok_user"

        client = Client()
        response = client.post(
            path=reverse('lucky_wheel:validate', kwargs={"version": "v1"}),
            data={'campaign_id': campaign.pk,
                  'user_id': user_id,
                  'phone_number': '9915022215'}
        )

        data = response.json()
        response = client.get(
            path=reverse('lucky_wheel:allocate', kwargs={"version": "v1"}),
            data={'campaign_id': campaign.pk, 'user_id': user_id},
            HTTP_AUTHORIZATION=data['val_token']
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
