from django.contrib.auth.models import (
    AbstractBaseUser,
)
from django.db import models

from superlists import settings


STAFF_EMAIL = settings.DEFAULT_FROM_EMAIL


class Token(models.Model):
    email = models.EmailField()
    uid = models.CharField(max_length=255)


class ListUser(AbstractBaseUser):
    email = models.EmailField(primary_key=True)
    USERNAME_FIELD = "email"

    @property
    def is_staff(self):
        return self.email == STAFF_EMAIL

    @property
    def is_active(self):
        return True
