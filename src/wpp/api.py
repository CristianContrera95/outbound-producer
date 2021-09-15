import os
import logging
import datetime as dt
from typing import Dict, Optional
from base64 import b64encode

import requests

from settings import LOGGER_NAME
from .utils import try_three_time


logger = logging.getLogger(LOGGER_NAME)


class WppClient:

    def __init__(self):
        self.url_base = os.getenv('WPP_URL')
        self.token = None
        self._token_expires = None
        self.__login()

    @property
    def __header(self) -> Dict:
        return {'Authorization': f'Bearer {self.token}'}

    @try_three_time
    def __login(self):
        USER = os.getenv('WPP_USER')
        PASS = os.getenv('WPP_PASS')
        _TOKEN = b64encode(bytes(f"{USER}:{PASS}", "utf-8")).decode()
        HEADER = {
            'Authorization': f'Basic {_TOKEN}'
        }
        response = requests.post(f'{self.url_base}/v1/users/login',
                                 headers=HEADER)
        response.raise_for_status()
        self.token = response.json()['users'][0]['token']
        self._token_expires = response.json()['users'][0]['expires_after'].split('+')[0]

    @property
    def token_expires(self):
        return dt.datetime.strptime(self._token_expires, "%Y-%m-%d %H:%M:%S")

    @try_three_time
    def contact_ids(self, contacts: list) -> Optional[dict]:
        """Validate list of contacts"""
        response = requests.post(f'{self.url_base}/v1/contacts',
                                 headers=self.__header,
                                 json={
                                     "blocking": "wait",
                                     "contacts": contacts,
                                     "force_check": True
                                 })

        response.raise_for_status()

        contacts_resp = response.json()['contacts']
        contacts_resp = {
            contact['input']: {
                'wa_id': contact.get('wa_id'),
                'status': contact['status']
            } for contact in contacts_resp
        }

        return contacts_resp
