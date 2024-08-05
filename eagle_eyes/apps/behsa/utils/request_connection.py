import os
import requests
from eagle_eyes.settings import BEHSA_PROXY


class RequestConnection:
    __instance = None

    @staticmethod
    def get_connection():
        """ Static access method. """
        if RequestConnection.__instance is None:
            RequestConnection()

        return RequestConnection.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if RequestConnection.__instance is not None:
            pass
        else:
            RequestConnection.__instance = requests.Session()
            RequestConnection.__instance.proxies = dict(http=BEHSA_PROXY, https=BEHSA_PROXY)
            RequestConnection.__instance.verify = os.path.dirname(os.path.abspath(__file__)) + '/consolidate.pem'

    def __call__(self, *args, **kwargs):
        return self.__instance
