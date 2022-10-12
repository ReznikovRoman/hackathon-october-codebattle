from starlite import Router

from .v1.urls import api_v1_router

api_router = Router(path="/api", route_handlers=[api_v1_router])
