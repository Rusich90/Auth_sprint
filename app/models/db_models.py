import uuid
from datetime import datetime

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import check_password_hash, generate_password_hash

from ..core.alchemy import db

users_roles = db.Table(
    "users_roles",
    db.Model.metadata,
    db.Column("user_id", db.ForeignKey("users.id")),
    db.Column("role_id", db.ForeignKey("roles.id")),
)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    is_superuser = db.Column(db.Boolean, unique=False, default=False)
    roles = db.relationship("Role", secondary=users_roles, back_populates="users")

    def __repr__(self):
        return f"<User {self.login}>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    users = db.relationship("User", secondary=users_roles, back_populates="roles")

    def __repr__(self):
        return f"<Role {self.name}>"


class Session(db.Model):
    __tablename__ = "sessions"
    __table_args__ = (
        UniqueConstraint("id", "auth_date"),
        {
            "postgresql_partition_by": "Range (auth_date)",
        },
    )

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("sessions", lazy=True))
    user_agent = db.Column(db.String)
    auth_date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        primary_key=True,
    )

    def __repr__(self):
        return f"<Session User {self.user.login}>"


class SocialAccount(db.Model):
    __tablename__ = "social_account"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False)
    user = db.relationship(User, backref=db.backref("social_accounts", lazy=True))

    social_id = db.Column(db.Text, nullable=False)
    social_name = db.Column(db.Text, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("social_id", "social_name", name="social_pk"),
    )

    def __repr__(self):
        return f"<SocialAccount {self.social_name}:{self.user_id}>"
