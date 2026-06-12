from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.estoque.models import ItemEstoque

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
        widgets = {
            "item": forms.Select(attrs={"class": INPUT_CLASS}),
            "quantidade": forms.NumberInput(
                attrs={"class": INPUT_CLASS, "min": 1}
            ),
        }
        labels = {
            "item": "Item do estoque",
            "quantidade": "Quantidade",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = ItemEstoque.objects.filter(ativo=True).order_by("nome")
        if self.instance and self.instance.pk:
            used_ids = ItemChamado.objects.filter(
                chamado=self.instance.chamado
            ).exclude(pk=self.instance.pk).values_list("item_id", flat=True)
            queryset = queryset.exclude(pk__in=used_ids)
        self.fields["item"].queryset = queryset
        self.fields["item"].empty_label = "Selecione..."


class ItemChamadoRowForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=ItemEstoque.objects.filter(ativo=True).order_by("nome"),
        required=False,
        empty_label="Selecione...",
        widget=forms.Select(attrs={"class": INPUT_CLASS}),
        label="Item do estoque",
    )
    quantidade = forms.IntegerField(
        required=False,
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={"class": INPUT_CLASS, "min": 1}),
        label="Quantidade",
    )

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get("item")
        quantidade = cleaned_data.get("quantidade")

        if not item:
            cleaned_data["item"] = None
            cleaned_data["quantidade"] = None
            return cleaned_data

        if not quantidade or quantidade < 1:
            self.add_error("quantidade", "Informe uma quantidade válida.")

        return cleaned_data


class BaseItemChamadoFormSet(forms.BaseFormSet):
    def __init__(self, *args, chamado=None, **kwargs):
        self.chamado = chamado
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        if any(self.errors):
            return

        filled_rows = [
            form.cleaned_data
            for form in self.forms
            if form.cleaned_data and form.cleaned_data.get("item")
        ]

        if not filled_rows:
            raise ValidationError("Adicione pelo menos um item.")

        if not self.chamado:
            return

        items_by_id = {}
        for row in filled_rows:
            item = row["item"]
            if item.pk in items_by_id:
                raise ValidationError(
                    f"O item '{item.nome}' foi selecionado mais de uma vez. "
                    "Cada produto deve aparecer apenas uma vez."
                )
            items_by_id[item.pk] = row["quantidade"]

        existing_ids = set(
            self.chamado.itens.values_list("item_id", flat=True)
        )
        already_on_chamado = [
            row["item"].nome
            for row in filled_rows
            if row["item"].pk in existing_ids
        ]
        if already_on_chamado:
            raise ValidationError(
                "Estes itens já estão no chamado: "
                + ", ".join(dict.fromkeys(already_on_chamado))
                + "."
            )

        self.merged_items = items_by_id


ItemChamadoFormSet = forms.formset_factory(
    ItemChamadoRowForm,
    formset=BaseItemChamadoFormSet,
    extra=1,
    min_num=0,
    validate_min=False,
)
