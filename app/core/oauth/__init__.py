__all__ = [
    "OAuthSignIn",
    "GoogleSignIn",
    "MailSignIn",
    "VkontakteSignIn",
    "YandexSignIn",
]

from .base import OAuthSignIn
from .google import GoogleSignIn
from .mail import MailSignIn
from .vk import VkontakteSignIn
from .yandex import YandexSignIn
