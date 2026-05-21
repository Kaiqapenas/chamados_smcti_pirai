from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update the default admin superuser."

    def handle(self, *args, **options):
        User = get_user_model()
        matricula = "admin"
        password = "3"

        user, created = User.objects.get_or_create(
            matricula=matricula,
            defaults={
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS("Superuser created with matricula 'admin'.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Superuser 'admin' already existed and was updated.")
            )
