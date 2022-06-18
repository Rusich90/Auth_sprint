from typing import Tuple

import requests
from flask import request

from .base import OAuthSignIn
from ..enums import Provider


class GoogleSignIn(OAuthSignIn):
    """Represents Google OAUTH."""

    provider_name: str = Provider.google

    def __init__(self):
        super().__init__()
        self.client.scope = "openid email profile"

    def callback(self) -> Tuple[str, str]:
        token = self.client.fetch_token(
            url=self.access_token_url,
            authorization_response=request.url,
        )
        response = requests.get(f'{self.info_url}{token["id_token"]}')
        info = response.json()
        return info["sub"], info["email"]
