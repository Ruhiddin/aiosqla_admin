from datetime import datetime
from pydantic import BaseModel
from typing import List


def get_schema_by_model_name(schemas: List[BaseModel], model_name: str):
    Schema = next([i for i in schemas if i.Meta.model.__name__ == model_name], None)
    assert Schema is not None, f"No schema found with this model_name: {model_name}"
    return Schema



def make_schema_nullable(schema: BaseModel) -> BaseModel:
    for field in schema.fields.values():
        field.allow_none = True
        field.required = False

    return schema


def convert_iso_to_datetime(data: dict) -> dict:
    """
    Converts all ISO-formatted datetime strings in a dictionary to datetime.datetime objects.
    Ignores fields that cannot be parsed or are not strings.
    
    Modifies the dictionary in place and also returns it.
    """
    for key, value in data.items():
        if isinstance(value, str):
            try:
                # fromisoformat supports `YYYY-MM-DDTHH:MM:SS[.ffffff][+HH:MM]`
                data[key] = datetime.fromisoformat(value)
            except ValueError:
                # Not a valid ISO-formatted datetime string
                continue
    return data