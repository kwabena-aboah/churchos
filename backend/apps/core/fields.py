import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.functional import cached_property


class EncryptedCharField(models.CharField):
    prefix = "fernet:v1:"

    @cached_property
    def fernet(self):
        configured_key = (
            getattr(settings, "AI_CREDENTIALS_ENCRYPTION_KEY", "")
            or settings.SECRET_KEY
        )
        key = base64.urlsafe_b64encode(
            hashlib.sha256(configured_key.encode("utf-8")).digest()
        )
        return Fernet(key)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value in (None, ""):
            return value
        token = self.fernet.encrypt(value.encode("utf-8")).decode("ascii")
        return f"{self.prefix}{token}"

    def from_db_value(self, value, expression, connection):
        if value in (None, ""):
            return value
        if not value.startswith(self.prefix):
            return value
        try:
            token = value[len(self.prefix):].encode("ascii")
            return self.fernet.decrypt(token).decode("utf-8")
        except (InvalidToken, UnicodeDecodeError) as exc:
            raise ImproperlyConfigured(
                "Could not decrypt an AI credential. Check that "
                "AI_CREDENTIALS_ENCRYPTION_KEY has not changed."
            ) from exc
