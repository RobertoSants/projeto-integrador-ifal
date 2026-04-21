from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    city = models.CharField(max_length=100, blank=True, default="")
    state = models.CharField(max_length=2, blank=True, default="")

    def __str__(self):
        return self.username
