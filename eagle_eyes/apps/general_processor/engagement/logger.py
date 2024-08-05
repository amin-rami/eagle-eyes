import json
from requests import Response
from logging import getLogger
from datetime import datetime


def log_api_call(api: str, resp: Response) -> None:
    logger = getLogger('external_api_calls')
    jd = {
        'logtime': datetime.utcnow().isoformat(),
        'api': api,
        'request': {
            'method': resp.request.method,
            'url': resp.request.url,
            'headers': dict(resp.request.headers),
            'body': json.loads(resp.request.body),
        },
        'response': {
            'status': resp.status_code,
            'headers': dict(resp.headers),
            'body': resp.json()
        }
    }
    logger.info(json.dumps(jd))
