from django import forms
from .models import ItemEstoque, CategoriaItem, MovimentacaoEstoque

class ItemEstoqueForm(forms.ModelForm):
    class Meta:
        model = ItemEstoque
        fields = ['nome', 'quantidade', 'quantidade_minima', 'unidade_medida',
                  'descricao', 'marca', 'modelo', 'serie', 'patrimonio', 'categoria', 'ativo']
        
class CategoriaItemForm(forms.ModelForm):
    class Meta:
        model = CategoriaItem
        fields = ["nome"]


class MovimentacaoEstoqueForm(forms.ModelForm):
    class Meta:
        model = MovimentacaoEstoque
        fields = ["item", "tipo", "quantidade", "observacao", "protocolo"]