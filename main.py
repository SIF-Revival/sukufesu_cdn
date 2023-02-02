from sanic import Sanic

# routes
from routes import add_external_routes
# from adminRoutes import add_external_routes as add_admin_routes

app = Sanic("sif_cdn")
add_external_routes(app)
# add_admin_routes(app)

if __name__ == "__main__":
    # configuration
    import config
    # start
    app.run(host=config.SANIC_HOST, port=config.SANIC_PORT, debug=config.SANIC_DEBUG)