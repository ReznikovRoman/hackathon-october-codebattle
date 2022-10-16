from .models import Advocate
from .repositories import AdvocateRepository
from .schemas import AdvocateCreateSchema, AdvocateDetailSchema, AdvocateShortDetailSchema
from .services import AdvocateService

__all__ = [
    "Advocate",
    "AdvocateRepository",
    "AdvocateService",
    "AdvocateCreateSchema",
    "AdvocateShortDetailSchema",
    "AdvocateDetailSchema",
]
