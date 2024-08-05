from django.urls import path
from eagle_eyes.apps.referral_reward import views

urlpatterns = [
    path('validate/', views.Validate.as_view(), name='validate'),
    path('allocate/', views.Allocate.as_view(), name='allocate'),
]
