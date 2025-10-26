from .sqla_extractor import SQLAlchemyExtractor
from .schema_extractor import SchemaExtractor

async def get_ui_data(instance, only_field: str=None):
    if isinstance(instance, dict) and hasattr(instance, "__schema__"):
        extractor = SchemaExtractor(instance, only_field)
    else:
        extractor = SQLAlchemyExtractor(instance, only_field)
    return await extractor.extract()
