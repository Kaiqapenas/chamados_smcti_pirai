from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, matricula, password=None, **extra_fields):
        if not matricula:
            raise ValueError("The 'matricula' field must be set.")

        user = self.model(matricula=matricula, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, matricula, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(matricula=matricula, password=password, **extra_fields)


class User(AbstractUser):
    username = None
    matricula = models.CharField(max_length=30, unique=True)
    telefone = models.CharField(max_length=30, blank=True, null=True)
    setor = models.CharField("Setor", max_length=100, blank=True, null=True)
    ativo = models.BooleanField("Ativo", default=True)

    USERNAME_FIELD = "matricula"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return f"{self.matricula} - {self.first_name}"


class TipoEvento(models.TextChoices):
    LOGIN = 'LOGIN', 'Login realizado'
    LOGIN_FALHA = 'LOGIN_FALHA', 'Falha de login'
    LOGOUT = 'LOGOUT', 'Logout realizado'
    ACESSO = 'ACESSO', 'Acesso a página'
    CRIACAO = 'CRIACAO', 'Criação de registro'
    EDICAO = 'EDICAO', 'Edição de registro'
    EXCLUSAO = 'EXCLUSAO', 'Exclusão de registro'


class AuditoriaLog(models.Model):
    tipo = models.CharField(
        max_length=20,
        choices=TipoEvento.choices,
        verbose_name='Tipo de Evento',
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs_auditoria',
        verbose_name='Usuário',
    )
    matricula_tentativa = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name='Matrícula (tentativa)',
    )
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='Endereço IP')
    data = models.DateTimeField(auto_now_add=True, verbose_name='Data/Hora')

    class Meta:
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering = ['-data']

    def __str__(self):
        ator = self.usuario or self.matricula_tentativa or 'Desconhecido'
        return f"[{self.tipo}] {ator} — {self.data:%d/%m/%Y %H:%M}"
