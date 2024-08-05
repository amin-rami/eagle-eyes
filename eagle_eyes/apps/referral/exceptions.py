from rest_framework.exceptions import APIException
from rest_framework import status


class AuthenticationFailed(APIException):
    default_detail = {
        "message": "شما به حساب کاربری خود وارد نشده اید یا حساب کاربری شما ثبت نشده است"
    }
    status_code = status.HTTP_401_UNAUTHORIZED


class InvalidToken(APIException):
    default_detail = {
        "message": "توکن شما نامعتبر است"
    }
    status_code = status.HTTP_401_UNAUTHORIZED


class InvalidPhoneNumber(APIException):
    default_detail = {
        "message": "شماره تلفن وارد شده نامعتبر است"
    }
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidInvitationLink(APIException):
    default_detail = {
        "message": "لینک دعوت شما نامعتبر است"
    }
    status_code = status.HTTP_404_NOT_FOUND


class AlreadySignedUp(APIException):
    default_detail = {
        "message": "شماره تلفن وارد شده قبلا ثبت نام کرده است"
    }
    status_code = status.HTTP_400_BAD_REQUEST


class AlreadyInvited(APIException):
    default_detail = {
        "message": "شماره تلفن وارد شده قبلا دعوت شده است"
    }
    status_code = status.HTTP_400_BAD_REQUEST


class BadRequest(APIException):
    default_detail = {
        "message": "bad request"
    }
    status_code = status.HTTP_400_BAD_REQUEST


class SelfInvite(APIException):
    default_detail = {
        "message": "نمیتوانید خودتان را دعوت کنید"
    }
    status_code = status.HTTP_400_BAD_REQUEST
