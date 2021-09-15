from uuid import UUID
from pydantic import BaseModel


TABLE_NAME = 'account'


class Account(BaseModel):
    """Databricks models"""
    id: UUID
    name: str

    def format_data(self):
        pass

    def validate_parameters(self):
        return True
