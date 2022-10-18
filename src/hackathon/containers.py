from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from hackathon.config.settings import get_settings
from hackathon.domain import advocates, companies
from hackathon.infrastructure.db import redis

__all__ = ["Container", "override_providers", "inject_db_session"]

settings = get_settings()


class Container(containers.DeclarativeContainer):
    """DI container."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "hackathon.api.v1.handlers.misc",
        ],
    )

    config = providers.Configuration()

    # Infrastructure

    db_session = providers.Dependency(instance_of=AsyncSession)

    redis_connection = providers.Resource(
        redis.init_redis,
        config=settings.redis,
    )

    # Domain -> Advocates

    social_account_repository = providers.Factory(
        advocates.SocialAccountRepository,
        session=db_session,
    )

    social_account_service = providers.Factory(
        advocates.SocialAccountService,
        repository=social_account_repository,
    )

    advocate_repository = providers.Factory(
        advocates.AdvocateRepository,
        session=db_session,
    )

    advocate_service = providers.Factory(
        advocates.AdvocateService,
        repository=advocate_repository,
    )

    # Domain -> Companies

    company_repository = providers.Factory(
        companies.CompanyRepository,
        session=db_session,
    )

    company_service = providers.Factory(
        companies.CompanyService,
        repository=company_repository,
    )


def inject_db_session(container: Container, session_maker: sessionmaker) -> Container:
    """Inject SQLAlchemy session into container."""
    container.db_session.override(providers.Singleton(session_maker))
    return container


def override_providers(container: Container, /) -> Container:
    """Override providers with stubs."""
    if not container.config.USE_STUBS():
        return container
    return container


async def dummy_resource() -> None:
    """Dummy async resource for overriding providers in a DI container."""
