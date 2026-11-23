from src.core.exceptions import BusinessRuleError


def non_blank(value: str, field: str, max_length: int) -> str:
    cleaned = value.strip() if isinstance(value, str) else ""
    if not cleaned:
        raise BusinessRuleError(f"{field} must not be blank")
    if len(cleaned) > max_length:
        raise BusinessRuleError(f"{field} must be at most {max_length} characters")
    return cleaned
