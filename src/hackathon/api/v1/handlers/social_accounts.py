from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from starlite import Controller, Dependency, Partial, Router, delete, get, patch, post

from hackathon.containers import Container
from hackathon.domain.advocates import (
    SocialAccount, SocialAccountCreateSchema, SocialAccountFullDetailSchema, SocialAccountService,
    SocialAccountShortDetailSchema,
)
from hackathon.domain.advocates.schemas import SocialAccountUpdateSchema
from hackathon.lib.dependency_injector.ext.starlite import ProvideDI, inject
from hackathon.lib.repositories.types import FilterTypes


class SocialAccountController(Controller):
    """Social Accounts API."""

    member_path = "{social_account_id:uuid}"

    @get()
    @inject
    async def get_social_accounts(
        self,
        filters: list[FilterTypes] = Dependency(skip_validation=True), *,
        service: Annotated[SocialAccountService, ProvideDI] = ProvideDI[Container.social_account_service],
    ) -> list[SocialAccountShortDetailSchema]:
        """Get a list of social accounts."""
        return [SocialAccountShortDetailSchema.from_orm(item) for item in await service.list(*filters)]

    @post()
    @inject
    async def create_social_account(
        self,
        data: SocialAccountCreateSchema, *,
        service: Annotated[SocialAccountService, ProvideDI] = ProvideDI[Container.social_account_service],
    ) -> SocialAccountFullDetailSchema:
        """Create a social account."""
        return SocialAccountFullDetailSchema.from_orm(await service.create(SocialAccount.from_dto(data)))

    @get(member_path)
    @inject
    async def get_social_account(
        self,
        social_account_id: UUID, *,
        service: Annotated[SocialAccountService, ProvideDI] = ProvideDI[Container.social_account_service],
    ) -> SocialAccountFullDetailSchema:
        """Get social account by ID."""
        social_account = await service.get(social_account_id)
        return SocialAccountFullDetailSchema.from_orm(social_account)

    @patch(member_path)
    @inject
    async def patch_social_account(
        self,
        social_account_id: UUID,
        data: Partial[SocialAccountUpdateSchema], *,
        service: Annotated[SocialAccountService, ProvideDI] = ProvideDI[Container.social_account_service],
    ) -> SocialAccountFullDetailSchema:
        """Patch an advocate."""
        return SocialAccountFullDetailSchema.from_orm(
            await service.update(social_account_id, SocialAccount.from_dto(data)))

    @delete(member_path, status_code=HTTPStatus.NO_CONTENT)
    @inject
    async def delete_social_account(
        self,
        social_account_id: UUID, *,
        service: Annotated[SocialAccountService, ProvideDI] = ProvideDI[Container.social_account_service],
    ) -> None:
        """Delete social account by ID."""
        await service.delete(social_account_id)


router = Router(
    path="/social-accounts",
    route_handlers=[SocialAccountController],
    tags=["Social Accounts"],
)
