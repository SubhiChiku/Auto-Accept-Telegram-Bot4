from aiohttp import web

# Define routes
routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    """Handle the root route and return a JSON response."""
    return web.json_response({"message": "@Snowball_Official"})

async def web_server():
    """Create and configure the web application."""
    web_app = web.Application(client_max_size=30 * 1024 * 1024)  # 30 MB limit
    web_app.add_routes(routes)
    return web_app

if __name__ == "__main__":
    app = web_server()
    web.run_app(app, host="0.0.0.0", port=8080)
