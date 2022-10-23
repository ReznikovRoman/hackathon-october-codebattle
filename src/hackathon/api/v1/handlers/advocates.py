from http import HTTPStatus
from typing import Annotated, Final, Sequence
from uuid import UUID

from starlite import Controller, Dependency, Partial, Provide, Router, delete, get, patch, post

from hackathon.containers import Container
from hackathon.dependencies import SEARCH_FILTER_DEPENDENCY_KEY, search_filter_provider_factory
from hackathon.domain.advocates import (
    Advocate, AdvocateCreateSchema, AdvocateDetailSchema, AdvocateFullDetailSchema, AdvocateService,
    AdvocateShortDetailSchema,
)
from hackathon.lib.dependency_injector.ext.starlite import ProvideDI, inject
from hackathon.lib.repositories.filters import SearchFilter
from hackathon.lib.repositories.types import FilterTypes


class AdvocateController(Controller):
    """Advocates API."""

    SEARCH_FIELDS: Final[Sequence[str]] = ["name", "username"]

    member_path = "{advocate_id:uuid}"

    @get(
        dependencies={
            SEARCH_FILTER_DEPENDENCY_KEY: Provide(search_filter_provider_factory(SEARCH_FIELDS)),
        },
    )
    @inject
    async def get_advocates(
        self,
        search_filter: SearchFilter = Dependency(skip_validation=True),
        filters: list[FilterTypes] = Dependency(skip_validation=True), *,
        service: Annotated[AdvocateService, ProvideDI] = ProvideDI[Container.advocate_service],
    ) -> list[AdvocateShortDetailSchema]:
        """Get a list of advocates."""
        filters.append(search_filter)
        return [AdvocateShortDetailSchema.from_orm(item) for item in await service.list(*filters)]

    @post()
    @inject
    async def create_advocate(
        self,
        data: AdvocateCreateSchema, *,
        service: Annotated[AdvocateService, ProvideDI] = ProvideDI[Container.advocate_service],
    ) -> AdvocateDetailSchema:
        """Create an advocate."""
        return AdvocateDetailSchema.from_orm(await service.create(Advocate.from_dto(data)))

    @get(member_path)
    @inject
    async def get_advocate(
        self,
        advocate_id: UUID, *,
        service: Annotated[AdvocateService, ProvideDI] = ProvideDI[Container.advocate_service],
    ) -> AdvocateFullDetailSchema:
        """Get advocate by ID."""
        advocate = await service.get(advocate_id)
        return AdvocateFullDetailSchema.from_orm(advocate)

    @patch(member_path)
    @inject
    async def patch_advocate(
        self,
        advocate_id: UUID,
        data: Partial[AdvocateCreateSchema], *,
        service: Annotated[AdvocateService, ProvideDI] = ProvideDI[Container.advocate_service],
    ) -> AdvocateDetailSchema:
        """Patch an advocate."""
        return AdvocateDetailSchema.from_orm(await service.update(advocate_id, Advocate.from_dto(data)))

    @delete(member_path, status_code=HTTPStatus.NO_CONTENT)
    @inject
    async def delete_advocate(
        self,
        advocate_id: UUID, *,
        service: Annotated[AdvocateService, ProvideDI] = ProvideDI[Container.advocate_service],
    ) -> None:
        """Delete advocate by ID."""
        await service.delete(advocate_id)


router = Router(
    path="/advocates",
    route_handlers=[AdvocateController],
    tags=["Advocates"],
)
