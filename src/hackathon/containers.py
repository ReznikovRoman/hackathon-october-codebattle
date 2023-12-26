from dependency_injector import containers, providers

from hackathon.config.settings import get_settings
from hackathon.domain import advocates, companies
from hackathon.infrastructure.db import postgres, redis

__all__ = ["Container", "override_providers"]

settings = get_settings()


class Container(containers.DeclarativeContainer):
    """DI container."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "hackathon.api.v1.handlers.advocates",
            "hackathon.api.v1.handlers.companies",
            "hackathon.api.v1.handlers.social_accounts",
            "hackathon.api.v1.handlers.misc",
        ],
    )

    config = providers.Configuration()

    # Infrastructure

    db = providers.Singleton(
        postgres.Database,
        config=settings.database,
    )

    redis_connection = providers.Resource(
        redis.init_redis,
        config=settings.redis,
    )

    # Domain -> Advocates

    social_account_repository = providers.Factory(
        advocates.SocialAccountRepository,
        session_factory=db.provided.session,
    )

    social_account_service = providers.Factory(
        advocates.SocialAccountService,
        repository=social_account_repository,
    )

    advocate_repository = providers.Factory(
        advocates.AdvocateRepository,
        session_factory=db.provided.session,
    )

    advocate_service = providers.Factory(
        advocates.AdvocateService,
        repository=advocate_repository,
    )

    # Domain -> Companies

    company_repository = providers.Factory(
        companies.CompanyRepository,
        session_factory=db.provided.session,
    )

    company_service = providers.Factory(
        companies.CompanyService,
        repository=company_repository,
    )


def override_providers(container: Container, /) -> Container:
    """Override providers with stubs."""
    if not container.config.USE_STUBS():
        return container
    return container


async def dummy_resource() -> None:
    """Dummy async resource for overriding providers in a DI container."""
