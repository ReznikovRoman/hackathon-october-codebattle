from hackathon.lib.schemas import BaseOrjsonSchema, OrjsonSchema, Schema


class AdvocateBaseSchema(BaseOrjsonSchema):
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
