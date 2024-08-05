from eagle_eyes.settings.django import METRICS_PREFIX
from prometheus_client import Counter

adtrace_requests = Counter(
    f'{METRICS_PREFIX}_adtrace_requests',
    'Requests sent to adtrace status',
    ['status']
)
