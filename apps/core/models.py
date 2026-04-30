from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


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
