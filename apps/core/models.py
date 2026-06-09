from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings
from typing import ClassVar


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

class PerfilUsuario(models.Model):
    """Tabela dos 4 perfis do MVP """

    class Tipo(models.TextChoices):
        SOLICITANTE   = "SO", "Solicitante"  # type: ignore[assignment]
        SECRETARIO    = "SE", "Secretário"  # type: ignore[assignment]
        ALMOXARIFE    = "AL", "Almoxarife"  # type: ignore[assignment]
        TECNICO       = "TE", "Técnico"  # type: ignore[assignment]
        ADMINISTRADOR = "AD", "Administrador"  # type: ignore[assignment]

    tipo = models.CharField(  # cspell:ignore tipo
        "Tipo",
        max_length=2,
        choices=Tipo.choices,
        unique=True,
    )

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

    def __str__(self) -> str:
        return self.get_tipo_display()  # type: ignore[attr-defined]
class User(AbstractUser):

    username = None
    matricula = models.CharField(max_length=30, unique=True)
    telefone = models.CharField(max_length=30, blank=True, null=True)
    setor = models.CharField("Setor", max_length=100, blank=True, null=True)
    ativo = models.BooleanField("Ativo", default=True)  # type: ignore[arg-type]
    
    # Grupos de permissão
    is_administrador = models.BooleanField("Administrador", default=False)  # type: ignore[arg-type]
    is_secretario = models.BooleanField("Secretário", default=False)  # type: ignore[arg-type]
    is_solicitante = models.BooleanField("Solicitante", default=False)  # type: ignore[arg-type]
    is_tecnico = models.BooleanField("Técnico", default=False)  # type: ignore[arg-type]
    is_almoxarife = models.BooleanField("Almoxarife", default=False)  # type: ignore[arg-type]

    # um usuário pode ter multiplos perfis (Carlos = Almoxarife + Solicitante)

    perfis = models.ManyToManyField(
        "PerfilUsuario",
        blank=True,
        related_name="usuarios",
        verbose_name="Perfis"
    )

    USERNAME_FIELD = "matricula"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta(AbstractUser.Meta):
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return f"{self.matricula} - {self.first_name}"
    
    # Helpers de permissão — usados nas views e templates
    def is_admin(self):
        """Verifica se o usuário é administrador"""
        return self.is_administrador

    def has_perfil_almoxarife(self):
        """Verifica se o usuário tem perfil de almoxarife via ManyToMany"""
        return self.perfis.filter(tipo=PerfilUsuario.Tipo.ALMOXARIFE).exists()  # type: ignore[attr-defined]

    def has_perfil_tecnico(self):
        """Verifica se o usuário tem perfil de técnico via ManyToMany"""
        return self.perfis.filter(tipo=PerfilUsuario.Tipo.TECNICO).exists()  # type: ignore[attr-defined]

    def has_perfil_solicitante(self):
        """Verifica se o usuário tem perfil de solicitante via ManyToMany"""
        return self.perfis.filter(tipo=PerfilUsuario.Tipo.SOLICITANTE).exists()  # type: ignore[attr-defined]

    def has_perfil_administrador(self):
        """Verifica se o usuário tem perfil de administrador via ManyToMany"""
        return self.perfis.filter(tipo=PerfilUsuario.Tipo.ADMINISTRADOR).exists()  # type: ignore[attr-defined]

    
    def get_grupos(self):
        """Retorna lista de grupos do usuário"""
        grupos = []
        if self.is_administrador:
            grupos.append("Administrador")
        if self.is_secretario:
            grupos.append("Secretário")
        if self.is_solicitante:
            grupos.append("Solicitante")
        if self.is_tecnico:
            grupos.append("Técnico")
        if self.is_almoxarife:
            grupos.append("Almoxarife")
        return grupos


class TipoEvento(models.TextChoices):
    LOGIN = 'LOGIN', 'Login realizado'  # type: ignore  # Login performed
    LOGIN_FALHA = 'LOGIN_FALHA', 'Falha de login'  # type: ignore
    LOGOUT = 'LOGOUT', 'Logout realizado'  # type: ignore
    ACESSO = 'ACESSO', 'Acesso a página'  # type: ignore
    CRIACAO = 'CRIACAO', 'Criação de registro'  # type: ignore
    EDICAO = 'EDICAO', 'Edição de registro'  # type: ignore
    EXCLUSAO = 'EXCLUSAO', 'Exclusão de registro'  # type: ignore


class AuditoriaLog(models.Model):
    objects: ClassVar[models.Manager]
    
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
