from django.db import models, transaction
from django.core.exceptions import ValidationError

# Create your models here.
#
# Rascunho inicial, temporário
#

class ItemEstoque(models.Model):
    class UnidadeMedida(models.TextChoices):
        UNIDADE = "UN", "Unidade"
        METRO = "M", "Metro"

    nome = models.CharField("Nome", max_length=200)
    quantidade = models.PositiveIntegerField("Quantidade", default=1)
    quantidade_minima = models.PositiveIntegerField("Quantidade Mínima", default=0)
    unidade_medida = models.CharField(
        "Unidade de Medida",
        max_length=2,
        choices=UnidadeMedida.choices,
        default=UnidadeMedida.UNIDADE,
    )
    descricao = models.TextField("Descrição")
    marca = models.CharField(
        "Marca", 
        max_length=200,
        null=True, 
        blank=True
    )
    modelo = models.CharField(
        "Modelo", 
        max_length=200, 
        null=True, 
        blank=True
    )
    serie = models.CharField(
        "Série", 
        max_length=200,
        null=True, 
        blank=True
    )
    patrimonio = models.CharField(
        "Patrimônio", 
        max_length=200, 
        null=True, 
        blank=True
    )
    ativo = models.BooleanField("Ativo", default=True)
    categoria = models.ForeignKey(
        "CategoriaItem",
        on_delete=models.CASCADE, 
        related_name="itens_estoque"
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
    
class ItemImagem(models.Model):
    produto = models.ForeignKey(
        ItemEstoque,
        related_name='imagens',
        on_delete=models.CASCADE
    )
    imagem = models.ImageField(upload_to='estoque/')
    legenda = models.CharField(max_length=255, blank=True, null=True)
    ordem = models.IntegerField(default=0, db_index=True)
    is_principal = models.BooleanField(default=False)

    class Meta:
        ordering = ['ordem', 'id']
        unique_together = ('produto', 'ordem')

    def __str__(self):
        return f"Imagem de {self.produto.nome}"
    
class MovimentacaoEstoque(models.Model):
    class TipoMovimentacao(models.TextChoices):
        ENTRADA = "EN", "Entrada"
        SAIDA = "SA", "Saída"

    item = models.ForeignKey(
        "ItemEstoque",
        on_delete=models.CASCADE,
        related_name="movimentacoes"
    )

    protocolo = models.ForeignKey(
        "chamados.Chamado",
        on_delete=models.SET_NULL,
        related_name="movimentacoes_estoque",
        null=True,
        blank=True
    )

    tipo = models.CharField(
        "Tipo de Movimentação",
        max_length=2,
        choices=TipoMovimentacao.choices,
    )

    quantidade = models.PositiveIntegerField("Quantidade")

    data_movimentacao = models.DateTimeField(
        "Data da Movimentação",
        auto_now_add=True
    )

    observacao = models.TextField(
        "Observação",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Movimentação de Estoque"
        verbose_name_plural = "Movimentações de Estoque"
        ordering = ["-data_movimentacao"]
        indexes = [
            models.Index(fields=["item", "data_movimentacao"]),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.item.nome} ({self.quantidade})"

    # 🔍 VALIDAÇÃO DE NEGÓCIO
    def clean(self):
        if self.tipo == self.TipoMovimentacao.SAIDA:
            if self.item and self.item.quantidade < self.quantidade:
                raise ValidationError("Estoque insuficiente para saída.")

    # 🔁 SAVE COM CONTROLE TOTAL
    def save(self, *args, **kwargs):
        with transaction.atomic():

            # 🔍 saldo atual
            saldo = self.item.quantidade

            # 🔄 se for edição, desfaz movimentação antiga (EM MEMÓRIA)
            if self.pk:
                antiga = MovimentacaoEstoque.objects.get(pk=self.pk)

                if antiga.tipo == self.TipoMovimentacao.ENTRADA:
                    saldo -= antiga.quantidade
                else:
                    saldo += antiga.quantidade

            # 🔥 DEBUG AQUI
            print("=== DEBUG MOVIMENTAÇÃO ===")
            print("Item:", self.item)
            print("Saldo atual:", self.item.quantidade)
            print("Saldo após reversão:", saldo)
            print("Tipo novo:", self.tipo)
            print("Quantidade nova:", self.quantidade)
        
            # 🔥 simula nova movimentação (SEM salvar ainda)
            if self.tipo == self.TipoMovimentacao.ENTRADA:
                saldo += self.quantidade
            else:
                saldo -= self.quantidade

            # ❌ valida ANTES de qualquer save
            if saldo < 0:
                raise ValidationError("Estoque não pode ficar negativo.")

            # ✅ agora sim aplica no banco
            self.item.quantidade = saldo
            self.item.save()

            super().save(*args, **kwargs)    
    
    # 🗑️ DELETE COM REVERSÃO
    def delete(self, *args, **kwargs):
        with transaction.atomic():

            if self.tipo == self.TipoMovimentacao.ENTRADA:
                self.item.quantidade -= self.quantidade
            else:
                self.item.quantidade += self.quantidade

            self.item.save()

            super().delete(*args, **kwargs)