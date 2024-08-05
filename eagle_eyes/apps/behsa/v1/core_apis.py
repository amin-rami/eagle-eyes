import enum
import json

import requests
from requests import RequestException
from urllib3.exceptions import ReadTimeoutError

from eagle_eyes import settings
from ..utils.request_connection import RequestConnection

BASE_URL = "https://Myliteprodtestsec2.mci.ir"
USERAGENT = "ZAREBIN"
behsa_urls = {
    "login": f"{BASE_URL}/auth/login2",
    "logout": f"{BASE_URL}/auth/logout",
    "verifyOtp": f"{BASE_URL}/auth/verify_otp",
    "salt": f"{BASE_URL}/auth/salt",
    "activation": f"{BASE_URL}/api/Zarebin/activation6",
    "currentState": f"{BASE_URL}/api/Zarebin/currentState5",
    "verify_current_status": f"{BASE_URL}/api/Zarebin/verifyCurrentStatus3",
    "history": f"{BASE_URL}/api/Zarebin/history5",
    "publicToken": f"{BASE_URL}/api/publicToken",
    "chance_inquiry": f"{BASE_URL}/api/chance/inquiry",
    "chance_activation": f"{BASE_URL}/api/chance/activation",
    "chance_inquiryScore": f"{BASE_URL}/api/mci-club/inquiryScore",
    "chance_givingScore": f"{BASE_URL}/api/mci-club/givingScore",
}


# Using enum class create enumerations
class Method(enum.Enum):
    POST = "POST"
    GET = "GET"


class CoreApi:
    def __init__(self) -> None:
        pass

    def send_request(self, method: Method, url, body, headers):
        try:
            if body:
                behsa_response = RequestConnection.get_connection().request(
                    method.value,
                    url,
                    data=json.dumps(
                        body),
                    headers=headers,
                    timeout=settings.BEHSA_API_CALL_TIMEOUT
                )
            else:
                behsa_response = RequestConnection.get_connection().request(
                    method.value,
                    url,
                    headers=headers,
                    timeout=settings.BEHSA_API_CALL_TIMEOUT
                )

            behsa_response_json = behsa_response.json()
            behsa_response_json["status_code"] = behsa_response.status_code
            behsa_response_json["elapsed"] = behsa_response.elapsed.total_seconds()

            if 'message' not in behsa_response_json:
                behsa_response_json['message'] = "OK"

            return behsa_response_json

        except ReadTimeoutError as e:

            return {
                "status_code": 408,
                "message": e.__str__().replace(":", " ").replace("\\", " ").replace("/", " ").replace(".", " ").replace(
                    "*", " "),
                "elapsed": settings.BEHSA_API_CALL_TIMEOUT
            }
        except requests.Timeout as e:
            return {
                "status_code": 408,
                "message": e.__str__().replace(":", " ").replace("\\", " ").replace("/", " ").replace(".", " ").replace(
                    "*", " "),
                "elapsed": settings.BEHSA_API_CALL_TIMEOUT
            }
        except requests.ConnectionError as e:
            return {
                "status_code": 444,
                "message": e.__str__().replace(":", " ").replace("\\", " ").replace("/", " ").replace(".", " ").replace(
                    "*", " "),
                "elapsed": 0
            }

        except RequestException as e:
            return {
                "status_code": 444,
                "message": e.__str__().replace(":", " ").replace("\\", " ").replace("/", " ").replace(".", " ").replace(
                    "*", " "),
                "elapsed": 0
            }
        except Exception as e:
            # capture_exception(e)
            return {
                "status_code": 500,
                "message": e.__str__().replace(":", " ").replace("\\", " ").replace("/", " ").replace(".", " ").replace(
                    "*", " "),
                "elapsed": 0
            }

    def urls(self):
        return behsa_urls

    def __request_behsa_api(self, method: Method, url, body, headers):
        response = self.send_request(method, url, body, headers)
        status_code = 504 if response["status_code"] in (408, 444) else response["status_code"]
        error_message = 'InternalError' if response["status_code"] in (408, 444) else response["message"]
        error_code = str(status_code) + '001'
        error = None if status_code == 200 else {
            "status_code": status_code,
            "error_code": error_code,
            "error_message": error_message
        }
        return response, error

    def login(self, mobile_number, otp_type):
        url = behsa_urls["login"]
        body = {
            "mobileNumber": f"{mobile_number}",
            "otpType": otp_type
        }
        headers = {
            'Content-Type': "application/json",
            'User-Agent': USERAGENT
        }
        return self.__request_behsa_api(Method.POST, url, body, headers)

    def logout(self, auth_token, salt_token):
        url = behsa_urls["logout"]
        headers = {
            'Content-Type': "application/json",
            'User-Agent': USERAGENT,
            'X_AUTH_TOKEN': f"{auth_token}",
            'X_SALT_TOKEN': f"{salt_token}",
        }

        return self.__request_behsa_api(Method.POST, url, None, headers)

    def verify_otp(self, request_id, otp, otp_type):
        url = behsa_urls["verifyOtp"]
        headers = {
            'Content-Type': "application/json",
            'User-Agent': USERAGENT
        }
        body = {
            "key": f"{otp}",
            "requestId": f"{request_id}",
            "otpType": otp_type
        }

        return self.__request_behsa_api(Method.POST, url, body, headers)

    def salt(self, auth_token):
        url = behsa_urls["salt"]
        headers = {
            'Content-Type': "application/json",
            'User-Agent': USERAGENT,
            'X_AUTH_TOKEN': f"{auth_token}"
        }

        return self.__request_behsa_api(Method.GET, url, None, headers)

    def activation(self, auth_token, salt_token):
        url = behsa_urls["activation"]
        headers = {
            'Content-Type': "application/json",
            'User-Agent': USERAGENT,
            'X_AUTH_TOKEN': f"{auth_token}",
            'X_SALT_TOKEN': f"{salt_token}",
        }

        return self.__request_behsa_api(Method.POST, url, None, headers)

    def verify_current_status(self, auth_token, salt_token):
        url = behsa_urls["verify_current_status"]
        headers = {
            'Content-Type': "application/json",
            'User-Agent': USERAGENT,
            'X_AUTH_TOKEN': f"{auth_token}",
            'X_SALT_TOKEN': f"{salt_token}",
        }

        return self.__request_behsa_api(Method.POST, url, None, headers)

    def history(self, auth_token, salt_token, from_date, to_date):
        url = behsa_urls["history"] + f"?startDate={from_date}&endDate={to_date}"
        headers = {
            'Content-Type': "application/json",
            'User-Agent': USERAGENT,
            'X_AUTH_TOKEN': f"{auth_token}",
            'X_SALT_TOKEN': f"{salt_token}",
        }

        return self.__request_behsa_api(Method.POST, url, None, headers)

    def public_token(self, auth_token, salt_token):
        url = behsa_urls["publicToken"]
        headers = {
            'Content-Type': "application/json",
            'X_AUTH_TOKEN': f"{auth_token}",
            'X_SALT_TOKEN': f"{salt_token}",
            'User-Agent': USERAGENT,
            'Accept-Encoding': 'gzip, deflate, br'
        }
        return self.__request_behsa_api(Method.GET, url, None, headers)

    def chance_inquiry(self, auth_token, salt_token):
        url = behsa_urls["chance_inquiry"]
        body = {}
        headers = {
            'Content-Type': "application/json",
            'User-Agent': USERAGENT,
            'X_AUTH_TOKEN': auth_token,
            'X_SALT_TOKEN': salt_token
        }
        return self.__request_behsa_api(Method.POST, url, body, headers)

    def chance_activation(self, auth_token, salt_token, offer_id):
        url = behsa_urls["chance_activation"]
        body = {
            "offerId": offer_id
        }
        headers = {
            'Content-Type': "application/json",
            'User-Agent': USERAGENT,
            'X_AUTH_TOKEN': auth_token,
            'X_SALT_TOKEN': salt_token
        }
        return self.__request_behsa_api(Method.POST, url, body, headers)

    def chance_giving_score(self, auth_token, salt_token, score_id, repeat_flag, register_flag):
        url = behsa_urls["chance_givingScore"]
        body = {
            "scoreId": score_id,
            "repeatFlag": repeat_flag,
            "registerFlag": register_flag
        }
        headers = {
            'Content-Type': "application/json",
            'User-Agent': USERAGENT,
            'X_AUTH_TOKEN': auth_token,
            'X_SALT_TOKEN': salt_token
        }
        return self.__request_behsa_api(Method.POST, url, body, headers)

    def chance_inquiry_score(self, auth_token, salt_token):
        url = behsa_urls["chance_inquiryScore"]
        body = {}
        headers = {
            'Content-Type': "application/json",
            'User-Agent': USERAGENT,
            'X_AUTH_TOKEN': auth_token,
            'X_SALT_TOKEN': salt_token
        }
        return self.__request_behsa_api(Method.POST, url, body, headers)
