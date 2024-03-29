
from ..server import Server
from .base import LoginResource, AuthResource, RegisterResource, UpdatePasswordResource, LogoutResource


def init_api(server: Server):
    server.api.add_resource(LoginResource, "/login")
    server.api.add_resource(AuthResource, "/auth")
    server.api.add_resource(RegisterResource, "/register")
    server.api.add_resource(UpdatePasswordResource, "/update-password")
    server.api.add_resource(LogoutResource, "/logout")
