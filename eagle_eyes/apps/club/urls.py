from django.urls import path
from eagle_eyes.apps.club import views

urlpatterns = [
    path('user-states/', views.UserStateList.as_view(), name='user_states'),
]
