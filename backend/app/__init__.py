from flask import Flask
from flask_cors import CORS

from .database import init_db
from .routes.invoices import invoices_bp
from .routes.monthly_cards import monthly_cards_bp
from .routes.parking import parking_bp
from .routes.spaces import spaces_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    init_db()

    app.register_blueprint(spaces_bp, url_prefix="/api/spaces")
    app.register_blueprint(monthly_cards_bp, url_prefix="/api/monthly-cards")
    app.register_blueprint(parking_bp, url_prefix="/api/parking")
    app.register_blueprint(invoices_bp, url_prefix="/api/invoices")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app
