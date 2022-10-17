from http import HTTPStatus
from uuid import UUID

from starlite import Controller, Dependency, Partial, Provide, Router, delete, get, patch, post

from hackathon.dependencies import provide_social_account_service
from hackathon.domain.advocates import (
    SocialAccount, SocialAccountCreateSchema, SocialAccountFullDetailSchema, SocialAccountService,
    SocialAccountShortDetailSchema,
)
from hackathon.domain.advocates.schemas import SocialAccountUpdateSchema
from hackathon.lib.repositories.types import FilterTypes


class SocialAccountController(Controller):
    """Social Accounts API."""

    member_path = "{social_account_id:uuid}"

    @get()
    async def get_social_accounts(
        self, service: SocialAccountService, filters: list[FilterTypes] = Dependency(skip_validation=True),
    ) -> list[SocialAccountShortDetailSchema]:
        """Get a list of social accounts."""
        return [SocialAccountShortDetailSchema.from_orm(item) for item in await service.list(*filters)]

    @post()
    async def create_social_account(
        self, data: SocialAccountCreateSchema, service: SocialAccountService,
    ) -> SocialAccountFullDetailSchema:
        """Create a social account."""
        return SocialAccountFullDetailSchema.from_orm(await service.create(SocialAccount.from_dto(data)))

    @get(member_path)
    async def get_social_account(
        self, social_account_id: UUID, service: SocialAccountService,
    ) -> SocialAccountFullDetailSchema:
        """Get social account by ID."""
        social_account = await service.get(social_account_id)
        return SocialAccountFullDetailSchema.from_orm(social_account)

    @patch(member_path)
    async def patch_social_account(
        self, social_account_id: UUID, data: Partial[SocialAccountUpdateSchema], service: SocialAccountService,
    ) -> SocialAccountFullDetailSchema:
        """Patch an advocate."""
        return SocialAccountFullDetailSchema.from_orm(
            await service.update(social_account_id, SocialAccount.from_dto(data)))

    @delete(member_path, status_code=HTTPStatus.NO_CONTENT)
    async def delete_social_account(self, social_account_id: UUID, service: SocialAccountService) -> None:
        """Delete social account by ID."""
        await service.delete(social_account_id)


router = Router(
    path="/social-accounts",
    route_handlers=[SocialAccountController],
    dependencies={"service": Provide(provide_social_account_service)},
    tags=["Social Accounts"],
)
