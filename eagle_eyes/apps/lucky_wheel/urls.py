from django.urls import path
from eagle_eyes.apps.lucky_wheel import views

urlpatterns = [
    path('slices', views.LuckyWheelList.as_view(), name='get_slices'),
    path('validate', views.Validate.as_view(), name='validate'),
    path('allocate', views.Allocate.as_view(), name='allocate'),
]
