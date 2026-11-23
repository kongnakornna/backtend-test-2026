class DomainError(Exception):
    """Base class for business-rule errors raised by the domain layer."""


class SchoolNotFoundError(DomainError):
    def __init__(self, school_id: int):
        self.school_id = school_id
        super().__init__(f"School {school_id} not found")
