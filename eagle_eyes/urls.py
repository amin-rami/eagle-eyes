"""eagle_eyes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

admin.site.site_header = 'Eagle Eyes'
admin.site.site_title = 'Eagle Eyes'
admin.site.index_title = 'Welcome to gamification panel'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django_prometheus.urls')),

    re_path(r'^api/(?P<version>(v1))/campaigns/', include(('eagle_eyes.apps.campaigns.urls', 'campaigns'))),
    re_path(r'^api/(?P<version>(v1))/lucky-wheel/', include(('eagle_eyes.apps.lucky_wheel.urls', 'lucky_wheel'))),
    re_path(r'^api/(?P<version>(v1))/games/', include(('eagle_eyes.apps.games.urls', 'games'))),
    re_path(r'^api/(?P<version>(v1))/referral-reward/',
            include(('eagle_eyes.apps.referral_reward.urls', 'referral_reward'))
            ),
    re_path(r'^api/(?P<version>(v1))/referral/', include(('eagle_eyes.apps.referral.urls', 'referral'))),
    re_path(r'^api/(?P<version>(v1))/club/', include(('eagle_eyes.apps.club.urls', 'club'))),

    re_path(r'^api/(?P<version>(v1))/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path(r'^api/(?P<version>(v1))/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    re_path(r'^api/(?P<version>(v1))/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('schema/', SpectacularAPIView.as_view(api_version='v1'), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(), name='swagger-ui'),
    # path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    re_path(r'^_nested_admin/', include('nested_admin.urls')),
]
