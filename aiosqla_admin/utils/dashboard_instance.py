from copy import deepcopy
from typing import Any, List, Literal, Optional, Union

from pydantic import ValidationError
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import make_transient
from sqlalchemy.sql import expression

from base import log
from database.models.layer_base import Base as BaseModel
from db_redis.memory.shared_clusters.dash import DashCluster
from utils.schema_utils import make_schema_nullable, model_schema_map
from utils.validation_utils import dict_resolve_complex_objs

# ==============______GET CURRENT INSTANCE______=========================================================================================== GET CURRENT INSTANCE
InstanceField = Literal['model_name_and_id', 'data', 'current_field', 'current_field_ui_text']


async def get_current_instance_(
    dashboard: DashCluster,
    field: Optional[Union[InstanceField, List[InstanceField]]] = None,
) -> Optional[Union[Any, List[Any]]]:
    """
    Retrieve one or more properties from the current instance in the dashboard stack.

    Args:
        dashboard (DashCluster): The dashboard context.
        field (str | list[str] | None): The field(s) to retrieve from the current instance.
            Valid values: 'model_name_and_id', 'data', 'current_field', 'current_field_ui_text'

    Returns:
        Any | list[Any] | None: Single result, ordered list of results, or None.
    """
    stack_list = await dashboard.detail.stack.stack_list.get()
    if not stack_list:
        return None

    current = stack_list[-1]
    class_name, i_id = current['class_name'], current['id']
    instance = dashboard.detail.stack.instance(class_name, i_id)

    if not field:
        return None

    # Normalize to list
    single = False
    if isinstance(field, str):
        field = [field]
        single = True

    field_map = {
        'data': instance.data,
        'current_field': instance.current_field,
        'current_field_ui_text': instance.current_field_ui_text,
    }

    # Fast path for single field
    if single:
        match field[0]:
            case 'model_name_and_id':
                return (class_name, i_id)
            case f if f in field_map:
                return await field_map[f].get()
            case _:
                return None

    # Pipeline for multiple fields
    pipe = dashboard.get_pipeline()
    static_values = []
    piped_indices = []
    for i, f in enumerate(field):
        if f == 'model_name_and_id':
            static_values.append((i, (class_name, i_id)))
        elif f in field_map:
            pipe.add(field_map[f].get)
            piped_indices.append(i)
        else:
            static_values.append((i, None))

    piped_results = await pipe.execute()

    result = [None] * len(field)
    for idx, val in static_values:
        result[idx] = val
    for idx, val in zip(piped_indices, piped_results):
        result[idx] = val

    return result


# ==============______UPDATE CURRENT INSTANCE______=========================================================================================== UPDATE CURRENT INSTANCE
async def update_current_instance_(
    dashboard: DashCluster,
    field: Optional[Literal['data', 'current_field', 'current_field_ui_text']],
    value: Any,
) -> bool:
    """
    Update a specific field of the current instance in the dashboard stack.

    Args:
        dashboard (DashCluster): The dashboard context.
        field (str): One of 'data', 'current_field', 'current_field_ui_text'.
        value (Any): The value to assign to the field.

    Returns:
        bool: True if the field was updated, False otherwise.
    """
    stack_list = await dashboard.detail.stack.stack_list.get()

    if not stack_list:
        return False

    current = stack_list[-1]
    class_name, i_id = current['class_name'], current['id']

    instance = dashboard.detail.stack.instance(class_name, i_id)

    match field:
        case 'data':
            await instance.data.set(value)
        case 'current_field':
            await instance.current_field.set(value)
        case 'current_field_ui_text':
            await instance.current_field_ui_text.set(value)
        case _:
            return False

    return True




# ====================================================================================================
# ==============             UPDATE INSTANCE             ==============#
# ====================================================================================================

async def update_instance_data(instance_data: dict, update_items: dict, schema, session) -> dict:
    try:
        merged_data = {**instance_data, **update_items}
        id = instance_data.get('id', None)
        if not id:
            schema = make_schema_nullable(schema)

        data = dict_resolve_complex_objs(merged_data)

        # TEMP session for isolated validation (no accidental mutations)
        clone_session = sessionmaker(bind=session.get_bind())()
        validated_data = schema.load(data, session=clone_session, partial=True)

        result = schema.dump(deepcopy(validated_data))  # full detach
        await clone_session.close()
        return result
    except ValidationError as e:
        raise ValueError(f"Validation failed: {e.messages}")




# ==============______HYDRATE INSTANCE FROM DATA______=========================================================================================== HYDRATE INSTANCE FROM DATA
async def hydrate_instance_from_data(model_name, data: dict, session, final: bool=False):
    """
    Convert dict data into SQLAlchemy model instance using schema.load
    """
    try:
        Schema = model_schema_map.get(model_name)
        schema = Schema()
        id = data.get('id', None)
        if not id and not final:
            schema = make_schema_nullable(schema)

        data = dict_resolve_complex_objs(data)

        # Safe: use the same session
        instance = await schema.load(data, session=session)  # session handles deduplication
        return instance
    except ValidationError as e:
        raise e




# ====================================================================================================
# ==============             REVERT INSTANCE CHANGES             ==============#
# ====================================================================================================
def revert_instance_changes(instance):
    try:
        make_transient(instance)
        return True, instance
    except InvalidRequestError:
        return False, instance



# ==============______GET INSTANCE DATA______=========================================================================================== GET INSTANCE DATA
async def get_instance_data(model_name: str, instance: BaseModel):
    Schema = model_schema_map.get(model_name)
    schema = Schema()

    if not instance.id:
        schema = make_schema_nullable(schema)

    data = schema.dump(instance)

    for column in instance.__table__.columns:
        key = column.name
        if key not in data or data[key] is None:
            if column.default is not None and not isinstance(column.default.arg, expression.TextClause):
                default_val = column.default.arg() if callable(column.default.arg) else column.default.arg
                data[key] = default_val
            elif column.server_default is not None:
                # You can't evaluate server_default in Python—it’s for DB-side defaults
                pass  # optionally leave this or note it's skipped

    return data


# ====================================================================================================
# ==============             COMMIT INSTANCE CHANGES             ==============#
# ====================================================================================================  
async def commit_instance_changes(session, instance):
    try:
        session.add(instance)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e