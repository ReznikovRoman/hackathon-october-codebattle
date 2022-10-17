from pydantic import AnyUrl, validator

from hackathon.lib.schemas import BaseOrjsonSchema, OrjsonSchema, Schema


class AdvocateCompanySchema(Schema):
    """List of advocates in company."""

    name: str
    short_bio: str
    years_of_experience: int
    photo_url: AnyUrl | None


class CompanyBaseSchema(BaseOrjsonSchema):
    """Company base schema."""

    name: str
    summary: str
    photo_url: AnyUrl | None


class CompanyCreateSchema(CompanyBaseSchema, OrjsonSchema):
    """Company create schema."""


class CompanyShortDetailSchema(CompanyBaseSchema, Schema):
    """Company short detail."""


class CompanyDetailSchema(CompanyBaseSchema, Schema):
    """Company detail."""


class CompanyFullDetailSchema(CompanyBaseSchema, Schema):
    """Company full detail."""

    advocates: list[AdvocateCompanySchema] | None

    @validator("advocates")
    def set_advocates(cls, advocates: list[AdvocateCompanySchema] | None) -> list[AdvocateCompanySchema]:
        return advocates or []
