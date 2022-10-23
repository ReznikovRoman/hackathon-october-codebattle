import uuid

from pydantic import AnyUrl

from hackathon.lib.schemas import BaseOrjsonSchema, OrjsonSchema, Schema


class SocialAccountBaseSchema(BaseOrjsonSchema):
    """Social account base schema."""

    github: AnyUrl | None
    linkedin: AnyUrl | None
    youtube: AnyUrl | None
    twitter: AnyUrl | None


class SocialAccountUpdateSchema(SocialAccountBaseSchema, OrjsonSchema):
    """Social account update."""


class SocialAccountCreateSchema(SocialAccountBaseSchema, OrjsonSchema):
    """Social account create schema."""

    advocate_id: uuid.UUID


class SocialAccountShortDetailSchema(SocialAccountBaseSchema, Schema):
    """Social account short detail."""


class SocialAccountFullDetailSchema(SocialAccountBaseSchema, Schema):
    """Social account full detail."""

    advocate_id: uuid.UUID


class AdvocateCompanySchema(Schema):
    """Advocate's company schema."""

    name: str
    summary: str
    photo_url: AnyUrl | None


class AdvocateBaseSchema(BaseOrjsonSchema):
    """Advocate base schema."""

    name: str
    short_bio: str
    years_of_experience: int
    photo_url: AnyUrl | None


class AdvocateCreateSchema(AdvocateBaseSchema, OrjsonSchema):
    """Advocate create schema."""

    company_id: uuid.UUID

    long_bio: str


class AdvocateShortDetailSchema(Schema, AdvocateBaseSchema):
    """Advocate short detail."""


class AdvocateDetailSchema(Schema, AdvocateBaseSchema):
    """Advocate detail."""

    long_bio: str


class AdvocateFullDetailSchema(Schema, AdvocateBaseSchema):
    """Advocate full detail."""

    long_bio: str

    company: AdvocateCompanySchema
    social_account: SocialAccountShortDetailSchema | None
