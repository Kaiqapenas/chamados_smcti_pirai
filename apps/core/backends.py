from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class MatriculaBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        matricula = username or kwargs.get("matricula")
        try:
            user = User.objects.get(matricula=matricula)
        except User.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user