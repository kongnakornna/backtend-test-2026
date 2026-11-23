"""Framework-free application errors.

Raised by the domain and application layers; the presentation layer maps
each type to an HTTP status in ``presentation/exception_handlers.py``.
"""


class AppError(Exception):
    code = "error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    code = "not_found"


class ConflictError(AppError):
    code = "conflict"


class BusinessRuleError(AppError):
    code = "business_rule_violation"
