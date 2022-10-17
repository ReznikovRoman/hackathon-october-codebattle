from starlite import Router

from .handlers import advocates, companies, misc, social_accounts

api_v1_router = Router(
    path="/v1",
    route_handlers=[
        social_accounts.router,
        advocates.router,
        companies.router,

        misc.router,
    ],
)
