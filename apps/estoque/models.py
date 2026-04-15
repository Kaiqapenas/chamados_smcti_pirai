from django.db import models

# Create your models here.
#
# Rascunho inicial, temporário
#
class ItemEstoque(models.Model):
    class unidade_medida(models.TextChoices):
        UNIDADE = "UN", "Unidade"
        METRO = "M", "Metro"

    nome = models.CharField("Nome", max_length=200)
    quantidade = models.IntegerField("Quantidade", default=0)
    quantidade_minima = models.IntegerField("Quantidade Mínima", default=0)
    unidade_medida = models.CharField(
        "Unidade de Medida",
        max_length=2,
        choices=unidade_medida.choices,
        default=unidade_medida.UNIDADE,
    )
    descricao = models.TextField("Descrição")
    marca = models.CharField("Marca", max_length=200)
    modelo = models.CharField("Modelo", max_length=200)
    serie = models.CharField("Série", max_length=200)
    patrimonio = models.IntegerField("Patrimônio", default=0)
    ativo = models.BooleanField("Ativo", default=True)
    categoria = models.ForeignKey(
        "CategoriaItem",
        on_delete=models.CASCADE, 
        related_name="itens_estoque"
    )
    imagem = models.ImageField(
        "Imagem", 
        upload_to="estoque/", 
        null=True, 
        blank=True
        )

    
    data_criacao = models.DateTimeField("Data de Criação", auto_now_add=True)
    ultima_edicao = models.DateTimeField("Última edição", auto_now=True)

    class Meta:
        verbose_name = "Item de Estoque"
        verbose_name_plural = "Itens de Estoque"
        ordering = ["-data_criacao"]

    def __str__(self):
        return f"[{self.get_unidade_medida_display()}] {self.nome}"
    
class CategoriaItem(models.Model):
    nome = models.CharField("Nome", max_length=200)

    def __str__(self):
        return self.nome