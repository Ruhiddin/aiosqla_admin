from sqlalchemy.inspection import inspect as sqlalchemy_inspect
from sqlalchemy.orm import class_mapper
from sqlalchemy.types import Enum as SQLAEnum
from .base_extractor import UIModelExtractor

class SQLAlchemyExtractor(UIModelExtractor):
    async def extract(self):
        instance = self.instance
        model_class = instance.__class__
        mapper = class_mapper(model_class)
        model_data = {}

        ordered_columns = [
            attr_name for attr_name, attr_value in model_class.__dict__.items()
            if hasattr(attr_value, "key") and attr_value.key in mapper.c
        ] if not self.only_field else [self.only_field]

        for column_name in ordered_columns:
            column = mapper.c.get(column_name, None)
            if column is None: 
                continue
            field_name = column.name
            field_type = type(column.type).__name__.lower()
            value = getattr(instance, field_name, None)
            required = (
                not column.nullable
                and not (column.default is not None or column.server_default is not None)
                and field_name != 'id'
            )
            if self.only_field and field_name != self.only_field:
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
            if self.only_field and field_name != self.only_field:
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
        
        model_data = self.reorder_logic.apply(model_data)
        return {self.only_field: model_data[self.only_field]} if self.only_field else model_data
