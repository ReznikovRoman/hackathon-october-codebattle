import pytest
from pydantic_factories import ModelFactory


@pytest.fixture
def model_factory() -> ModelFactory:
    return ModelFactory()
