from hackathon.lib.services import Service

from .models import Advocate
from .repositories import AdvocateRepository


class AdvocateService(Service[Advocate, AdvocateRepository]):
    """Service for working with Advocates."""
