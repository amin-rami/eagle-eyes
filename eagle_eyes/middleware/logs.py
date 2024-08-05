import logging
import json
from django.utils import timezone
from sentry_sdk import capture_exception


class RequestResponseLogMiddleware:
    def __init__(self, get_response):
        self.get_reponse = get_response
        self.logger = logging.getLogger('requests_responses')
        self.logger.setLevel(logging.INFO)

    def __call__(self, request):
        try:
            # do not log if request is not from an api call
            if not request.path.startswith("/api"):
                return self.get_reponse(request)
            # a flag to indicate if self.get_reponse(request) has been called
            is_request_processed = False
            # a flag to indicate if the logging process has been successful
            is_successful = True

            raw_body = request.body.decode()
            try:
                body_data = json.loads(raw_body) if raw_body != "" else {}
            except Exception as e:
                body_data = {
                    "middleware_message": "could not convert body to JSON",
                    "raw_body": raw_body
                }
                is_successful = False
                capture_exception(e)

            request_log = {
                "method": request.method,
                "path": request.path,
                "query_params": request.GET,
                "headers": dict(request.headers),
                "body": body_data
            }

            response = self.get_reponse(request)
            is_request_processed = True
            raw_body = response.content.decode()
            try:
                body_data = json.loads(raw_body) if raw_body != "" else {}
            except Exception as e:
                body_data = {
                    "middleware_message": "could not convert body to JSON",
                    "raw_body": raw_body
                }
                is_successful = False
                capture_exception(e)

            response_log = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": body_data,
            }

            log = self.create_log_template(
                is_successful=is_successful,
                request=request_log,
                response=response_log,
            )
        except Exception as e:
            log = self.create_log_template(
                is_successful=False,
                middleware_message=str(e),
            )
            if not is_request_processed:
                response = self.get_reponse(request)
            capture_exception(e)

        self.logger.info(log)
        return response

    def create_log_template(self, is_successful, **data):
        return json.dumps({
            "log_status": "success" if is_successful else "failed",
            "logtime": timezone.now().isoformat(),
            **data
        })
