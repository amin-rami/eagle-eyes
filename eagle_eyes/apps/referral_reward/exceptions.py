from rest_framework.exceptions import APIException
from rest_framework import status


class NotMCI(APIException):
    default_detail = {
        "code": 403004,
        "message": 'NOT_MCI_MOBILE_NUMBER',
        "user_title": "همراه اولی نبودن شماره تلفن",
        "user_description": "شماره تلفن همراه اولی نمی باشد"
    }
    status_code = status.HTTP_403_FORBIDDEN


class NotDone(APIException):
    default_detail = {
        "code": 403004,
        "message": 'CAMPAIGN_NOT_DONE',
        "user_title": "ماموریت ها انجام نشده اند",
        "user_description": "شما هنوز ماموریت های مورد نیاز برای دریافت جایزه را انجام نداده اید"
    }
    status_code = status.HTTP_403_FORBIDDEN


class RewardAlreadyTaken(APIException):
    default_detail = {
        "code": 403004,
        "message": 'REWARD_ALREADY_TAKEN',
        "user_title": "جایزه قبلا دریافت شده است",
        "user_description": "شما قبلا جایزه خود را دریافت کرده اید"
    }
    status_code = status.HTTP_403_FORBIDDEN


class InvalidToken(APIException):
    default_detail = {
        "code": 403004,
        "message": 'INVALID_TOKEN',
        "user_title": "توکن نامعتبر",
        "user_description": "توکن شما نامعتبر است"
    }
    status_code = status.HTTP_403_FORBIDDEN


class TokenOwnerMismatch(APIException):
    default_detail = {
        "code": 403004,
        "message": 'TOKEN_OWNER_MISMATCH',
        "user_title": "توکن نامعتبر",
        "user_description": "توکن شما نامعتبر است"
    }
    status_code = status.HTTP_403_FORBIDDEN


class InvalidSSOToken(APIException):
    default_detail = {
        "code": 401004,
        "message": 'INVALID_SSO_TOKEN',
        "user_title": "ورود نامعتبر",
        "user_description": "لطفا ابتدا به حساب خود وارد شوید"
    }
    status_code = status.HTTP_401_UNAUTHORIZED


class NotEnoughPermissions(APIException):
    default_detail = {
        "code": 401004,
        "message": "NOT_BEHSA_TOKEN",
        "user_title": "دسترسی نامعتبر",
        "user_description": "دسترسی های مورد نیاز وجود ندارد",
    }
    status_code = status.HTTP_401_UNAUTHORIZED


class CampaignNotFound(APIException):
    default_detail = {
        "code": 404004,
        "message": 'CAMPAIGN_NOT_FOUND',
        "user_title": "کمپین مورد نظر یافت نشد",
        "user_description": "کمپین مورد نظر یافت نشد"
    }
    status_code = status.HTTP_404_NOT_FOUND


class AlreadyActiveReward(APIException):
    default_detail = {
        "code": 400004,
        "message": 'Reward_Already_Activated',
        "user_title": "بسته فعال",
        "user_description": "شماره شما در طی یک روز گذشته بسته فعال داشته است.پس از پایان مهلت بسته مجددا تلاش کنید"
    }
    status_code = status.HTTP_400_BAD_REQUEST


class AllocationFailed(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = {
        "code": 500001,
        "message": 'Reward_Allocation_Failed',
        "user_title": "خطای سرور",
        "user_description": "امکان دریافت جایزه در این زمان وجود ندارد"
    }
