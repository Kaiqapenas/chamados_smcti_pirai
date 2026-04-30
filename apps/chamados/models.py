from django.conf import settings
from django.db import models, transaction
from django.core.exceptions import ValidationError
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

    TRANSICOES_VALIDAS = {
        Status.ABERTO: [Status.EM_ANDAMENTO],
        Status.EM_ANDAMENTO: [Status.FINALIZADO],
        Status.FINALIZADO: [],  # chamado finalizado não pode ser reaberto
    }

    #protocolo gerado automaticamente, unico e nao editavel
    numero_protocolo = models.CharField(
        "Protocolo",
        max_length=12,
        unique=True,
        default=gerar_protocolo,
        editable=False,
    )

    #informacoes do solicitante
    solicitante = models.CharField(
        "Solicitante",
        max_length=200,
        help_text="Nome do solicitante ou órgão"
    )
    para_onde_solicitou = models.CharField("Para onde solicitou", max_length=200)
    
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
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="chamados_usuario",
        verbose_name="Usuário de interação"
    )

    # TODO: adicionar após implementar app de usuários
    # tecnicos = models.ManyToManyField(
    #     "usuarios.Usuario",
    #     verbose_name="Técnicos",
    #     related_name="chamados",
    #     blank=True
    # )

    #datas
    data_criacao = models.DateTimeField("Data de abertura", auto_now_add=True)
    #prazo:
    data_prevista = models.DateField("Data prevista", null=True, blank=True)
    #ultima edicao pra auditoria
    ultima_edicao = models.DateTimeField("Última edição", auto_now=True)
    class Meta:
        verbose_name = "Chamado"
        verbose_name_plural = "Chamados"
        ordering = ["-data_criacao"]

    def __str__(self):
        return f"[{self.numero_protocolo}] {self.titulo}"
    

    def _validar_estoque(self):
        """Verifica se todos os itens do chamado têm estoque suficiente para finalizar."""
        erros = []
        for item_chamado in self.itens.select_related("item").all():
            if item_chamado.quantidade > item_chamado.item.quantidade:
                erros.append(
                    f"'{item_chamado.item.nome}': necessário {item_chamado.quantidade}, "
                    f"disponível {item_chamado.item.quantidade}."
                    )
        if erros:
            raise ValidationError(
            "Estoque insuficiente para finalizar o chamado:\n" + "\n".join(erros)
            )
    
    def _dar_baixa_estoque(self):
        from apps.estoque.models import MovimentacaoEstoque
        for item_chamado in self.itens.select_related("item").all():
            MovimentacaoEstoque.objects.create(
                item=item_chamado.item,
                tipo=MovimentacaoEstoque.TipoMovimentacao.SAIDA,
                quantidade=item_chamado.quantidade,
                protocolo=self,
                observacao=f"Baixa automática ao finalizar chamado {self.numero_protocolo}"
            )
            # item.quantidade é atualizado pelo save() da MovimentacaoEstoque
    
    def mudar_status(self, novo_status):
        """Muda o status do chamado respeitando as transições válidas."""
        transicoes = self.TRANSICOES_VALIDAS.get(self.status, [])

        if novo_status not in transicoes:
            raise ValidationError(
                f"Não é possível alterar de '{self.get_status_display()}' "
                f"para '{dict(self.Status.choices)[novo_status]}'."
            )

        # Valida estoque antes de finalizar
        if novo_status == self.Status.FINALIZADO:
            self._validar_estoque()

        status_anterior = self.status
        self.status = novo_status
        self.save()

        # Baixa no estoque ao finalizar
        if novo_status == self.Status.FINALIZADO:
            self._dar_baixa_estoque()

        AlteracaoChamado.objects.create(
            chamado=self,
            status_anterior=status_anterior,
            status_novo=novo_status,
            descricao=f"Status alterado para {self.get_status_display()}"
        )

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

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="chamados_item_usuario",
        verbose_name="Usuário de interação no item"
    )

    class Meta:
        verbose_name = "Item do chamado"
        verbose_name_plural = "Itens do chamado"
        unique_together = ("chamado", "item") #nao pode ter o msm item mais de uma vez no chamado, mas a qntd pode ser maior q 1

    def __str__(self):
        return f"{self.item.nome} ({self.quantidade})"
    
    def clean(self):
        # Não permite modificar itens de chamado finalizado
        if self.chamado.status == Chamado.Status.FINALIZADO:
            raise ValidationError("Não é possível modificar itens de um chamado finalizado.")
        # Quantidade deve ser maior que zero
        if self.quantidade <= 0:
            raise ValidationError("Quantidade deve ser maior que zero.")
    
    def delete(self, *args, **kwargs):
        # Não permite remover itens de chamado finalizado
        if self.chamado.status == Chamado.Status.FINALIZADO:
            raise ValidationError("Não é possível remover itens de um chamado finalizado.")
        super().delete(*args, **kwargs)


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
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="chamados_alteracoes_usuario",
        verbose_name="Usuário de interação na alteração"
    )
    
    class Meta:
        verbose_name = "Alteração de chamado"
        verbose_name_plural = "Alterações de chamados"
        ordering = ["-data_alteracao"]

    def __str__(self):
        return f"[{self.chamado.numero_protocolo}] {self.data_alteracao.strftime('%d/%m/%Y %H:%M')}"
