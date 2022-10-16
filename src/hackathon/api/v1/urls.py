from starlite import Router

from .handlers import advocates, misc

api_v1_router = Router(
    path="/v1",
    route_handlers=[
        advocates.router,

        misc.router,
    ],
)
