from django.contrib import admin
import nested_admin
from eagle_eyes.apps.general_processor.models import Tracker, EngagementCriteria


class EngagementInline(nested_admin.NestedTabularInline):
    model = EngagementCriteria
    extra = 0


@admin.register(Tracker)
class TrackerAdmin(nested_admin.NestedModelAdmin):
    list_display = (
        "title",
        "start_date",
        "end_date",
    )

    inlines = [EngagementInline]
