import logging
from http import HTTPStatus

import pytest

from app.core.enums import DefaultRole
from app.serializers.roles import RoleBody

logger = logging.getLogger(__name__)
pytestmark = pytest.mark.asyncio

PATH = "/api/v1/roles"


class TestGetRoles:
    """Test roles GET method"""

    async def test_get_roles_list_success(self, make_request, superadmin_token):
        """Test get roles list method with success."""
        response = await make_request(
            method="GET",
            url=f"{PATH}/",
            jwt=superadmin_token,
        )
        assert response.status == HTTPStatus.OK
        logger.info("Roles: %s", response.body)


class TestCreateRole:
    """Test create role method."""

    async def test_success(self, make_request, superadmin_token):
        """Test create role method with success."""
        target_role = RoleBody(id=1, name=DefaultRole.admin.value)
        response = await make_request(
            method="POST",
            url=f"{PATH}/",
            json=target_role.dict(),
            jwt=superadmin_token,
        )
        assert response.status == HTTPStatus.CREATED
        assert target_role == RoleBody(**response.body)

    async def test_already_exists(self, make_request, superadmin_token):
        """Test create role method with already exists exception."""
        target_role = RoleBody(id=1, name=DefaultRole.admin.value)
        response = await make_request(
            method="POST",
            url=f"{PATH}/",
            json=target_role.dict(),
            jwt=superadmin_token,
        )
        assert response.status == HTTPStatus.CONFLICT


class TestUpdateRole:
    """Test update role method."""

    target_role = RoleBody(id=1, name=DefaultRole.subscribed.value)

    async def test_success(self, make_request, superadmin_token):
        """Test update role method with success."""
        response = await make_request(
            method="PATCH",
            url=f"{PATH}/1/",
            json=self.target_role.dict(),
            jwt=superadmin_token,
        )
        assert response.status == HTTPStatus.OK
        assert self.target_role == RoleBody(**response.body)

    async def test_already_exists(self, make_request, superadmin_token):
        """Test update role method with success."""
        response = await make_request(
            method="PATCH",
            url=f"{PATH}/1/",
            json=self.target_role.dict(),
            jwt=superadmin_token,
        )
        assert response.status == HTTPStatus.CONFLICT

    async def test_not_found(self, make_request, superadmin_token):
        """Test update role method with 404 exception."""
        response = await make_request(
            method="PATCH",
            url=f"{PATH}/0/",
            json=self.target_role.dict(),
            jwt=superadmin_token,
        )
        assert response.status == HTTPStatus.NOT_FOUND


class TestDeleteRole:
    """Test delete role method."""

    async def test_success(self, make_request, superadmin_token):
        """Test update role method with success."""
        response = await make_request(
            method="DELETE",
            url=f"{PATH}/1/",
            jwt=superadmin_token,
        )
        assert response.status == HTTPStatus.NO_CONTENT

    async def test_does_not_exists(self, make_request, superadmin_token):
        """Test update role method with 404 exception."""
        response = await make_request(
            method="DELETE",
            url=f"{PATH}/1/",
            jwt=superadmin_token,
        )
        assert response.status == HTTPStatus.NOT_FOUND
