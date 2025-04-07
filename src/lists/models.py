from django.conf import settings
from django.db import models
from django.urls import reverse


class Item(models.Model):
    text = models.TextField(default="")
    list = models.ForeignKey("List", default=None, on_delete=models.CASCADE)

    class Meta:
        ordering = ("id",)
        unique_together = ("list", "text")

    def __str__(self):
        return self.text


class List(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="lists",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def get_absolute_url(self):
        return reverse("view_list", args=[self.id])
