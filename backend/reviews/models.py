from django.db import models
from django.contrib.auth import get_user_model
from workers.models import Worker

User = get_user_model()


class Review(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_given")
    rating = models.IntegerField()
    comment = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review de {self.author} para {self.worker} — {self.rating}★"
