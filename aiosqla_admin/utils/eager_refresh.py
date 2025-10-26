from sqlalchemy import inspect, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession


async def eager_refresh(
    session: AsyncSession,
    instance: object,
    *relationship_fields: str
):
    """
    Reloads a SQLAlchemy instance from the database, eagerly loading all relationships with selectinload
    unless specific fields are passed.

    Args:
        session (AsyncSession): The SQLAlchemy async session.
        instance (object): The SQLAlchemy ORM model instance to reload.
        *relationship_fields (str): Optional list of relationship fields to load. If none provided, all are loaded.

    Returns:
        The reloaded instance with specified relationships eagerly loaded.
    """
    model_cls = type(instance)
    mapper = inspect(model_cls)
    
    # Handle composite primary keys
    pk_filter = []
    for pk_col in mapper.primary_key:
        value = getattr(instance, pk_col.key, None)
        if value is None:
            raise ValueError(f"Primary key column '{pk_col.key}' is None for {model_cls.__name__}")
        pk_filter.append(pk_col == value)

    # Determine which relationships to load
    if relationship_fields:
        rel_names = relationship_fields
    else:
        rel_names = list(mapper.relationships.keys())

    # Validate relationships
    invalid = [r for r in rel_names if r not in mapper.relationships]
    if invalid:
        raise AttributeError(f"{model_cls.__name__} has no relationship(s): {', '.join(invalid)}")

    options = [selectinload(getattr(model_cls, r)) for r in rel_names]

    stmt = select(model_cls).options(*options).filter(*pk_filter)
    result = await session.execute(stmt)
    loaded = result.scalar_one_or_none()

    if loaded is None:
        raise ValueError(f"Instance of {model_cls.__name__} not found with PK={pk_filter}")

    return loaded
