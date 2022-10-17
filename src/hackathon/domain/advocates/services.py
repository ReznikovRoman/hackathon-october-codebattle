from hackathon.lib.services import Service

from .models import Advocate, SocialAccount
from .repositories import AdvocateRepository, SocialAccountRepository


class AdvocateService(Service[Advocate, AdvocateRepository]):
    """Service for working with Advocates."""


class SocialAccountService(Service[SocialAccount, SocialAccountRepository]):
    """Service for working with Social Accounts."""
