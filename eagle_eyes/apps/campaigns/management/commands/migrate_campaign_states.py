from django.utils import timezone
from django.core.management.base import BaseCommand
from eagle_eyes.apps.campaigns.models import Campaign


def generate_state_template(campaign):
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


def migrate_campaign_states(campaign: Campaign):
    campaign_template = generate_state_template(campaign)
    for campaign_state_index, campaign_state in enumerate(campaign.states.all()):
        print(
            f"Updating CampaignState for campaign: {campaign_state.campaign_id}, " +
            f"user: {campaign_state.user_id}, Index: {campaign_state_index}"
        )
        old_state = campaign_state.state
        new_state = campaign_template
        for index, stage in enumerate(new_state["stages"]):
            new_state["stages"][index]['done'] = old_state['stages'][stage['index']]['done']
            new_state["stages"][index]['started'] = old_state['stages'][stage['index']]['started']
            new_state["stages"][index]['finished'] = old_state['stages'][stage['index']]['finished']
            new_state["stages"][index]['duration_seconds'] = old_state['stages'][stage['index']]['duration_seconds']

            old_stage = campaign_state.campaign.stages.get(index=stage['index'])
            for criteria in old_stage.reward_criterias.all().select_related('action__vertical'):
                criteria_key = f'{criteria.action.title}-{criteria.action.vertical.name}'
                new_state["stages"][index]['criteria'][str(criteria.id)]['user_value'] = \
                    old_state['stages'][old_stage.index]['criteria'][criteria_key]['user_value']
                new_state["stages"][index]['criteria'][str(criteria.id)]['done'] = \
                    old_state['stages'][old_stage.index]['criteria'][criteria_key]['done']
                new_state["stages"][index]['criteria'][str(criteria.id)]['started'] = \
                    old_state['stages'][old_stage.index]['criteria'][criteria_key]['started']
                new_state["stages"][index]['criteria'][str(criteria.id)]['finished'] = \
                    old_state['stages'][old_stage.index]['criteria'][criteria_key]['finished']
                new_state["stages"][index]['criteria'][str(criteria.id)]['duration_seconds'] = \
                    old_state['stages'][old_stage.index]['criteria'][criteria_key]['duration_seconds']
        campaign_state.state = new_state
        campaign_state.save()


class Command(BaseCommand):
    help = 'Decrypt user id list'

    def add_arguments(self, parser):
        parser.add_argument('campaign_id', type=int)

    def handle(self, *args, **kwargs):
        campaign: Campaign = Campaign.objects.get(pk=kwargs["campaign_id"])
        migrate_campaign_states(campaign)
        # Set a default delay value for stages of the campaign
        campaign.stages.filter(delay__isnull=True).update(delay=timezone.timedelta(days=0))
