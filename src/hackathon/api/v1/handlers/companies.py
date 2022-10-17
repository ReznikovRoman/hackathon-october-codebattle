from http import HTTPStatus
from typing import Final
from uuid import UUID

from starlite import Controller, Dependency, Partial, Provide, Router, delete, get, patch, post

from hackathon.dependencies import SEARCH_FILTER_DEPENDENCY_KEY, provide_company_service, search_filter_provider_factory
from hackathon.domain.companies import (
    Company, CompanyCreateSchema, CompanyDetailSchema, CompanyFullDetailSchema, CompanyService,
    CompanyShortDetailSchema,
)
from hackathon.lib.repositories.filters import SearchFilter
from hackathon.lib.repositories.types import FilterTypes


class CompanyController(Controller):
    """Companies API."""

    SEARCH_FIELD: Final[str] = "name"

    member_path = "{company_id:uuid}"

    @get(
        dependencies={
            SEARCH_FILTER_DEPENDENCY_KEY: Provide(search_filter_provider_factory(SEARCH_FIELD)),
        },
    )
    async def get_companies(
        self,
        service: CompanyService,
        search_filter: SearchFilter = Dependency(skip_validation=True),
        filters: list[FilterTypes] = Dependency(skip_validation=True),
    ) -> list[CompanyShortDetailSchema]:
        """Get a list of companies."""
        filters.append(search_filter)
        return [CompanyShortDetailSchema.from_orm(item) for item in await service.list(*filters)]

    @post()
    async def create_company(
        self, data: CompanyCreateSchema, service: CompanyService,
    ) -> CompanyDetailSchema:
        """Create a company."""
        return CompanyDetailSchema.from_orm(await service.create(Company.from_dto(data)))

    @get(member_path)
    async def get_company(
        self, company_id: UUID, service: CompanyService,
    ) -> CompanyFullDetailSchema:
        """Get company by ID."""
        return CompanyFullDetailSchema.from_orm(await service.get(company_id))

    @patch(member_path)
    async def patch_company(
        self, company_id: UUID, data: Partial[CompanyCreateSchema], service: CompanyService,
    ) -> CompanyDetailSchema:
        """Patch a company."""
        return CompanyDetailSchema.from_orm(await service.update(company_id, Company.from_dto(data)))

    @delete(member_path, status_code=HTTPStatus.NO_CONTENT)
    async def delete_company(self, company_id: UUID, service: CompanyService) -> None:
        """Delete company by ID."""
        await service.delete(company_id)


router = Router(
    path="/companies",
    route_handlers=[CompanyController],
    dependencies={"service": Provide(provide_company_service)},
    tags=["Companies"],
)
