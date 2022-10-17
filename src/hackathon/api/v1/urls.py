from starlite import Router

from .handlers import advocates, misc, social_accounts

api_v1_router = Router(
    path="/v1",
    route_handlers=[
        social_accounts.router,
        advocates.router,

        misc.router,
    ],
)
