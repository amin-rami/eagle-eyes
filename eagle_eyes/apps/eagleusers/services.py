import os
import jwt
import json
import requests
import re
from rest_framework import exceptions
from eagle_eyes.apps.eagleusers.models import Config, Notary
from eagle_eyes.apps.referral.exceptions import InvalidPhoneNumber
from sentry_sdk import capture_exception
import logging


BW2_BASE_URL = os.getenv("BW2_BASE_URL")
BW2_API_KEY = os.getenv("BW2_API_KEY")
BW3_BASE_URL = os.getenv("BW3_BASE_URL")
BW3_TOKEN = os.getenv("BW3_TOKEN")


class UserService:
    @staticmethod
    def extract_user_id(request) -> str:
        return request.headers.get("x-user-id")

    @staticmethod
    def extract_auth_phone_number(auth_token):
        try:
            return jwt.decode(
                auth_token, options={"verify_signature": False}, algorithms=["HS256"]
            )["userIdentity"]
        except Exception:
            raise exceptions.InvalidToken()

    @staticmethod
    def phone_number(user_id: str) -> dict:
        try:
            return Notary.objects.filter(user_id=user_id).first().phone_number
        except Exception:
            pass
        try:
            url = f"{BW3_BASE_URL}/profile/userinfo"
            headers = {
                    "X-User-ID": user_id,
                    "Authorization": f"Bearer {BW3_TOKEN}",
                    "Content-Type": "application/json",
                }
            resp = requests.get(url, headers=headers)
            LoggingService.log(
                context='phone_number',
                browser='BW3',
                request_headers=headers,
                status_code=resp.status_code,
                response_data=resp.json()
            )
        except Exception as e:
            capture_exception(e)

        if resp.status_code == 200 and "phoneNumber" in resp.json():
            phone_number = UserService.format_phone_number(resp.json()["phoneNumber"])
            Notary.objects.update_or_create(user_id=user_id, defaults={"phone_number": phone_number})
            return phone_number
        try:
            url = f"{BW2_BASE_URL}/profiles/get_profiles"
            data = {"user_ids": [user_id]}
            headers = {"X-API-Key": BW2_API_KEY, "Content-Type": "application/json"}
            resp = requests.post(
                url,
                json.dumps(data),
                headers=headers,
            )
            LoggingService.log(
                context='phone_number',
                browser='BW2',
                request_data=data,
                request_headers=headers,
                status_code=resp.status_code,
                response_data=resp.json(),
            )

        except Exception as e:
            capture_exception(e)
        try:
            phone_number = UserService.format_phone_number(resp.json()["data"][0]["phone_number"])
            Notary.objects.update_or_create(user_id=user_id, defaults={"phone_number": phone_number})
        except Exception:
            phone_number = None
        return phone_number

    @staticmethod
    def user_id(phone_number: str) -> str:
        phone_number = UserService.format_phone_number(phone_number)
        try:
            return Notary.objects.filter(phone_number=phone_number).first().user_id
        except Exception:
            pass
        try:
            url = f"{BW3_BASE_URL}/profile"
            data = {"phoneNumber": f'0{phone_number}'}
            headers = {
                    "Authorization": f"Bearer {BW3_TOKEN}",
                    "Content-Type": "application/json",
                }
            resp = requests.post(
                url,
                json.dumps(data),
                headers=headers,
            )
            LoggingService.log(
                context='user_id',
                browser='BW3',
                request_data=data,
                request_headers=headers,
                status_code=resp.status_code,
                response_data=resp.json()
            )
        except Exception as e:
            capture_exception(e)

        if resp.status_code == 200 and "id" in resp.json():
            Notary.objects.update_or_create(phone_number=phone_number, defaults={"user_id": resp.json()['id']})
            return resp.json()["id"]
        try:
            url = f"{BW2_BASE_URL}/profiles/get_profiles"
            data = {"phone_numbers": [f'0{phone_number}']}
            headers = {"X-API-Key": BW2_API_KEY, "Content-Type": "application/json"}
            resp = requests.post(
                url,
                json.dumps(data),
                headers=headers,
            )
            LoggingService.log(
                context='user_id',
                browser='BW2',
                request_data=data,
                request_headers=headers,
                status_code=resp.status_code,
                response_data=resp.json()
            )
        except Exception as e:
            capture_exception(e)
        try:
            userid = resp.json()["data"][0]["user_id"]
            Notary.objects.update_or_create(phone_number=phone_number, defaults={"user_id": userid})
        except Exception:
            userid = None
        return userid

    @staticmethod
    def is_mci(phone_number: str):
        mci_pre_codes = (
            Config.objects.filter(title="MCI Pre Codes").cache().first().value
        )
        if phone_number.startswith("0"):
            phone_number = phone_number[1:]
        return any(
            phone_number.startswith(pre_code.strip())
            for pre_code in mci_pre_codes.split(",")
        )

    @staticmethod
    def format_phone_number(phone_number):
        try:
            if re.search(r"(^[0]?)([9])(\d{9}$)", phone_number) is None:
                raise exceptions.InvalidPhoneNumber()
            return phone_number[1:] if len(phone_number) == 11 else phone_number
        except Exception:
            raise InvalidPhoneNumber()


class LoggingService:
    @staticmethod
    def log(context=None, browser=None, request_data=None, request_headers=None, status_code=None, response_data=None):
        logger = logging.getLogger('eagleusers_api_calls')
        log = {
            'context': context,
            'browser': browser,
            'request_data': request_data,
            'status_code': status_code,
            'response_data': response_data
        }
        logger.info(json.dumps(log))
