from django.db import models
from django.contrib.auth import get_user_model
from services.models import ServiceCategory
from datetime import date

User = get_user_model()

class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="worker_profile")
    full_name = models.CharField(max_length=200)
    birth_date = models.DateField()  # NOVO CAMPO: Armazenamento da Data de Nascimento
    bio = models.TextField(blank=True, default="")
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    photo = models.ImageField(upload_to="fotos/", blank=True, null=True)
    services = models.ManyToManyField(ServiceCategory, blank=True, related_name="workers")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def age(self):
        """Calcula dinamicamente a idade atual baseada no ano corrente (2026)"""
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    @property
    def avg_rating(self):
        if hasattr(self, "_avg_rating"):
            if self._avg_rating is not None:
                return round(float(self._avg_rating), 2)
            return None
        reviews = self.reviews.all()
        if not reviews.exists():
            return None
        return round(sum(r.rating for r in reviews) / reviews.count(), 2)

    @avg_rating.setter
    def avg_rating(self, value):
        if value is not None:
            self._avg_rating = round(float(value), 2)
        else:
            self._avg_rating = None

    def __str__(self):
        return self.full_name