from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False
    )

    class Meta:
        model = User
        fields = ['matricula', 'telefone', 'password', 'is_active', 'is_staff', 'is_superuser'] 
        widgets = {
            'is_active': forms.CheckboxInput(),
            'is_staff': forms.CheckboxInput(),
            'is_superuser': forms.CheckboxInput()
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
    
    
