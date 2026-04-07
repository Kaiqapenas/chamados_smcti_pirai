from django.db import models


class Chamado(models.Model):
    class Status(models.TextChoices):
        ABERTO = "AB", "Aberto"
        EM_ANDAMENTO = "EA", "Em Andamento"
        FINALIZADO = "FI", "Finalizado"

    titulo = models.CharField("Título", max_length=200)
    descricao = models.TextField("Descrição")
    status = models.CharField(
        "Status",
        max_length=2,
        choices=Status.choices,
        default=Status.ABERTO,
    )
    data_criacao = models.DateTimeField("Data de Criação", auto_now_add=True)

    class Meta:
        verbose_name = "Chamado"
        verbose_name_plural = "Chamados"
        ordering = ["-data_criacao"]

    def __str__(self):
        return f"[{self.get_status_display()}] {self.titulo}"
