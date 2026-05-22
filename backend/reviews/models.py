from django.db import models
from django.contrib.auth import get_user_model
from workers.models import Worker

User = get_user_model()


class Review(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="reviews")
    # ALTERAÇÃO CIRÚRGICA: Permite valores nulos no banco de dados para suportar avaliações de visitantes anônimos
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_given", null=True, blank=True)
    rating = models.IntegerField()
    comment = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Tratamento simples para exibição no painel administrativo caso seja anônimo
        autor_nome = self.author.username if self.author else "Anônimo"
        return f"Review de {autor_nome} para {self.worker} — {self.rating}★"