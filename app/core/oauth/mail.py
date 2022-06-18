from typing import Tuple

import requests
from flask import request

from .base import OAuthSignIn
from ..enums import Provider


class MailSignIn(OAuthSignIn):
    """Represents MAIL.RU OAUTH."""

    provider_name: str = Provider.mail

    def callback(self) -> Tuple[str, str]:
        token = self.client.fetch_token(
            url=self.access_token_url,
            authorization_response=request.url,
        )
        response = requests.get(f'{self.info_url}{token["access_token"]}')
        info = response.json()
        return info["id"], info["email"]
