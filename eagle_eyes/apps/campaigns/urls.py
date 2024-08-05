from django.urls import path
from eagle_eyes.apps.campaigns import views

urlpatterns = [
    path('events/', views.EventList.as_view(), name='event_list'),
    path('campaign-states/', views.CampaignStateList.as_view(),
         name='campaign_state_list'),
    path('actions/<int:pk>/', views.ActionDetails.as_view(), name='actions'),
]
