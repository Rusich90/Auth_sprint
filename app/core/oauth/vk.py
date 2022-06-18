from typing import Tuple

import requests
from flask import request
from transliterate import translit

from .base import OAuthSignIn
from ..enums import Provider


class VkontakteSignIn(OAuthSignIn):
    """Represents VK OAUTH."""

    provider_name: str = Provider.vkontakte

    def __init__(self):
        super().__init__()
        self.client.token_endpoint_auth_method = "client_secret_post"

    def callback(self) -> Tuple[str, str]:
        token = self.client.fetch_token(
            url=self.access_token_url,
            authorization_response=request.url,
        )
        response = requests.get(
            f'{self.info_url}{token["access_token"]}&user_ids={token["user_id"]}'
        )
        info = response.json()["response"][0]
        login = f'{info["first_name"]}{info["last_name"]}'.lower()
        translit_login = translit(login, "ru", reversed=True)
        email = f"{translit_login}@yandex_auth.test"
        return str(info["id"]), email
