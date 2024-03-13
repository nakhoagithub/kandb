
from .extensions import api

from .apis.main import main_routes
from .apis.crud import collection_routes
from .apis.program import program_routes

main_routes(api)
collection_routes(api)
program_routes(api)
