from django import forms
from .models import Chamado, ItemChamado

class ChamadoForm(forms.ModelForm):
    class Meta:
        model = Chamado
        fields = [
            "solicitante",
            "para_onde_solicitou", 
            "titulo", 
            "descricao", 
            "urgencia",
            "status"
            ]
        
        
class ItemChamadoForm(forms.ModelForm):
    class Meta:
        model = ItemChamado
        fields = ["item", "quantidade"]