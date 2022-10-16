from http import HTTPStatus
from typing import Final
from uuid import UUID

from starlite import Controller, Dependency, Partial, Provide, Router, delete, get, patch, post

from hackathon.dependencies import (
    SEARCH_FILTER_DEPENDENCY_KEY, provide_advocate_service, search_filter_provider_factory,
)
from hackathon.domain.advocates import (
    Advocate, AdvocateCreateSchema, AdvocateDetailSchema, AdvocateService, AdvocateShortDetailSchema,
)
from hackathon.lib.repositories.filters import SearchFilter
from hackathon.lib.repositories.types import FilterTypes


class AdvocateController(Controller):
    """Advocates API."""

    SEARCH_FIELD: Final[str] = "name"

    member_path = "{advocate_id:uuid}"

    @get(
        dependencies={
            SEARCH_FILTER_DEPENDENCY_KEY: Provide(search_filter_provider_factory(SEARCH_FIELD)),
        },
    )
    async def get_advocates(
        self,
        service: AdvocateService,
        search_filter: SearchFilter = Dependency(skip_validation=True),
        filters: list[FilterTypes] = Dependency(skip_validation=True),
    ) -> list[AdvocateShortDetailSchema]:
        """Get a list of advocates."""
        return [AdvocateShortDetailSchema.from_orm(item) for item in await service.list(search_filter, *filters)]

    @post()
    async def create_advocate(self, data: AdvocateCreateSchema, service: AdvocateService) -> AdvocateDetailSchema:
        """Create an advocate."""
        return AdvocateDetailSchema.from_orm(await service.create(Advocate.from_dto(data)))

    @get(member_path)
    async def get_advocate(self, advocate_id: UUID, service: AdvocateService) -> AdvocateDetailSchema:
        """Get advocate by ID."""
        advocate = await service.get(advocate_id)
        return AdvocateDetailSchema.from_orm(advocate)

    @patch(member_path)
    async def patch_advocate(
        self, advocate_id: UUID, data: Partial[AdvocateCreateSchema], service: AdvocateService,
    ) -> AdvocateDetailSchema:
        """Patch an advocate."""
        return AdvocateDetailSchema.from_orm(await service.update(advocate_id, Advocate.from_dto(data)))

    @delete(member_path, status_code=HTTPStatus.NO_CONTENT)
    async def delete_advocate(self, advocate_id: UUID, service: AdvocateService) -> None:
        """Delete advocate by ID."""
        await service.delete(advocate_id)


router = Router(
    path="/advocates",
    route_handlers=[AdvocateController],
    dependencies={"service": Provide(provide_advocate_service)},
    tags=["Advocates"],
)
