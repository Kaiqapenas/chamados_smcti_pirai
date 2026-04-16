from django.db import models

#
# Rascunho inicial, temporário
#
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
    ultima_edicao = models.DateTimeField("Última edição", auto_now=True)

    class Meta:
        verbose_name = "Chamado"
        verbose_name_plural = "Chamados"
        ordering = ["-data_criacao"]

    def __str__(self):
        return f"[{self.get_status_display()}] {self.titulo}"
    
class ItemChamado(models.Model):
    chamado = models.ForeignKey(
        Chamado, 
        on_delete=models.CASCADE, 
        related_name="itens"
    )
   
    item = models.ForeignKey(
        "estoque.ItemEstoque",
        on_delete=models.CASCADE,
        related_name="chamados"
    )
    quantidade = models.PositiveIntegerField("Quantidade", default=1)

    class Meta:
        verbose_name = "Item do Chamado"
        verbose_name_plural = "Itens dos Chamados"

    def __str__(self):
        return self.item.nome

class AlteracaoChamado(models.Model):
    chamado = models.ForeignKey(
        Chamado, 
        on_delete=models.CASCADE, 
        related_name="alteracoes"
    )
    descricao = models.TextField("Descrição da Alteração")
    data_alteracao = models.DateTimeField("Data da Alteração", auto_now_add=True)
    status_anterior = models.CharField(
        "Status Anterior",
        max_length=2,
        choices=Chamado.Status.choices
    )
    status_novo = models.CharField(
        "Status Novo",
        max_length=2,
        choices=Chamado.Status.choices
    )

    class Meta:
        verbose_name = "Alteração de Chamado"
        verbose_name_plural = "Alterações de Chamados"
        ordering = ["-data_alteracao"]

    def __str__(self):
        return f"Alteração em {self.chamado.titulo} - {self.data_alteracao.strftime('%Y-%m-%d %H:%M:%S')}"