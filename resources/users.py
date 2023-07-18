from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt,
    get_jwt_identity,
    create_refresh_token,
)

from schemas.schemas import UserSchema
from models import UserModel
from db import db
from blocked_tokens import BLOCKLIST

blp = Blueprint("users", __name__, description="IUser requests: ")


@blp.route("/user/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        user_data["password"] = pbkdf2_sha256.hash(user_data["password"])
        user = UserModel(**user_data)

        try:
            db.session.add(user)
            db.session.commit()

            return user
        except IntegrityError as e:
            abort(500, message="Username already in use")
        except SQLAlchemyError as e:
            abort(500, str(e))


@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get(user_id)

        if not user:
            abort(404, message="No user found for the provided Id")

        return user

    def delete(self, user_id):
        user = UserModel.query.get(user_id)

        if not user:
            abort(404, message="No user found for the provided Id")

        try:
            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted successfully"}, 200
        except SQLAlchemyError as e:
            abort(500, str(e))


@blp.route("/user/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.user_id, fresh=True)
            refresh_token = create_refresh_token(identity=user.user_id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        abort(400, message="username or password is invalid")


@blp.route("/user/refresh")
class UserTokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user_id = get_jwt_identity()
        new_token = create_access_token(identity=current_user_id, fresh=False)

        return {"access_token": new_token}, 200


@blp.route("/user/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)

        return {"message": "Successfully logged out"}, 200
