from http import HTTPStatus

from flask import Blueprint, request
from flask_jwt_extended import get_current_user, jwt_required
from flask_pydantic import validate

from app.core import config
from app.core.alchemy import db
from app.core.oauth import OAuthSignIn
from app.models.db_models import Session, SocialAccount, User
from app.serializers.auth import ErrorBody, OkBody
from app.utils import generate_password, get_new_tokens

oauth = Blueprint("oauth", __name__, url_prefix="/oauth")


@oauth.route("/<provider>", methods=["GET"])
@validate()
def oauth_authorize(provider: str):
    if not hasattr(config.OAuthSettings(), provider):
        msg = f'Unsupported provider name - "{provider}"'
        return ErrorBody(error=msg), HTTPStatus.BAD_REQUEST

    oauth = OAuthSignIn.get_provider(provider)

    if request.method == "GET":
        return oauth.authorize()


@oauth.route("/<provider>", methods=["DELETE"])
@validate()
@jwt_required()
def delete_service(provider: str):
    if not hasattr(config.OAuthSettings(), provider):
        msg = f'Unsupported provider name - "{provider}"'
        return ErrorBody(error=msg), HTTPStatus.BAD_REQUEST

    social_account = SocialAccount.query.filter_by(
        user_id=get_current_user().id, social_name=provider
    ).one_or_none()
    if social_account:
        db.session.delete(social_account)
        db.session.commit()
        msg = f"{provider} account successfully detached"
        return ErrorBody(error=msg), HTTPStatus.CONFLICT
    else:
        msg = f"User does not have {provider} account"
        return ErrorBody(error=msg), HTTPStatus.CONFLICT


@oauth.route("/add/<provider>", methods=["GET"])
@validate()
@jwt_required()
def add_service(provider: str):
    if not hasattr(config.OAuthSettings(), provider):
        msg = f'Unsupported provider name - "{provider}"'
        return ErrorBody(error=msg), HTTPStatus.BAD_REQUEST

    oauth = OAuthSignIn.get_provider(provider)
    state = f"user_{get_current_user().id}"
    return oauth.authorize(state)


@oauth.route("/callback/<provider>", methods=["GET"])
@validate()
def oauth_callback(provider: str):
    """
    Endpoint for redirect_uri from services
    Can authorization, registration user and attach service to user
    """
    user = None
    generated_password = None

    # If user add service - state include user_id
    state = request.args.get("state")
    if state.startswith("user_"):
        user_id = state.split("_")[1]
        user = User.query.get(user_id)

    oauth = OAuthSignIn.get_provider(provider)
    social_id, email = oauth.callback()
    social_account = SocialAccount.query.filter_by(
        social_id=social_id, social_name=provider
    ).one_or_none()

    # Authorization logic
    if social_account and not user:
        session = Session(
            user=social_account.user, user_agent=request.user_agent.string
        )
        db.session.add(session)
        db.session.commit()
        return get_new_tokens(social_account.user, request.user_agent.string)

    # Registration logic
    elif not user and not social_account:
        user = User(login=email)
        generated_password = generate_password()
        user.set_password(generated_password)
        db.session.add(user)
        db.session.commit()

    # Add social_account logic
    if social_account:
        msg = f"{provider} already attached"
        return ErrorBody(error=msg), HTTPStatus.CONFLICT
    social = SocialAccount(user=user, social_id=social_id, social_name=provider)
    db.session.add(social)
    db.session.commit()

    # If registration logic
    if generated_password:
        session = Session(user=user, user_agent=request.user_agent.string)
        db.session.add(session)
        db.session.commit()
        return get_new_tokens(user, request.user_agent.string)

    msg = f"{provider} account successfully attached"
    return OkBody(result=msg), HTTPStatus.OK
