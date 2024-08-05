from eagle_eyes.apps.campaigns.models import Event
from eagle_eyes.apps.club.models import Mission, UserState, Config, ActivityHistory

from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
import math


def process_club_event(event: Event):
    mission = Mission.objects.filter(action=event.action, is_active=True).first()
    if not mission:
        return
    user_state, _ = UserState.objects.get_or_create(user_id=event.user)
    today = timezone.make_aware(datetime.combine(event.date_time, datetime.min.time()))
    today_user_xp = ActivityHistory.objects.filter(
        user_id=event.user,
        date_time__gte=today,
        date_time__lte=today + timedelta(days=1)
    ).all().aggregate(Sum('earned_xp'))['earned_xp__sum']
    today_user_xp = 0 if today_user_xp is None else int(today_user_xp)

    daily_limit = int(Config.objects.get(title='Daily XP Limit').value)

    if mission.has_limit and today_user_xp >= daily_limit:
        return

    boosters = mission.boosters.all()
    multiplication_factor = 1
    for booster in boosters:
        if booster.start_date <= event.date_time <= booster.end_date:
            multiplication_factor *= booster.multiplier
    granted_xp = math.ceil(mission.XP * multiplication_factor)
    granted_points = math.ceil(mission.points * multiplication_factor)

    if mission.has_limit:
        if today_user_xp >= daily_limit:
            granted_xp = 0
            granted_points = 0
        if today_user_xp + granted_xp > daily_limit:
            granted_xp = daily_limit - today_user_xp

    user_state.XP += granted_xp
    user_state.points += granted_points

    ActivityHistory.objects.create(
        user_id=event.user,
        mission_id=mission.pk,
        vertical=event.action.vertical.name,
        action=event.action.title,
        earned_xp=granted_xp,
        earned_points=granted_points,
        date_time=event.date_time
    )
    user_state.save()
