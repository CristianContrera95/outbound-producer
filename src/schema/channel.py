from uuid import UUID
from typing import Optional
from pydantic import BaseModel


TABLE_NAME = 'channel'


class Channel(BaseModel):
    """Databricks models"""
    # id: Optional[UUID]
    name: str
    type_id: str
    value: str

    def format_data(self):
        pass

    def validate_parameters(self):
        return True
