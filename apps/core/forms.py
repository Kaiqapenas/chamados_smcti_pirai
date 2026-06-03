from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        help_text="Deixe em branco para manter a senha atual"
    )

    class Meta:
        model = User
        fields = [
            'matricula', 'first_name', 'last_name', 'email', 'telefone', 'setor',
            'password', 'ativo',
            'is_administrador', 'is_secretario', 'is_solicitante', 'is_tecnico', 'is_almoxarife',
            'is_active', 'is_staff', 'is_superuser'
        ]
        widgets = {
            'ativo': forms.CheckboxInput(),
            'is_administrador': forms.CheckboxInput(),
            'is_secretario': forms.CheckboxInput(),
            'is_solicitante': forms.CheckboxInput(),
            'is_tecnico': forms.CheckboxInput(),
            'is_almoxarife': forms.CheckboxInput(),
            'is_active': forms.CheckboxInput(),
            'is_staff': forms.CheckboxInput(),
            'is_superuser': forms.CheckboxInput()
        }
        help_texts = {
            'is_administrador': 'Acesso total ao sistema',
            'is_secretario': 'Acesso a chamados e relatórios',
            'is_solicitante': 'Pode criar novos chamados',
            'is_tecnico': 'Pode atender chamados atribuídos',
            'is_almoxarife': 'Gerencia estoque e movimentações',
        }

    def save(self, commit=True):
        user = super().save(commit=False)

        password = self.cleaned_data.get("password")

        if password:
            user.set_password(password)  # 🔐 HASH AQUI

        if commit:
            user.save()

        return user

    
        
class UserLoginForm(forms.Form):
    matricula = forms.CharField(label="Matrícula", max_length=30)
    password = forms.CharField(label="Senha", widget=forms.PasswordInput)
    
    
