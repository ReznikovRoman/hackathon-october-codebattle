from starlite import Router

from .handlers import misc

api_v1_router = Router(
    path="/v1",
    route_handlers=[
        misc.router,
    ],
)
