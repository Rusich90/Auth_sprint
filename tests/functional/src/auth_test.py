import logging
from http import HTTPStatus
from typing import Any, Dict

import pytest

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.asyncio

PATH = "/api/v1/auth"


class TestUserAuth:
    user = {"login": "Test", "password": "QWERTy90!"}
    # noinspection SpellCheckingInspection
    change_name = {"login": "Best", "password": "QWERTysds90!"}
    tokens: Dict[str, Any] = {}

    async def test_create_user(self, make_request):
        response = await make_request(
            method="POST",
            url=f"{PATH}/registration",
            json=self.user,
        )
        assert response.status == HTTPStatus.CREATED
        logger.info("Response status : %s", response.status)
        assert response.body["login"] == self.user["login"]
        logger.info("Response message : %s", response.body)

    async def test_login_user(self, make_request):
        response = await make_request(
            method="POST",
            url=f"{PATH}/login",
            json=self.user,
        )
        assert response.status == HTTPStatus.OK
        self.tokens["access_token"] = response.body["access_token"]
        self.tokens["refresh_token"] = response.body["refresh_token"]
        logger.info("Response status : %s", response.status)

    async def test_change_login(self, make_request):
        response = await make_request(
            method="POST",
            url=f"{PATH}/change",
            json=self.change_name,
            jwt=self.tokens["access_token"],
        )
        assert response.status == HTTPStatus.ACCEPTED
        logger.info("Response status : %s", response.status)

    async def test_history(self, make_request):
        params = {"page": 1, "page_size": 1}
        response = await make_request(
            params=params,
            method="GET",
            url=f"{PATH}/history",
            jwt=self.tokens["access_token"],
        )

        assert response.status == HTTPStatus.OK
        logger.info("Response status : %s", response.status)

    async def test_refresh_token(self, make_request):
        response = await make_request(
            method="POST",
            url=f"{PATH}/refresh",
            json={"refresh_token": self.tokens["refresh_token"]},
        )
        assert response.status == HTTPStatus.OK
        self.tokens["access_token"] = response.body["access_token"]
        self.tokens["refresh_token"] = response.body["refresh_token"]

        logger.info("Response status : %s", response.status)

    async def test_logout(self, make_request):
        response = await make_request(
            method="POST",
            url=f"{PATH}/logout",
            jwt=self.tokens["access_token"],
        )

        assert response.status == HTTPStatus.CREATED
        logger.info("Response status : %s", response.status)


class TestAuthNegative:
    user_wrong_password = {"login": "Test", "password": "1234"}
    # noinspection SpellCheckingInspection
    user_right = {"login": "Best", "password": "QWERTysds90!"}
    user_fake = {"login": "Test", "password": "QWERTy90!"}

    async def test_create_user_short_password(self, make_request):
        response = await make_request(
            method="POST",
            url=f"{PATH}/registration",
            json=self.user_wrong_password,
        )
        assert response.status == HTTPStatus.BAD_REQUEST
        logger.info("Response status : %s", response.status)
        assert (
            response.body["validation_error"]["body_params"][0]["type"] == "value_error"
        )
        logger.info(
            "Response message : %s",
            response.body["validation_error"]["body_params"][0]["type"],
        )

    async def test_create_existing_user(self, make_request):
        response = await make_request(
            method="POST",
            url=f"{PATH}/registration",
            json=self.user_right,
        )
        assert response.status == HTTPStatus.CONFLICT
        logger.info("Response status : %s", response.status)
        logger.info("Response body : %s", response.body["error"])

    async def test_login_user_fake(self, make_request):
        response = await make_request(
            method="POST",
            url=f"{PATH}/login",
            json=self.user_fake,
        )
        assert response.status == HTTPStatus.CONFLICT
        logger.info("Response status : %s", response.status)
        assert response.body["error"] == "User with this credentials does not exist"
        logger.info("Response body : %s", response.body["error"])

    async def test_change_no_token(self, make_request):
        response = await make_request(
            method="POST",
            url=f"{PATH}/change",
            json=self.user_fake,
            jwt={},
        )
        assert response.status == HTTPStatus.UNAUTHORIZED
        logger.info("Response status : %s", response.status)
        assert response.body["error"] == "Missing Authorization Header"
        logger.info("Response body : %s", response.body["error"])
