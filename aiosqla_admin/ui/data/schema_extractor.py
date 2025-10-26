from .base_extractor import UIModelExtractor

class SchemaExtractor(UIModelExtractor):
    async def extract(self):
        instance = self.instance
        schema = instance.__schema__
        model_data = {}

        for field_name, model_field in schema.model_fields.items():
            if self.only_field and field_name != self.only_field:
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

        model_data = self.reorder_logic.apply(model_data)
        return {self.only_field: model_data[self.only_field]} if self.only_field else model_data
