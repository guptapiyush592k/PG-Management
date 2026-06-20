from pydantic import BaseModel


def require_at_least_one_field(model: BaseModel) -> None:
    if not model.model_fields_set:
        raise ValueError("At least one field must be provided")


def merge_update(existing: dict, update: BaseModel) -> dict:
    """Return a copy of existing values with PATCH fields applied."""
    merged = dict(existing)
    for field in update.model_fields_set:
        merged[field] = getattr(update, field)
    return merged
