import uuid

from django.db import models

from lists.models import List


class User(models.Model):
    email = models.EmailField(primary_key=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"
    is_anonymous = False
    is_authenticated = True

    shared_lists = models.ManyToManyField(
        List,
        related_name="shared_with",
        blank=True,
    )


class Token(models.Model):
    email = models.EmailField()
    uid = models.CharField(default=uuid.uuid4, max_length=40)
