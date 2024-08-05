import os
import sys
from datetime import timedelta
from typing import Any, Dict

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# sentry
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    send_default_pii=True,
    attach_stacktrace=True,
    request_bodies="always",
    with_locals=True,
    environment=os.getenv('ENVIRONMENT', "dev"),
    release="1.0.0",
    server_name="Eagle Eyes",
    traces_sample_rate=0.1,
)

# SIMPLE_JWT
JWT_SIGNING_KEY = os.getenv('JWT_SIGNING_KEY')
JWT_VERIFYING_KEY = os.getenv('JWT_VERIFYING_KEY')
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),

    'ALGORITHM': 'RS256',
    'SIGNING_KEY': JWT_SIGNING_KEY,
    'VERIFYING_KEY': JWT_VERIFYING_KEY
}

# drf-spectacular
SPECTACULAR_SETTINGS: Dict[str, Any] = {
    'SCHEMA_PATH_PREFIX': '/api/v[0-9]',

    'TITLE': 'Eagle Eyes API Docs',
    'DESCRIPTION': '',

    'VERSION': '1.22.0',
}

if 'gunicorn' in sys.argv[0]:
    PROMETHEUS_METRICS_EXPORT_PORT_RANGE = range(8001, 8050)

BEHSA_API_CALL_TIMEOUT = os.getenv('BEHSA_API_CALL_TIMEOUT', 20)
BEHSA_PROXY = os.getenv('BEHSA_PROXY')
CORS_ALLOW_ALL_ORIGINS = True
# TODO add allow origin whitelist

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
CACHEOPS_REDIS_DB = os.getenv("CACHEOPS_REDIS_DB", "5")
CACHEOPS_REDIS = {
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'db': CACHEOPS_REDIS_DB,
    # connection timeout in seconds
    'socket_timeout': 3,
    'password': REDIS_PASSWORD
}
CACHEOPS_DEGRADE_ON_FAILURE = True
CACHEOPS_CONFIG = {
    'ops': 'all',
    'cache_on_save': True,
    'timeout': os.getenv("CACHEOPS_TIMEOUT", 60 * 60)
    }
CACHEOPS = {
    'campaigns.vertical': CACHEOPS_CONFIG,
    'campaigns.action': CACHEOPS_CONFIG,
    'campaigns.campaign': CACHEOPS_CONFIG,
    'campaigns.campaigncheckpoint': CACHEOPS_CONFIG,
    'campaigns.stage': CACHEOPS_CONFIG,
    'campaigns.rewardcriteria': CACHEOPS_CONFIG,
    'referral_reward.reward': CACHEOPS_CONFIG,
    'eagleusers.config': CACHEOPS_CONFIG,
    'eagleusers.notray': CACHEOPS_CONFIG,
    'referral.referralcriteria': CACHEOPS_CONFIG,
    'general_processor.tracker': CACHEOPS_CONFIG,
    'general_processor.engagementcriteria': CACHEOPS_CONFIG,
}
