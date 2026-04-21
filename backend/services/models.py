from django.db import models


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    icon = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        return self.name
