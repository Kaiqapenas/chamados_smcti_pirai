from django import forms
from django.contrib.auth import get_user_model

from .models import Chamado, ItemChamado

User = get_user_model()

INPUT_CLASS = "input-field"


class ChamadoForm(forms.ModelForm):
    class Meta:
        model = Chamado
        fields = [
            "solicitante",
            "titulo",
            "descricao",
            "urgencia",
            "para_onde_solicitou",
            "tecnico",
            "data_prevista",
        ]
        widgets = {
            "solicitante": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Nome do solicitante",
                }
            ),
            "para_onde_solicitou": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Secretaria — Sala 101",
                }
            ),
            "titulo": forms.TextInput(
                attrs={
                    "class": INPUT_CLASS,
                    "placeholder": "Preencher qual manutenção",
                }
            ),
            "descricao": forms.Textarea(
                attrs={
                    "class": f"{INPUT_CLASS} textarea-field",
                    "placeholder": "Descrição do problema",
                    "rows": 6,
                }
            ),
            "urgencia": forms.HiddenInput(),
            "tecnico": forms.Select(attrs={"class": INPUT_CLASS}),
            "data_prevista": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "class": INPUT_CLASS,
                    "type": "date",
                }
            ),
        }
        labels = {
            "para_onde_solicitou": "Endereço",
            "titulo": "Tipo de manutenção",
            "urgencia": "Prioridade",
            "data_prevista": "Prazo desejado",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tecnico"].queryset = User.objects.filter(
            is_active=True, is_tecnico=True
        )
        self.fields["tecnico"].required = False
        self.fields["tecnico"].empty_label = "Selecione..."
        self.fields["data_prevista"].required = False
        self.fields["data_prevista"].input_formats = ["%Y-%m-%d"]

        self.fields["urgencia"].required = False
        if self.is_bound and not self.data.get("urgencia"):
            data = self.data.copy()
            data["urgencia"] = Chamado.Urgencia.NORMAL
            self.data = data
        elif not self.is_bound:
            self.fields["urgencia"].initial = Chamado.Urgencia.NORMAL

    def clean_urgencia(self):
        return self.cleaned_data.get("urgencia") or Chamado.Urgencia.NORMAL


class ItemChamadoForm(forms.ModelForm):
    class Meta:
        model = ItemChamado
        fields = ["item", "quantidade"]
