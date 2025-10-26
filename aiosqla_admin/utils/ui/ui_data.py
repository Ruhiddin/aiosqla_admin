from sqlalchemy.inspection import inspect as sqlalchemy_inspect
from sqlalchemy.orm import class_mapper
from sqlalchemy.types import Enum as SQLAEnum


# ==============______REORDER AUTO TIMESTAMPS______=========================================================================================== REORDER AUTO TIMESTAMPS
def reorder_model_data(data: dict) -> dict:
    """Reorders 'id' to the beginning and auto timestamps to the end of the data dictionary."""
    if 'id' in data:
        id_value = data.pop('id')
        data = {'id': id_value, **data}
    
    for key in ['updated_at', 'created_at']:
        if key in data:
            data[key] = data.pop(key)
    
    return data

# ====================================================================================================
# ==============             GET UI DATA             ==============#
# ====================================================================================================
async def get_ui_data(instance, only_field_name: str = None):
    """
    Extract detailed data and metadata for fields from either:
    - a SQLAlchemy model instance
    - a Marshmallow schema-generated dictionary (must attach __schema__)
    """
    model_data = {}

    if isinstance(instance, dict) and hasattr(instance, "__schema__"):
        schema = instance.__schema__
        for field_name, model_field in schema.__fields__.items():
            if only_field_name and field_name != only_field_name:
                continue

            value = instance.get(field_name, None)
            field_type = model_field.outer_type_.__name__.lower()
            required = model_field.required
            read_only = model_field.field_info.extra.get("read_only", False)

            model_data[field_name] = {
                "type": field_type,
                "required": required,
                "value": value,
                "read_only": read_only,
            }
    else:
        # 🧩 SQLAlchemy-mode (original)
        model_class = instance.__class__
        mapper = class_mapper(model_class)

        ordered_columns = [
            attr_name
            for attr_name, attr_value in model_class.__dict__.items()
            if hasattr(attr_value, "key") and attr_value.key in mapper.c
        ] if not only_field_name else [only_field_name]

        for column_name in ordered_columns:
            column = mapper.c.get(column_name, None)
            if column is None: continue
            field_name = column.name
            field_type = type(column.type).__name__.lower()
            value = getattr(instance, field_name, None)
            required = (
                not column.nullable
                and not (column.default is not None or column.server_default is not None)
                and field_name != 'id'
            )
            if only_field_name and field_name != only_field_name:
                continue

            if isinstance(column.type, SQLAEnum):
                EnumClass = column.type.enum_class
                if EnumClass:
                    model_data[field_name] = {
                        "type": EnumClass,
                        "required": required,
                        "class_name": EnumClass.__name__,
                        "value": value,
                    }
            elif hasattr(column, "foreign_keys") and column.foreign_keys:
                continue
            elif field_type == "DateTime":
                is_auto_filled = column.default is not None or column.server_default is not None
                model_data[field_name] = {
                    "type": 'datetime',
                    "required": required,
                    "value": value,
                    "read_only": is_auto_filled,
                }
            elif field_name == 'id':
                model_data[field_name] = {
                    "type": int,
                    "required": required,
                    "value": value,
                    "read_only": True,
                }
            elif field_name == 'rel_id':
                class_name = getattr(instance, 'rel_class', None)
                class_name = class_name.value if class_name else class_name
                model_data[field_name] = {
                    "type": "rel_single",
                    "required": required,
                    "class_name": class_name,
                    "read_only": True,
                    "value": value,
                }
            else:
                model_data[field_name] = {
                    "type": field_type,
                    "required": required,
                    "value": value,
                }

        for rel in sqlalchemy_inspect(model_class).relationships:
            field_name = rel.key
            if only_field_name and field_name != only_field_name:
                continue
            related_instances = getattr(instance, field_name, None)
            required = any(not col.nullable for col in rel.local_columns)
            related_class_name = rel.mapper.class_.__name__

            if rel.uselist:
                if 'media' in field_name:
                    model_data[field_name] = {
                        "type": "rel_many",
                        "required": required,
                        "class_name": "Media",
                        "values": [
                            {'id': obj.id, 'file_type': obj.file_type.value}
                            for obj in related_instances or []
                        ],
                    }
                else:
                    model_data[field_name] = {
                        "type": "rel_many",
                        "required": required,
                        "class_name": related_class_name,
                        "values": [obj.id for obj in related_instances or []],
                    }
            else:
                model_data[field_name] = {
                    "type": "rel_single",
                    "required": required,
                    "class_name": related_class_name,
                    "repr": related_instances.short_repr() if related_instances else '',
                    "value": related_instances.id if related_instances else None,
                }

    model_data = reorder_model_data(model_data)
    result = {only_field_name: model_data[only_field_name]} if only_field_name else model_data

    return result
