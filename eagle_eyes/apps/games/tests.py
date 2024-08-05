from django.test import TestCase
from eagle_eyes.apps.campaigns.models import Action, ActionParameter, Event, Vertical
from eagle_eyes.apps.games import services
from django.utils import timezone
from django.urls import reverse
from eagle_eyes.apps.games.management.commands.process_game_events import process_game_event
from eagle_eyes.apps.games.models import UserState
import uuid


class GameServiceTestCase(TestCase):
    def test_get_label(self):
        self.assertEqual(services.get_label(current_level=0), '')
        self.assertEqual(services.get_label(current_level=1), 'آکبند')
        self.assertEqual(services.get_label(current_level=4), 'پیرو')
        self.assertEqual(services.get_label(current_level=40), 'نامدار')
        self.assertEqual(services.get_label(current_level=55), 'پهلوان')
        self.assertEqual(services.get_label(current_level=100), 'اسطوره')
        self.assertEqual(services.get_label(current_level=150), 'اسطوره')

    def test_get_level_total_plays(self):
        self.assertEqual(services.get_level_total_plays(current_level=0), 5)
        self.assertEqual(services.get_level_total_plays(current_level=10), 5)
        self.assertEqual(services.get_level_total_plays(current_level=11), 10)
        self.assertEqual(services.get_level_total_plays(current_level=71), 100)
        self.assertEqual(services.get_level_total_plays(current_level=101), 200)
        self.assertEqual(services.get_level_total_plays(current_level=150), 200)


class GameEventProcessingTest(TestCase):
    def setUp(self):
        vertical = Vertical.objects.create(name="game")
        self.user_id = str(uuid.uuid4())
        action = Action.objects.create(
            title="play_game",
            vertical=vertical
        )
        ActionParameter.objects.create(
            action=action,
            key='game_id',
            value_type=ActionParameter.ParamValueType.INT
        )

        self.event1 = Event.objects.create(
            user=self.user_id,
            action=action,
            params={
                "game_id": 1
            },
            date_time=timezone.now()
        )
        self.event2 = Event.objects.create(
            user=self.user_id,
            action=action,
            params={
                "game_id": 2
            },
            date_time=timezone.now()
        )

    def test_process_game_event(self):
        game1_id = self.event1.params.get("game_id")
        process_game_event(self.event1)
        user_state = UserState.objects.get(user_id=self.user_id)
        self.assertEqual(user_state.game_states.get(f'{game1_id}').get("label"), '')
        self.assertEqual(user_state.game_states.get(f'{game1_id}').get("level"), 0)
        self.assertEqual(user_state.game_states.get(f'{game1_id}').get("played"), 1)
        self.assertEqual(user_state.game_states.get(f'{game1_id}').get("remaining"), 4)
        self.assertEqual(user_state.game_states.get(f'{game1_id}').get("progress"), 0.2)
        for _ in range(4):
            process_game_event(self.event1)
        user_state = UserState.objects.get(user_id=self.user_id)
        self.assertEqual(user_state.game_states.get(f'{game1_id}').get("label"), 'آکبند')
        self.assertEqual(user_state.game_states.get(f'{game1_id}').get("level"), 1)
        self.assertEqual(user_state.game_states.get(f'{game1_id}').get("played"), 0)
        self.assertEqual(user_state.game_states.get(f'{game1_id}').get("remaining"), 5)
        self.assertEqual(user_state.game_states.get(f'{game1_id}').get("progress"), 0)
        game2_id = self.event2.params.get("game_id")
        for _ in range(16):
            process_game_event(self.event2)
        user_state = UserState.objects.get(user_id=self.user_id)
        # Check state of game 1
        self.assertEqual(user_state.game_states.get(f'{game1_id}').get("label"), 'آکبند')
        self.assertEqual(user_state.game_states.get(f'{game1_id}').get("level"), 1)
        self.assertEqual(user_state.game_states.get(f'{game1_id}').get("played"), 0)
        self.assertEqual(user_state.game_states.get(f'{game1_id}').get("remaining"), 5)
        self.assertEqual(user_state.game_states.get(f'{game1_id}').get("progress"), 0)
        # Check state of game 2
        self.assertEqual(user_state.game_states.get(f'{game2_id}').get("label"), 'پیرو')
        self.assertEqual(user_state.game_states.get(f'{game2_id}').get("level"), 3)
        self.assertEqual(user_state.game_states.get(f'{game2_id}').get("played"), 1)
        self.assertEqual(user_state.game_states.get(f'{game2_id}').get("remaining"), 4)
        self.assertEqual(user_state.game_states.get(f'{game2_id}').get("progress"), 0.2)
        # Check global state
        self.assertEqual(user_state.label, "پیرو")
        self.assertEqual(user_state.level, 4)
        self.assertEqual(user_state.played, 21)
        # Test the UserStateList API
        url = reverse('games:user_state_list', kwargs={'version': 'v1'})
        params = {'user_id': self.user_id}
        response = self.client.get(url, params)
        self.assertEqual(response.data["label"], "پیرو")
        self.assertEqual(response.data["level"], 4)
        self.assertEqual(response.data["played"], 21)
