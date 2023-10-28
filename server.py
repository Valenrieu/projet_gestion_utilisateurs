from importlib.machinery import SourceFileLoader
from aiohttp import web
import aiohttp_cors
import pathlib

#######################
## Load routes files ##
#######################

SERVER_ROOT = pathlib.Path(__file__).parents[0]
ROUTES_DIR = SERVER_ROOT / 'routes'

routes_files = [f for f in pathlib.Path(ROUTES_DIR).rglob('**/index.py')]

routes = {}
handlers = []

for file in routes_files:
    route = '/' + str(file.parents[0].relative_to(ROUTES_DIR))
    module_name = 'routes' + route.replace('/', '.')
    module = SourceFileLoader(module_name, str(file)).load_module() 
    routes[route] = module

    for method in ['GET', 'PUT', 'POST', 'DELETE']:
        if not hasattr(module, method):
            continue

        handler = getattr(module, method)
        routedef = getattr(web, method.lower())(route, handler)
        handlers.append(routedef)

#############################
## Config and start server ##
#############################

app = web.Application()
app.add_routes(handlers)

# Add CORS options
# Enables others domain to use your REST API.
cors = aiohttp_cors.setup(app, defaults={
  "*": aiohttp_cors.ResourceOptions(
       allow_credentials=True,
       expose_headers="*",
       allow_headers="*"
   )
})

for route in list(app.router.routes()):
    cors.add(route)

if __name__ == '__main__':
    web.run_app(app)
