from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple

from authlib.integrations.requests_client import OAuth2Session
from flask import Response, redirect, url_for

from .. import config
from ..config import OAuthServiceSettings


class OAuthSignIn(ABC):
    providers: Dict["str", "OAuthSignIn"] = {}

    @property
    def provider_name(self) -> str:
        pass

    def __init__(self):
        credentials: OAuthServiceSettings = getattr(
            config.OAuthSettings(), self.provider_name
        )
        redirect_uri = f"{config.FlaskSettings.redirect_uri}{self.provider_name}"
        self.client = OAuth2Session(
            client_id=credentials.client_id,
            client_secret=credentials.client_secret.get_secret_value(),
            redirect_uri=redirect_uri,
        )
        self.authorize_url = credentials.authorize_url
        self.access_token_url = credentials.access_token_url
        self.info_url = credentials.info_url

    def authorize(self, state: Optional[str] = None) -> Response:
        url, _ = self.client.create_authorization_url(self.authorize_url, state)
        return redirect(url)

    @abstractmethod
    def callback(self) -> Tuple[str, str]:
        pass

    def get_callback_url(self) -> str:
        return url_for("oauth_callback", provider=self.provider_name, _external=True)

    @classmethod
    def get_provider(cls, provider_name: str) -> "OAuthSignIn":
        if not cls.providers:
            cls.providers = {cl.provider_name: cl() for cl in cls.__subclasses__()}
        return cls.providers[provider_name]
