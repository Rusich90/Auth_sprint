from http import HTTPStatus

from flask import Blueprint
from flask_pydantic import validate

from app.core.alchemy import db
from app.core.enums import DefaultRole
from app.models.db_models import Role
from app.serializers.auth import ErrorBody, OkBody
from app.serializers.roles import RoleBody
from app.utils import permissions_required

roles = Blueprint("roles", __name__, url_prefix="/roles")


@roles.route("/", methods=["GET"])
@validate(response_many=True)
@permissions_required(DefaultRole.admin)
def roles_list():
    return [RoleBody(id=role.id, name=role.name) for role in Role.query.all()]


@roles.route("/", methods=["POST"])
@validate()
@permissions_required(DefaultRole.admin)
def create_role(body: RoleBody):
    name_exist = Role.query.filter_by(name=body.name).one_or_none()
    if name_exist:
        msg = "Role with this name already exist"
        return ErrorBody(error=msg), HTTPStatus.CONFLICT
    role = Role(**body.dict())
    db.session.add(role)
    db.session.commit()
    return RoleBody(id=role.id, name=role.name), HTTPStatus.CREATED


@roles.route("/<role_id>/", methods=["PATCH"])
@validate()
@permissions_required(DefaultRole.admin)
def update_role(role_id: int, body: RoleBody):
    role = Role.query.filter_by(id=role_id).one_or_none()
    if not role:
        msg = "No role with this id"
        return ErrorBody(error=msg), HTTPStatus.NOT_FOUND
    name_exist = Role.query.filter_by(name=body.name).one_or_none()
    if name_exist:
        msg = "Role with this name already exist"
        return ErrorBody(error=msg), HTTPStatus.CONFLICT
    role.name = body.name
    db.session.commit()
    return RoleBody(id=role.id, name=role.name)


@roles.route("/<role_id>/", methods=["DELETE"])
@validate()
@permissions_required(DefaultRole.admin)
def delete_role(role_id: int):
    role = Role.query.filter_by(id=role_id).one_or_none()
    if not role:
        msg = "No role with this id"
        return ErrorBody(error=msg), HTTPStatus.NOT_FOUND
    db.session.delete(role)
    db.session.commit()
    msg = "Role successfully deleted"
    return OkBody(result=msg), HTTPStatus.NO_CONTENT
