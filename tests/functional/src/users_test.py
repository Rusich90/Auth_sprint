import logging
from http import HTTPStatus
from uuid import uuid4

import pytest
import pytest_asyncio

from app.serializers.auth import UserBody
from app.serializers.roles import RoleBody
from app.serializers.users import UserRolesBody

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.asyncio

PATH = "/api/v1/users"


@pytest_asyncio.fixture(name="temp_role", scope="session")
async def temp_role_fixture(make_request, superadmin_token):
    target_role = RoleBody(name="temp_role")
    response = await make_request(
        method="POST",
        url="/api/v1/roles/",
        json=target_role.dict(),
        jwt=superadmin_token,
    )

    role = RoleBody(**response.body)
    yield role


@pytest_asyncio.fixture(name="temp_user", scope="session")
async def temp_user_fixture(make_request):
    target_user = {"login": "role_tester", "password": "SuperStr0ng!"}
    response = await make_request(
        method="POST",
        url="/api/v1/auth/registration",
        json=target_user,
    )
    user = UserBody(**response.body)
    yield user


class TestGetUserRoles:
    """Test get users and roles method."""

    async def test_get_roles_list_success(self, make_request, superadmin_token: str):
        """Test get users and roles list method with success."""
        response = await make_request(
            method="GET",
            url=f"{PATH}/",
            jwt=superadmin_token,
        )
        assert response.status == HTTPStatus.OK
        logger.info("Users and roles: %s", response.body)


class TestSetRole:
    """Test grant role method."""

    async def test_success(
        self,
        make_request,
        superadmin_token: str,
        temp_role: RoleBody,
        temp_user: UserBody,
    ):
        """Test grant role with success."""
        response = await make_request(
            method="PUT",
            url=f"{PATH}/{temp_user.id}/roles/{temp_role.id}",
            jwt=superadmin_token,
        )
        assert response.status == HTTPStatus.OK

        user_roles = UserRolesBody(**response.body)
        assert temp_role in user_roles.roles
        logger.info("User and roles: %s", response.body)

    async def test_user_not_found(
        self,
        make_request,
        superadmin_token: str,
        temp_role: RoleBody,
    ):
        """Test grant roles with 404 exception."""
        random_id = uuid4()
        response = await make_request(
            method="PUT",
            url=f"{PATH}/{random_id}/roles/{temp_role.id}",
            jwt=superadmin_token,
        )
        assert response.status == HTTPStatus.NOT_FOUND

    async def test_role_not_found(
        self,
        make_request,
        superadmin_token: str,
        temp_user: UserBody,
    ):
        """Test grant an absent role."""
        response = await make_request(
            method="PUT",
            url=f"{PATH}/{temp_user.id}/roles/0",
            jwt=superadmin_token,
        )
        assert response.status == HTTPStatus.NOT_FOUND

    async def test_role_already_exists(
        self,
        make_request,
        superadmin_token: str,
        temp_role: RoleBody,
        temp_user: UserBody,
    ):
        """Test grant already existed role."""
        response = await make_request(
            method="PUT",
            url=f"{PATH}/{temp_user.id}/roles/{temp_role.id}",
            jwt=superadmin_token,
        )
        assert response.status == HTTPStatus.CONFLICT


class TestDeleteRole:
    """Test revoke role method."""

    async def test_revoke_role_success(
        self,
        make_request,
        superadmin_token: str,
        temp_role: RoleBody,
        temp_user: UserBody,
    ):
        """Test get users and roles list method with success."""
        response = await make_request(
            method="DELETE",
            url=f"{PATH}/{temp_user.id}/roles/{temp_role.id}",
            jwt=superadmin_token,
        )
        assert response.status == HTTPStatus.OK

        user_roles = UserRolesBody(**response.body)
        assert temp_role not in user_roles.roles
        logger.info("User and roles: %s", response.body)

    async def test_user_not_found(
        self,
        make_request,
        superadmin_token: str,
        temp_role: RoleBody,
    ):
        """Test grant the role for absent user."""
        random_id = uuid4()
        response = await make_request(
            method="DELETE",
            url=f"{PATH}/{random_id}/roles/{temp_role.id}",
            jwt=superadmin_token,
        )
        assert response.status == HTTPStatus.NOT_FOUND

    async def test_role_not_found(
        self,
        make_request,
        superadmin_token: str,
        temp_user: UserBody,
    ):
        """Test grant an absent role."""
        response = await make_request(
            method="DELETE",
            url=f"{PATH}/{temp_user.id}/roles/0",
            jwt=superadmin_token,
        )
        assert response.status == HTTPStatus.NOT_FOUND

    async def test_role_is_not_granted(
        self,
        make_request,
        superadmin_token: str,
        temp_role: RoleBody,
        temp_user: UserBody,
    ):
        """Test revoking not granted role."""
        response = await make_request(
            method="DELETE",
            url=f"{PATH}/{temp_user.id}/roles/{temp_role.id}",
            jwt=superadmin_token,
        )
        assert response.status == HTTPStatus.CONFLICT
