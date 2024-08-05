from django.urls import path
from eagle_eyes.apps.games import views

urlpatterns = [
    path('user-states/', views.UserStateList.as_view(), name='user_state_list'),
    path('user-top-ranks/', views.UserTopRanksList.as_view(), name='user_top_ranks_list')
]
