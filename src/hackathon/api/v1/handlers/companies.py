from http import HTTPStatus
from typing import Annotated, Final, Sequence
from uuid import UUID

from starlite import Controller, Dependency, Partial, Provide, Router, delete, get, patch, post

from hackathon.containers import Container
from hackathon.dependencies import SEARCH_FILTER_DEPENDENCY_KEY, search_filter_provider_factory
from hackathon.domain.companies import (
    Company, CompanyCreateSchema, CompanyDetailSchema, CompanyFullDetailSchema, CompanyService,
    CompanyShortDetailSchema,
)
from hackathon.lib.dependency_injector.ext.starlite import ProvideDI, inject
from hackathon.lib.repositories.filters import SearchFilter
from hackathon.lib.repositories.types import FilterTypes


class CompanyController(Controller):
    """Companies API."""

    SEARCH_FIELDS: Final[Sequence[str]] = ["name"]

    member_path = "{company_id:uuid}"

    @get(
        dependencies={
            SEARCH_FILTER_DEPENDENCY_KEY: Provide(search_filter_provider_factory(SEARCH_FIELDS)),
        },
    )
    @inject
    async def get_companies(
        self,
        search_filter: SearchFilter = Dependency(skip_validation=True),
        filters: list[FilterTypes] = Dependency(skip_validation=True), *,
        service: Annotated[CompanyService, ProvideDI] = ProvideDI[Container.company_service],
    ) -> list[CompanyShortDetailSchema]:
        """Get a list of companies."""
        filters.append(search_filter)
        return [CompanyShortDetailSchema.from_orm(item) for item in await service.list(*filters)]

    @post()
    @inject
    async def create_company(
        self,
        data: CompanyCreateSchema, *,
        service: Annotated[CompanyService, ProvideDI] = ProvideDI[Container.company_service],
    ) -> CompanyDetailSchema:
        """Create a company."""
        return CompanyDetailSchema.from_orm(await service.create(Company.from_dto(data)))

    @get(member_path)
    @inject
    async def get_company(
        self,
        company_id: UUID, *,
        service: Annotated[CompanyService, ProvideDI] = ProvideDI[Container.company_service],
    ) -> CompanyFullDetailSchema:
        """Get company by ID."""
        return CompanyFullDetailSchema.from_orm(await service.get(company_id))

    @patch(member_path)
    @inject
    async def patch_company(
        self,
        company_id: UUID,
        data: Partial[CompanyCreateSchema], *,
        service: Annotated[CompanyService, ProvideDI] = ProvideDI[Container.company_service],
    ) -> CompanyDetailSchema:
        """Patch a company."""
        return CompanyDetailSchema.from_orm(await service.update(company_id, Company.from_dto(data)))

    @delete(member_path, status_code=HTTPStatus.NO_CONTENT)
    @inject
    async def delete_company(
        self,
        company_id: UUID, *,
        service: Annotated[CompanyService, ProvideDI] = ProvideDI[Container.company_service],
    ) -> None:
        """Delete company by ID."""
        await service.delete(company_id)


router = Router(
    path="/companies",
    route_handlers=[CompanyController],
    tags=["Companies"],
)
