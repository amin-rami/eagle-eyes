from rest_framework import status
from rest_framework.exceptions import APIException

logger = None
exception_dict = {
    "INQUIRY_CHANCE_FAILED": "InquiryChanceFailed",
    "ACTIVATION_PACKAGE_CHANCE_FAILED": "ActivationPackageChanceFailed",
    "INVALID_OFFER_ID": "InvalidOfferId",
    "LOGIN_FAILED_WHITE_LIST": "LoginFailedWhiteList",
    "INVALID_MOBILE_NUMBER": "InvalidMobileNumber",
    "OTP_SEND_FAILED": "OtpSendFailed",
    "INVALID_REQUEST_ID": "InvalidRequestId",
    "OTP_KEY_NOT_VALID": "OtpKeyNotValid",
    "OTP_VERIFY_FAILED": "OtpVerifyFailed",
    "ACTIVATION_ZAREBIN_FAILED": "ActivationZarebinFailed",
    "CURRENTSTATE_ZAREBIN_FAILED": "CurrentstateZarebinFailed",
    "MAX_ACTIVE_SESSION_EXCEED": "MaxActiveSessionExceed",
    "INVALID_AUTH_TOKEN": "InvalidAuthToken",
    "PACKAGE_DETAIL_ZAREBIN_FAILED": "PackageDetailZarebinFailed",
    "GET_ENRICHED_MOBILE_NUMBER_FAILED": "GetEnrichedMobileNumberFailed",
    "MCI_CHECK_NETWORK_FAILED": "MciCheckNetworkFailed",
    "CURRENTSTATE_ZAREBIN_ELIGIBLE_FAILED": "CurrentstateZarebinEligibleFailed",
    "CURRENTSTATE_ZAREBIN_CHECK_ELIGIBLE_FAILED": "CurrentstateZarebinCheckEligibleFailed",
    "INVALID_OTP_TYPE": "InvalidOtpType",
    "error.http.401": "Unauthorized",
    "error.http.403": "Forbidden",
    "InternalError": "InternalError",
}


class DataNotValid(APIException):
    default_detail = {
        "code": 400001,
        "message": '',
        "user_title": "درخواست شما اشتباه است",
        "user_description": "لطفاً دوباره تلاش کنید"
    }
    status_code = status.HTTP_400_BAD_REQUEST


class ActivationPackageChanceFailed(APIException):
    default_detail = {
        "code": 400002,
        "message": 'ACTIVATION_PACKAGE_CHANCE_FAILED',
        "user_title": "خطا در فعالسازی بسته شانس",
        "user_description": "متاسفانه در حال حاضر مشکلی پیش آمده است، لطفاً چند دقیقه دیگر مجددا تلاش فرمایید"
    }
    status_code = status.HTTP_400_BAD_REQUEST


class LoginFailedWhiteList(APIException):
    default_detail = {
        "code": 400003,
        "message": 'LOGIN_FAILED_WHITE_LIST',
        "user_title": "وایت لیست نبودن شماره موبایل",
        "user_description": "لطفاً دوباره تلاش کنید"
    }
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidMobileNumber(APIException):
    default_detail = {
        "code": 400004,
        "message": 'INVALID_MOBILE_NUMBER',
        "user_title": "خالی بودن شماره تلفن",
        "user_description": "شماره تلفن خالی یا اشتباه می باشد."
    }
    status_code = status.HTTP_400_BAD_REQUEST


class OtpSendFailed(APIException):
    default_detail = {
        "code": 400005,
        "message": 'OTP_SEND_FAILED',
        "user_title": "محدودیت تعداد ارسال در دوره",
        "user_description": "برای درخواست مجدد، می باییست چند دقیقه صبر کنید"
    }
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidRequestId(APIException):
    default_detail = {
        "code": 400006,
        "message": 'INVALID_REQUEST_ID',
        "user_title": "requestId نامعتبر",
        "user_description": "لطفا مجددا وارد صفحه لاگین شوید"
    }
    status_code = status.HTTP_400_BAD_REQUEST


class OtpKeyNotValid(APIException):
    default_detail = {
        "code": 400007,
        "message": 'OTP_KEY_NOT_VALID',
        "user_title": "otp نامعتبر",
        "user_description": "کد اعتبارسنجی واردشده اشتباه است."
    }
    status_code = status.HTTP_400_BAD_REQUEST


class OtpVerifyFailed(APIException):
    default_detail = {
        "code": 400008,
        "message": 'OTP_VERIFY_FAILED',
        "user_title": "خطای verify otp",
        "user_description": "در تایید کد اعتبارسنجی مشکلی پیش آمده است. مجددا تلاش کنید."
    }
    status_code = status.HTTP_400_BAD_REQUEST


class ActivationZarebinFailed(APIException):
    default_detail = {
        "code": 400009,
        "message": 'ACTIVATION_ZAREBIN_FAILED',
        "user_title": "خطا در activation",
        "user_description": "در فعالسازی بسته مشکلی پیش آمده است. مجددا وارد شوید."
    }
    status_code = status.HTTP_400_BAD_REQUEST


class CurrentstateZarebinFailed(APIException):
    default_detail = {
        "code": 400010,
        "message": 'CURRENTSTATE_ZAREBIN_FAILED',
        "user_title": "خطا در current state",
        "user_description": "چند دقیقه دیگر مجددا تلاش فرمایید"
    }
    status_code = status.HTTP_400_BAD_REQUEST


class MaxActiveSessionExceed(APIException):
    default_detail = {
        "code": 400011,
        "message": 'MAX_ACTIVE_SESSION_EXCEED',
        "user_title": "محدودیت در سشن های فعال کاربر",
        "user_description": "تعداد سشن های فعال شما بیشتر از محدودیت می باشد"
    }
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidAuthToken(APIException):
    default_detail = {
        "code": 400012,
        "message": 'INVALID_AUTH_TOKEN',
        "user_title": "Auth Token نامعتبر",
        "user_description": "توکن شما نامعتبر می باشد"
    }
    status_code = status.HTTP_400_BAD_REQUEST


class PackageDetailZarebinFailed(APIException):
    default_detail = {
        "code": 400013,
        "message": 'PACKAGE_DETAIL_ZAREBIN_FAILED',
        "user_title": "خطا در جزئیات بسته",
        "user_description": "در دریافت جزئیات بسته مشکلی پیش آمده است. مجددا تلاش نمایید."
    }
    status_code = status.HTTP_400_BAD_REQUEST


class GetEnrichedMobileNumberFailed(APIException):
    default_detail = {
        "code": 400014,
        "message": 'GET_ENRICHED_MOBILE_NUMBER_FAILED',
        "user_title": "شماره موبایل از شبکه همراه دریافت نشد",
        "user_description": "شماره موبایل از شبکه همراه دریافت نشد"
    }
    status_code = status.HTTP_400_BAD_REQUEST


class MciCheckNetworkFailed(APIException):
    default_detail = {
        "code": 400015,
        "message": 'MCI_CHECK_NETWORK_FAILED',
        "user_title": "Salt Token نا معتبر",
        "user_description": "Salt Token نا معتبر می باشد"
    }
    status_code = status.HTTP_400_BAD_REQUEST


class CurrentstateZarebinEligibleFailed(APIException):
    default_detail = {
        "code": 400016,
        "message": 'CURRENTSTATE_ZAREBIN_ELIGIBLE_FAILED',
        "user_title": "خطا در بررسی قابلیت فعالسازی برای یک کاربر",
        "user_description": "بررسی قابلیت فعالسازی بسته برای شما با خطا مواجه شد. لطفا مجددا وارد شوید"
    }
    status_code = status.HTTP_400_BAD_REQUEST


class CurrentstateZarebinCheckEligibleFailed(APIException):
    default_detail = {
        "code": 400017,
        "message": 'CURRENTSTATE_ZAREBIN_CHECK_ELIGIBLE_FAILED',
        "user_title": "خطا در بررسی اعتبار بسته",
        "user_description": "در استعلام اعتبار بسته مشکلی به وجود آمده است. لطفا لحظاتی دیگر تلاش کنید"
    }
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidOtpType(APIException):
    default_detail = {
        "code": 400018,
        "message": 'INVALID_OTP_TYPE',
    }
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidValidateToken(APIException):
    default_detail = {
        "code": 400019,
        "message": 'INVALID_VAL_TOKEN',
        "user_title": "VALIDATE Token نامعتبر",
        "user_description": "توکن شما نامعتبر می باشد"
    }
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidOfferId(APIException):
    default_detail = {
        "code": 500003,
        "message": 'INVALID_OFFER_ID',
        "user_title": "شناسه آفر نامعتبر",
        "user_description": "شناسه آفر نامعتبر می باشد. امکان فعالسازی بسته با این آفر وجود ندارد."
    }
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class ConfigNotFound(APIException):
    default_detail = {
        "code": 404001,
        "message": '',
        "user_title": "گردونه ی شانس وجود ندارد",
        "user_description": "لطفاً بعدا تلاش کنید"
    }
    status_code = status.HTTP_404_NOT_FOUND


class CampaignDateInNotNow(APIException):
    default_detail = {
        "code": 404002,
        "message": 'Campaign_Date_In_Not_Now',
        "user_title": "مدت زمان شرکت در این رویداد به اتمام رسیده است.",
        "user_description": "رویدادهای ‌آینده به شما اطلاع داده می‌شود."
    }
    status_code = status.HTTP_404_NOT_FOUND


class UserAlreadyAttempted(APIException):
    default_detail = {
        "code": 403001,
        "message": 'User_Already_Attempted',
        "user_title": "قبلا شانس خود را امتحان کردید",
        "user_description": "منتظر گردونه های شانس ‌آینده باشید."
    }
    status_code = status.HTTP_403_FORBIDDEN


class CampaignNotFound(APIException):
    default_detail = {
        "code": 404003,
        "message": 'CampaignNotFound',
        "user_title": "مدت زمان شرکت در این رویداد به اتمام رسیده است.",
        "user_description": "رویدادهای ‌آینده به شما اطلاع داده می‌شود."
    }
    status_code = status.HTTP_404_NOT_FOUND


class ChanceActivationFailed(APIException):
    default_detail = {
        "code": 500001,
        "message": '',
        "user_title": "متاسفانه در حال حاضر مشکلی پیش آمده است",
        "user_description": "لطفاً چند دقیقه دیگر مجددا تلاش فرمایید"
    }
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class InquiryChanceFailed(APIException):
    default_detail = {
        "code": 500002,
        "message": 'INQUIRY_CHANCE_FAILED',
        "user_title": "خطا در استعلام شانس",
        "user_description": "متاسفانه در حال حاضر مشکلی پیش آمده است، لطفاً چند دقیقه دیگر مجددا تلاش فرمایید"
    }
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class Unauthorized(APIException):
    default_detail = {
        "code": 401001,
        "message": 'Unauthorized',
        "user_title": "Unauthorized",
        "user_description": "می بایست مجددا وارد شوید"
    }
    status_code = status.HTTP_401_UNAUTHORIZED


class Forbidden(APIException):
    default_detail = {
        "code": 403001,
        "message": 'Forbidden',
    }
    status_code = status.HTTP_403_FORBIDDEN


class InternalError(APIException):
    default_detail = {
        "code": 500001,
        "message": 'InternalError',
        "user_title": "متاسفانه در حال حاضر مشکلی پیش آمده است",
        "user_description": "لطفاً چند دقیقه دیگر مجددا تلاش کنید"
    }
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
