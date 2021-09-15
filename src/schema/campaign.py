import re
from uuid import uuid4, UUID
from typing import List, Optional, Dict

from pydantic import BaseModel

from .contact import Contact
from .template import Template
from .account import Account
from .channel import Channel
from .exceptions import InvalidData


TABLE_NAME = 'campaign'


class Campaign(BaseModel):
    """Databricks models"""
    # id: Optional[UUID]
    name: Optional[str] = 'campaign-' + str(uuid4())
    status: str
    account: Account
    channel: Channel  # TODO: Check in validations if channel.type is wpp
    template: Template
    contacts: List[Contact] = []

    def format_data(self):
        self.channel.value.replace(' ', '')

    def __validate_from_number(self):
        if re.fullmatch('\+?\d{10,15}', self.channel.value) is None:
            raise InvalidData(f'from_number has invalid value: {self.channel.value}')

    def __validate_contacts(self):
        # validate that there are contacts
        if len(self.contacts) == 0:
            raise InvalidData(f'contacts has len 0')

        # validate that the contact numbers are correct
        for contact in self.contacts:
            if re.fullmatch('\+?\d{10,15}', contact.number) is None:
                raise InvalidData(f'Invalid contact number: {contact.number}')

    def __validate_template(self):
        # how??
        return True

    def __validate_contact_variables(self):
        def _is_null(value):
            return value is None \
                   or value == '' \
                   or value == 'null' \
                   or value == 'nan'

        # validate all contact has the same variables
        variables_keys = [list(contact.variables.keys()) for contact in self.contacts]
        var = variables_keys[0]
        if not all([var == var_i for var_i in variables_keys[1:]]):
            raise InvalidData(f'Contacts has different variables.')

        # validate all variables has not null value (or empty)
        for contact in self.contacts:
            for key in var:
                if _is_null(contact.variables[key]):
                    raise InvalidData(
                        f'Contact {contact.number} has null variable value: '
                        f'{key}={contact.variables[key]}.'
                    )

    def validate_fields(self):
        # TODO: Validations:
        #  - Template content
        #  - Template variables mapping to contact variables

        self.__validate_from_number()
        self.__validate_contacts()
        self.__validate_template()
        self.__validate_contact_variables()
