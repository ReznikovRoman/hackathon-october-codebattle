import uuid

from hackathon.lib.schemas import BaseOrjsonSchema, OrjsonSchema, Schema


class SocialAccountBaseSchema(BaseOrjsonSchema):
    """Social account base schema."""

    github: str | None
    linkedin: str | None
    youtube: str | None


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


class AdvocateBaseSchema(BaseOrjsonSchema):
    """Advocate base schema."""

    name: str
    short_bio: str
    years_of_experience: int


class AdvocateCreateSchema(AdvocateBaseSchema, OrjsonSchema):
    """Advocate create schema."""

    long_bio: str


class AdvocateShortDetailSchema(Schema, AdvocateBaseSchema):
    """Advocate short detail."""


class AdvocateDetailSchema(Schema, AdvocateBaseSchema):
    """Advocate full detail."""

    long_bio: str

    social_account: SocialAccountShortDetailSchema
