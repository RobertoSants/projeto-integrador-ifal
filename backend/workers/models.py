from django.db import models
from django.contrib.auth import get_user_model
from services.models import ServiceCategory

User = get_user_model()


class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="worker_profile")
    full_name = models.CharField(max_length=200)
    bio = models.TextField(blank=True, default="")
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    photo = models.ImageField(upload_to="fotos/", blank=True, null=True)
    services = models.ManyToManyField(ServiceCategory, blank=True, related_name="workers")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def avg_rating(self):
        reviews = self.reviews.all()
        if not reviews.exists():
            return None
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)

    def __str__(self):
        return self.full_name
