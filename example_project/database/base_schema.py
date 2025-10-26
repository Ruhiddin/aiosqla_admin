from collections import defaultdict
from typing import Any, ClassVar, Dict, List, Optional, Type, Union, get_type_hints

from pydantic import BaseModel, ConfigDict, create_model
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta, Mapper, RelationshipProperty, class_mapper


def extract_id(v):
    if isinstance(v, dict):
        return v.get("id")
    return v

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    _model_class: ClassVar[Optional[Type[DeclarativeMeta]]] = None
    _relation_fields: ClassVar[Dict[str, Dict[str, Any]]] = {}

    class Meta:
        model: Optional[Type[DeclarativeMeta]] = None

    @classmethod
    def _resolve_config(cls):
        if cls._model_class is None:
            cls._model_class = getattr(cls.Meta, "model", None)
            if cls._model_class is None:
                raise ValueError("Meta.model must be defined")
    
    @classmethod
    def validators(cls) -> Dict[str, classmethod]:
        """Override in subclasses to define custom validation logic."""
        return {}
    

    @classmethod
    def _generate_schema(cls) -> Type[BaseModel]:
        cls._resolve_config()
        mapper: Mapper = class_mapper(cls._model_class)
        fields = {}
        cls._relation_fields = {}

        for prop in mapper.attrs:
            name = getattr(prop, 'key', None)
            if not name:
                continue

            if isinstance(prop, RelationshipProperty):
                related_model = prop.mapper.class_
                uselist = prop.uselist
                cls._relation_fields[name] = {"model": related_model, "uselist": uselist}
                type_hint = Optional[List[Union[int, Any]]] if uselist else Optional[Union[int, Any]]
                fields[name] = (type_hint, None)
            else:
                try:
                    py_type = prop.columns[0].type.python_type
                except Exception:
                    py_type = get_type_hints(cls._model_class).get(name, Any)
                fields[name] = (Optional[py_type], None)

        schema_cls = create_model(
            f"{cls._model_class.__name__}Schema",
            __base__=cls,
            __validators__=cls.validators(),
            **fields
        )
        schema_cls._model_class = cls._model_class
        schema_cls._relation_fields = cls._relation_fields

        def model_dump_override(self, **kwargs):
            data = super(schema_cls, self).model_dump(**kwargs)
            for field, info in schema_cls._relation_fields.items():
                val = getattr(self, field, None)
                if info["uselist"]:
                    data[field] = [obj.id for obj in val if getattr(obj, "id", None) is not None]
                else:
                    data[field] = val.id if getattr(val, "id", None) is not None else None
            return data

        schema_cls.model_dump = model_dump_override
        return schema_cls

    @classmethod
    def model_validate_auto(cls, obj: Any) -> BaseModel:
        return cls._generate_schema().model_validate(obj)

    @classmethod
    async def to_instance(cls, data: Dict[str, Any], session: AsyncSession) -> DeclarativeMeta:
        cls._resolve_config()
        model_cls = cls._model_class

        # Step 1: Collect all IDs per related model
        id_map = defaultdict(set)
        field_map = {}  # field -> (model, uselist, raw_value)

        for field, info in cls._relation_fields.items():
            related_model = info["model"]
            uselist = info["uselist"]
            val = data.get(field)

            field_map[field] = (related_model, uselist, val)


            if uselist and isinstance(val, list):
                for item in val:
                    obj_id = extract_id(item)
                    if obj_id is not None:
                        id_map[related_model].add(obj_id)
            elif val is not None:
                obj_id = extract_id(val)
                if obj_id is not None:
                    id_map[related_model].add(obj_id)

        # Step 2: Fetch all related objects in batches
        fetched_objects = {}
        for model, ids in id_map.items():
            if not ids:
                continue
            result = await session.execute(select(model).where(model.id.in_(ids)))
            for obj in result.scalars():
                fetched_objects[(model, obj.id)] = obj

        # Step 3: Assign fetched objects back into data
        for field, (related_model, uselist, val) in field_map.items():
            def resolve(obj):
                obj_id = obj.get("id") if isinstance(obj, dict) else obj
                fetched = fetched_objects.get((related_model, obj_id))
                if not fetched:
                    raise ValueError(f"{related_model.__name__} with id={obj_id} not found for field '{field}'")
                return fetched

            if uselist:
                data[field] = [resolve(item) for item in (val or [])]
            else:
                data[field] = resolve(val) if val is not None else None

        return model_cls(**data)
