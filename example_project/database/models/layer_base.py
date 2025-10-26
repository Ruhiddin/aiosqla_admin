from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import (
    relationship,
)
from sqlalchemy.orm.attributes import InstrumentedAttribute

# ==============______ICON MIXIN______=========================================================================================== ICON MIXIN
__field_icons__ = {
        'field_id': '🖇',
        'id': '🆔',
        'first_name': '👤',
        'phone': '☎️',
        'realtive': '🫂',
        'user': '👤',
        'residence': '📍',
        'treating': '💞',
        'grade': '🌟',
        'comment': '💬',
        'bike': '🚲',
        'price': '💰',
        'accessuar': '🧩',
        'index': '#️⃣',
        'ready': '🛠',
        'size': '📐',
        'during_order_id': '🏷',
        'purpose': '🎯',
        'amount': '🧮',
        'reason': '💬',
        'current_amount': '🧮',
        'code': '🔠',
        'file_type': '📀',
        'media_type': '🗂',
        'rel_class': '💿',
        'key': '🔑',
        'value': '🔠',
        'is_active': '🟢',
        'direction': '↕️',
        'read_status': '📨'
    }

__default_icon__ = '✏️'

# ==============______GET ICON______=========================================================================================== GET ICON
def get_icon(field_name):
    """
    Retrieve the icon for a given field name.
    If no specific icon is defined, return the default icon.
    """
    return next(
        (icon for key, icon in __field_icons__.items() if key in field_name),
        __default_icon__,
    )
    




class EagerLoadMixin:
    @declared_attr
    def __mapper_args__(cls):
        return {
            "eager_defaults": True  # Ensures defaults are eagerly loaded
        }

    @declared_attr
    def __mapper_cls__(cls):
        # Customize the Mapper to always load relationships eagerly
        from sqlalchemy.orm import Mapper

        class CustomMapper(Mapper):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for prop in kwargs.get("properties", {}).values():
                    if isinstance(prop, InstrumentedAttribute) and isinstance(prop.property, relationship):
                        # Automatically change lazy loading to 'selectin' if it's lazy-loaded
                        if prop.property.lazy == "select":
                            prop.property.lazy = "selectin"
        return CustomMapper


# class TelegramBase:
#     """Base class for models that need Telegram-specific list views."""
#     __excluded_btns__ = []

#     def tg_list_view(self):
#         """Telegram-specific enhanced list view."""
#         fields_to_include = getattr(self, '__list_view_fields__', None)
#         if fields_to_include is None:
#             fields_to_include = [col.key for col in inspect(self.__class__).columns]

#         icony_values = []

#         for field in fields_to_include:
#             # try:
#             value = self._resolve_field_expression(field)
#             icon = __default_icon__

#             if value and enum_labels.get(value) and isinstance(value, PyEnum):
#                 icony_value = enum_labels[value]
#             elif value and isinstance(value, datetime):
#                 icony_value = f"📅 {value}"
#             else:
#                 icon = get_icon(field)
#                 if hasattr(value, 'value') and isinstance(value, PyEnum):
#                     value = value.value
#                 icony_value = f"{icon} {value}" if value is not None else f"{icon} None"

#             icony_values.append(icony_value)
#             # except (AttributeError, IndexError, KeyError, ValueError):
#             #     icony_values.append(f"🚫-{field}")

#         # Fix label string length
#         return " ".join(string[:17] + ".." if len(string) > 17 else string for string in icony_values)

#     @classmethod
#     def tg_items_per_page(self):
#         item_max_len = len(self.__list_view_fields__) * 20
#         ITEMS_LEN_LIMIT = TELEGRAM_MESSAGE_LIMIT - 96
#         return ITEMS_LEN_LIMIT // (item_max_len + 1)

#     def _resolve_field_expression(self, field):
#         """Resolves dot notation and slicing."""
#         if '[' in field and ']' in field:
#             base_field, slice_expr = field.split('[')
#             slice_expr = slice_expr.rstrip(']')
#             value = self._get_nested_attr(base_field)

#             if value is not None:
#                 start, end = map(lambda x: int(x) if x else None, slice_expr.split(':'))
#                 return value[start:end]
#             return None
#         else:
#             return self._get_nested_attr(field)
        
#     def _get_nested_attr(self, attr_path):
#         """
#         Safely access nested attributes using dot notation.
#         Example: 'relative.name' resolves to self.relative.name.
#         """
#         attrs = attr_path.split('.')
#         value = self
#         for attr in attrs:
#             value = getattr(value, attr, None)
#             if value is None:
#                 break
#         return value



# ====================================================================================================
# ==============             BASE             ==============#
# ====================================================================================================
class Base(DeclarativeBase, EagerLoadMixin):#, TelegramBase):
    __abstract__ = True  # Prevents table creation for Base itself

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    def short_repr(self):
        return str(self.id)
    
    def __repr__(self):
        fields = [col.key for col in inspect(self.__class__).columns]
        field_values = [f"{field}={getattr(self, field, None)}" for field in fields]
        return f"<{self.__class__.__name__}({', '.join(field_values)})>"

