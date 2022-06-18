from enum import Enum, auto


class AutoName(Enum):
    """Represents Enum with automatic naming."""

    def _generate_next_value_(self, start, count, last_values):
        """Generate value similar to attr name."""
        return self


class DefaultRole(AutoName):
    """Represents default roles."""

    banned = auto()
    visitor = auto()
    user = auto()
    subscribed = auto()
    admin = auto()
    superadmin = auto()


class Provider(AutoName):
    google = auto()
    mail = auto()
    vkontakte = auto()
    yandex = auto()
