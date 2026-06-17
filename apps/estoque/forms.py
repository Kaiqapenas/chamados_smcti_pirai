from django import forms
from .models import ItemEstoque, CategoriaItem, MovimentacaoEstoque, RequisicaoPeca

class ItemEstoqueForm(forms.ModelForm):
    class Meta:
        model = ItemEstoque
        fields = ["nome", "quantidade", "quantidade_minima", "unidade_medida",
                  "descricao", "marca", "modelo", "serie", "patrimonio", "categoria", "ativo"]
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # 👉 se for edição (tem instance)
            if self.instance and self.instance.pk:
                self.fields['quantidade'].disabled = True
                
        def clean_quantidade(self):
            if self.instance and self.instance.pk:
                return self.instance.quantidade
            return self.cleaned_data['quantidade']
            
class CategoriaItemForm(forms.ModelForm):
    class Meta:
        model = CategoriaItem
        fields = ["nome", "descricao"]


class MovimentacaoEstoqueForm(forms.ModelForm):
    class Meta:
        model = MovimentacaoEstoque
        fields = ["item", "tipo", "quantidade", "observacao", "protocolo"]
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # 👉 se for edição (tem instance)
            if self.instance and self.instance.pk:
                self.fields['tipo'].disabled = True
                
        def clean_tipo(self):
            if self.instance and self.instance.pk:
                return self.instance.tipo
            return self.cleaned_data['tipo']

class RequisicaoPecaForm(forms.ModelForm):
    class Meta:
        model = RequisicaoPeca
        fields = ['chamado', 'item_solicitado', 'quantidade', 'urgencia', 'justificativa']
        widgets = {
            'chamado': forms.Select(attrs={'class': 'form-select'}),
            'item_solicitado': forms.Select(attrs={'class': 'form-select'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'urgencia': forms.HiddenInput(),
            'justificativa': forms.Textarea(attrs={
                'class': 'justificativa-box',
                'rows': 4,
                'placeholder': 'Necessário para manutenção...'
            }),
        }

    def __init__(self, *args, **kwargs):
        # Recebe o usuário passado pela view
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

        if usuario is not None:
            from apps.chamados.models import Chamado
            # Filtra apenas os chamados atribuídos ao técnico logado
            # e que não estejam finalizados
            self.fields['chamado'].queryset = Chamado.objects.filter(
                tecnico=usuario
            ).exclude(status='FI')