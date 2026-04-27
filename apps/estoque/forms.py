from django import forms
from .models import ItemEstoque, CategoriaItem, MovimentacaoEstoque

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