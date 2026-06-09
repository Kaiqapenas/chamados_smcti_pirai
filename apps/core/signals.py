from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def assign_admin_on_superuser(sender, instance, created, **kwargs):
    """Ao criar um superuser, marca o campo is_administrador como True."""
    if created and instance.is_superuser:
        if not instance.is_administrador:
            instance.is_administrador = True
            instance.save(update_fields=["is_administrador"]) 
