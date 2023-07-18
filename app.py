import os
from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv

from db import db
from blocked_tokens import BLOCKLIST  # mover para a db

from resources.items import blp as ItemBlueprint
from resources.stores import blp as StoreBlueprint
from resources.tags import blp as TagBlueprint
from resources.users import blp as UserBlueprint


def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv(
        "DATABASE_URL", "sqlite:///data.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)

    app.config["JWT_SECRET_KEY"] = os.getenv("DATABASE_URL", "secret_123")
    jwt = JWTManager(app)

    # ----- jwt settings:
    @jwt.token_in_blocklist_loader
    def check_if_token_is_blocked(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.needs_fresh_token_loader
    def needs_fresh_token_loader(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "message": "Token is not fresh",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )

    @jwt.revoked_token_loader
    def revoked_token_loader(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "message": "Token is not valid, please log in again.",
                    "error": "token_revoked",
                }
            ),
            401,
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_loader(error):
        return (
            jsonify(
                {"message": "Signature verification failed", "error": "invalid_token"}
            ),
            401,
        )

    # -------
    # Exemplo para criacao da database via SQLalchemy, cria uma database sqlite3
    # Normalmente pode ser utilizado para testes e desenvolvimento local antes da integracao
    # with app.app_context():
    #     db.create_all()
    # -------

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app
