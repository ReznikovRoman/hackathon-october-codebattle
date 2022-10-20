import inspect
import typing
from typing import Any, Callable, TypeVar

from dependency_injector import wiring

__all__ = ["inject", "ProvideDI"]

F = TypeVar("F", bound=Callable[..., Any])  # noqa: VNE001

ProvideDI = wiring.Provide


def _is_dependency(arg: Any) -> bool:
    """Verify that the given argument is a wiring `Marker` from `dependency-injector`."""
    return getattr(arg, "__IS_MARKER__", False)


def get_inject_annotations(function: F) -> dict[str, Any]:
    """Get function's DI annotations."""
    return {
        name: annotation
        for name, annotation in typing.get_type_hints(function, include_extras=True).items()
        if any(_is_dependency(arg) for arg in typing.get_args(annotation))
    }


def clear_wrapper(wrapper: F) -> F:
    """Remove DI parameters from the given function."""
    inject_annotations = get_inject_annotations(wrapper)
    signature = inspect.signature(wrapper)
    new_params = tuple(
        parameter
        for parameter in signature.parameters.values()
        if parameter.name not in inject_annotations
    )
    wrapper.__signature__ = signature.replace(parameters=new_params)
    for name in inject_annotations:
        del wrapper.__annotations__[name]
    return wrapper


def inject(function: F) -> F:
    """Inject DI provider into function."""
    wrapper = wiring.inject(function)
    wrapper = clear_wrapper(wrapper)
    return wrapper
