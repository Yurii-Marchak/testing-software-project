from app.web.controllers.build_controller import register_build_routes
from app.web.controllers.client_controller import register_client_routes
from app.web.controllers.component_controller import register_component_routes
from app.web.controllers.dashboard_controller import register_dashboard_routes
from app.web.controllers.order_controller import register_order_routes


def register_routes(app) -> None:
    register_dashboard_routes(app)
    register_client_routes(app)
    register_build_routes(app)
    register_order_routes(app)
    register_component_routes(app)
