import os
import jwt
from sentry_sdk import capture_exception


class UserIDMiddleware:
    def __init__(self, get_response):
        self.get_reponse = get_response

    def __call__(self, request):

        try:
            # do not log if request is not from an api call
            if not request.path.startswith("/api"):
                return self.get_reponse(request)

            if not ("X-Token" in request.headers or "Authorization" in request.headers):
                return self.get_reponse(request)

            token = request.headers.get("X-Token") or request.headers.get("Authorization")
            token = token[7:] if "bearer" in token[:7].lower() else token
            sso_public_key = os.getenv("MAGNIX_SSO_PUBLIC_KEY")
            payload = jwt.decode(token, sso_public_key, algorithms=["RS256"])

            if 'userid' in payload:
                request.META['HTTP_X_USER_ID'] = payload['userid']
            elif 'muid' in payload:
                request.META['HTTP_X_USER_ID'] = payload['muid']

            if 'data' in payload:
                request.META['HTTP_X_DATA'] = payload['data']

            request.__dict__.pop('headers', None)

        except Exception as e:
            capture_exception(e)

        return self.get_reponse(request)
