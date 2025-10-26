from datetime import datetime
from uuid import UUID

from aiogram_toolkit.markdown.normalizators import normalize_markdown_v2 as nm2


def count_errors(errors: dict) -> int:
    return sum([len(val) for i, val in errors.items()])



def format_validation_errors_ui(errors: dict) -> str:
    """
    Format validation errors into a user-friendly plain-text message.
    Uses numeric ordering for fields and 1.1, 1.2... for sub-errors.
    """
    lines = [f"⚠️ {len(errors)} fields are not valid, pls fix them and then try to save again\\. \n\n❗️ {count_errors(errors)} errors:"]
    for field_index, (field, errs) in enumerate(errors.items(), 1):
        lines.append(f"__*{field_index}*__\\. *{nm2(field.replace('_', ' ').capitalize())}* \\({len(errs)} error{'s' if len(errs) > 1 else ''}\\):")
        for err_index, msg in enumerate(errs, 1):
            lines.append(f"     *{field_index}\\.{err_index}*\\. _{nm2(msg)}_")
    return "\n".join(lines)



def dict_resolve_complex_objs(data):
    if isinstance(data, dict):
        return {k: dict_resolve_complex_objs(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [dict_resolve_complex_objs(v) for v in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, UUID):
        return str(data)
    return data