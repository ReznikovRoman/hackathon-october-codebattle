from hackathon.lib.services import Service

from .models import Company
from .repositories import CompanyRepository


class CompanyService(Service[Company, CompanyRepository]):
    """Service for working with Companies."""
