from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Count, Q
from datetime import datetime
from django.contrib.auth import get_user_model

from apps.chamados.models import Chamado
from apps.estoque.models import ItemEstoque, MovimentacaoEstoque

User = get_user_model()


class RelatorioGraficoView(LoginRequiredMixin, TemplateView):
    template_name = "relatorios/relatorio_grafico.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['chamados_abertos'] = Chamado.objects.filter(
            status__in=['AB', 'EA']
        ).count()
        
        context['itens_estoque'] = ItemEstoque.objects.count()
        
        context['tecnicos_ativos'] = User.objects.filter(
            is_active=True,
            is_tecnico=True,
            ativo=True
        ).count()
        
        mes_atual = datetime.now()
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        context['mes_referencia'] = f"{meses[mes_atual.month]}/{mes_atual.year}"
        
        modificacoes = []
        for mov in MovimentacaoEstoque.objects.select_related('item', 'usuario').order_by('-data_movimentacao')[:10]:
            modificacoes.append({
                'item': mov.item.nome,
                'acao': f"{mov.get_tipo_display()} ({'+' if mov.tipo == 'EN' else '-'}{mov.quantidade})",  # type: ignore[attr-defined]
                'tipo': 'entrada' if mov.tipo == 'EN' else 'retirada',  # cspell:ignore tipo
                'usuario': mov.usuario.get_full_name() or mov.usuario.username,
                'data_hora': mov.data_movimentacao.strftime('%d/%m %H:%M')
            })
        context['modificacoes'] = modificacoes
        
        import json
        from django.db.models import Sum
        
        consumo_qs = MovimentacaoEstoque.objects.filter(
            tipo='SA'
        ).values('item__nome').annotate(total=Sum('quantidade')).order_by('-total')[:5]
        
        consumo_labels = [c['item__nome'] for c in consumo_qs]
        consumo_valores = [c['total'] for c in consumo_qs]
        
        entradas = MovimentacaoEstoque.objects.filter(tipo='EN').aggregate(total=Sum('quantidade'))['total'] or 0
        saidas = MovimentacaoEstoque.objects.filter(tipo='SA').aggregate(total=Sum('quantidade'))['total'] or 0
        
        context['consumo_labels'] = json.dumps(consumo_labels)
        context['consumo_valores'] = json.dumps(consumo_valores)
        
        context['pizza_labels'] = json.dumps(['Entradas', 'Saídas'])
        context['pizza_valores'] = json.dumps([entradas, saidas])
        
        return context