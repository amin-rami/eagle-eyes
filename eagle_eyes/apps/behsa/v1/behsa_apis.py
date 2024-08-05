import datetime

from jalali_date import datetime2jalali

from . import exceptions  # noqa
from .core_apis import CoreApi


class BehsaApi(CoreApi):

    def salt(self, auth_token):
        resp, error = super().salt(auth_token)
        if resp["status_code"] != 200:
            raise getattr(exceptions, exceptions.exception_dict.get(error["error_message"],
                                                                    "InternalError"))()
        return resp['data']

    def verify_current_status(self, auth_token, salt_token):
        resp, error = super().verify_current_status(auth_token, salt_token)
        if resp["status_code"] != 200:
            raise getattr(exceptions, exceptions.exception_dict.get(error["error_message"],
                                                                    "InternalError"))()
        # Make Response
        current_dto = resp['data']['currentStateDto']
        offer_state = current_dto['offerState'] if current_dto is not None else {}
        package_status = current_dto['offerState']['status'] if offer_state is not None else ""
        phone_number = current_dto['userTellNumber'] if current_dto is not None else ""
        eligible = resp['data']['eligible']
        has_active_package = resp['data']['active']
        eligible_dto = resp['data']['eligibleDto']
        non_mci = current_dto['nonMci']

        if offer_state == {} or (offer_state and (not offer_state.get('startDate') or not offer_state.get('expDate')
                                                  or not offer_state.get('dataRemain') or not offer_state.get(
                    'dataInit')
                                                  or not offer_state.get('startDateTimestamp') or not offer_state.get(
                    'endDateTimestamp'))):
            offer_state = {
                "startDate": datetime2jalali(datetime.datetime.today()).strftime('%Y/%m/%d'),
                "expDate": datetime2jalali(datetime.datetime.today() + datetime.timedelta(days=30)).strftime(
                    '%Y/%m/%d'),
                "dataRemain": 2090,
                "dataInit": 2090,
                "startDateTimestamp": int(int(datetime.datetime.now().timestamp()) * 1e3),
                "endDateTimestamp": int(
                    int((datetime.datetime.today() + datetime.timedelta(days=30)).timestamp()) * 1e3),
            }
        if not eligible_dto or (eligible_dto and not eligible_dto.get('nextActive')):
            eligible_dto = {
                "nextActive": datetime2jalali(datetime.datetime.today() + datetime.timedelta(days=30)).strftime(
                    '%Y/%m/%d %H:%M:%S')
            }

        res = {
            "offer_state": offer_state,
            "package_status": package_status,
            "phone_number": phone_number,
            "eligible": eligible,
            "has_active_package": has_active_package,
            "eligibleDto": eligible_dto,
            "non_mci": non_mci
        }

        return res

    def chance_inquiry(self, auth_token, salt_token):
        resp, error = super().chance_inquiry(auth_token, salt_token)
        if resp["status_code"] not in (200, 400):
            raise getattr(exceptions, exceptions.exception_dict.get(error["error_message"],
                                                                    "ChanceActivationFailed"))()
        return resp

    def chance_activation(self, auth_token, salt_token, offer_id):
        resp, error = super().chance_activation(auth_token, salt_token, offer_id)
        if resp["status_code"] != 200:
            raise getattr(exceptions, exceptions.exception_dict.get(error["error_message"],
                                                                    "InternalError"))()
