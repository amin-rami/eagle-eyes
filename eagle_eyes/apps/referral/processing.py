from eagle_eyes.apps.referral.models import Referral, ReferralCriteria, ReferralState
from eagle_eyes.apps.campaigns.models import Campaign
from eagle_eyes.apps.referral.services import MutualEventServices
from eagle_eyes.apps.eagleusers.services import UserService


def process_mutual_event(event):
    active_campaigns = (
        Campaign.objects.filter(
            start_date__lte=event.date_time, end_date__gte=event.date_time
        )
        .all()
        .cache()
    )
    referral_criterias = (
        ReferralCriteria.objects.select_related("reward_criteria__action__vertical")
        .all()
        .cache()
    )
    referral_criterias = referral_criterias.filter(
        referee_required_action=event.action,
        reward_criteria__stage__campaign__in=active_campaigns,
    ).all()
    if not referral_criterias:
        return

    referee_phone_number = UserService.phone_number(event.user)
    if referee_phone_number is None:
        return

    referral = Referral.objects.filter(
        referee_phone_number=referee_phone_number, done=True
    ).first()
    if not referral:
        return

    referral_state, _ = ReferralState.objects.get_or_create(referral=referral)
    referral_state.state = {} if referral_state.state is None else referral_state.state
    state = referral_state.state
    for referral_criteria in referral_criterias:
        key = str(referral_criteria.id)
        if key not in state:
            state[key] = {
                "user_value": 0,
                "value": referral_criteria.value,
                "done": False,
            }
        if state[key]["done"]:
            continue
        state[key]["user_value"] += 1
        if state[key]["user_value"] >= state[key]["value"]:
            state[key]["done"] = True
            MutualEventServices.send_mutual_event(
                referral,
                referrer_event={
                    "action": referral_criteria.reward_criteria.action.title,
                    "vertical": referral_criteria.reward_criteria.action.vertical.name,
                },
                referee_event={
                    "action": referral_criteria.referee_rewarded_action.title,
                    "vertical": referral_criteria.referee_rewarded_action.vertical.name,
                },
            )
    referral_state.save()
