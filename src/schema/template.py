from uuid import UUID
from typing import Optional
from pydantic import BaseModel


TABLE_NAME = 'template'


class Template(BaseModel):
    """Databricks models"""
    # id: Optional[UUID]
    name: str
    namespace: str
    language: str
    content: Optional[str]

    def format_data(self):
        pass

    def validate_parameters(self):
        return True
