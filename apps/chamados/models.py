from django.db import models
import random
import string
from django.utils import timezone

#
# Rascunho inicial, temporário
#

def gerar_protocolo():
    """Gera um numero de protocolo no formato ANOMESxxxxxx"""
    ano_mes = timezone.now().strftime("%Y%m")
    sufixo = ''.join(random.choices(string.digits, k=6))
    protocolo = f"{ano_mes}{sufixo}"
    # n vai ter colisao
    while Chamado.objects.filter(numero_protocolo=protocolo).exists():
        sufixo = ''.join(random.choices(string.digits, k=6))
        protocolo = f"{ano_mes}{sufixo}"
    return protocolo

class Chamado(models.Model):
    class Status(models.TextChoices):
        ABERTO = "AB", "Aberto"
        EM_ANDAMENTO = "EA", "Em andamento"
        FINALIZADO = "FI", "Finalizado"

    class Urgencia(models.TextChoices):
        NORMAL = "NO", "Normal"
        URGENTE = "UR", "Urgente"

    #protocolo gerado automaticamente, unico e nao editavel
    numero_protocolo = models.CharField(
        "Protocolo",
        max_length=12,
        unique=True,
        default=gerar_protocolo,
        editable=False,
    )

    #informacoes do solicitante
    solicitante = models.CharField("Solicitante", max_length=200)
    #informacoes do chamado
    titulo = models.CharField("Título", max_length=200)
    descricao = models.TextField("Descrição")
    urgencia = models.CharField(
        "Urgência",
        max_length=2,
        choices=Urgencia.choices,
        default=Urgencia.NORMAL
    )
    status = models.CharField(
        "Status",
        max_length=2,
        choices=Status.choices,
        default=Status.ABERTO,
    )

    #datas
    data_criacao = models.DateTimeField("Data de abertura", auto_now_add=True)

    class Meta:
        verbose_name = "Chamado"
        verbose_name_plural = "Chamados"
        ordering = ["-data_criacao"]

    def __str__(self):
        return f"[{self.numero_protocolo}] {self.titulo}"
    
class ItemChamado(models.Model):
    #peças requisitadas pro chamado
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
        verbose_name = "Item do chamado"
        verbose_name_plural = "Itens dos chamados"

    def __str__(self):
        return self.item.nome

class AlteracaoChamado(models.Model):
    #historico de alterações do chamado
    chamado = models.ForeignKey(
        Chamado, 
        on_delete=models.CASCADE, 
        related_name="alteracoes"
    )
    descricao = models.TextField("Descrição da alteração")

    # Rastreia a transição de status para auditoria
    status_anterior = models.CharField(
        "Status anterior",
        max_length=2,
        choices=Chamado.Status.choices
    )
    
    status_novo = models.CharField(
        "Status novo",
        max_length=2,
        choices=Chamado.Status.choices
    )

    data_alteracao = models.DateTimeField("Data da alteração", auto_now_add=True)
    class Meta:
        verbose_name = "Alteração de chamado"
        verbose_name_plural = "Alterações de chamados"
        ordering = ["-data_alteracao"]

    def __str__(self):
        return f"[{self.chamado.numero_protocolo}] {self.data_alteracao.strftime('%d/%m/%Y %H:%M')}"
