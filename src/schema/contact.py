from uuid import uuid4, UUID
from typing import Optional, List
from pydantic import BaseModel, Json


TABLE_NAME = 'contact'


class Contact(BaseModel):
    """Databricks models"""
    id: Optional[UUID]
    number: str
    variables: Json = {}

    def format_data(self):
        # TODO: regex to check number
        pass

    def validate_parameters(self):
        return True
