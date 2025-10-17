from django.contrib.auth.models import Group, User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    class Role(models.TextChoices):
        SECPLA = 'secpla', 'Secpla'
        DIRECCION = 'direccion', 'Dirección'
        DEPARTAMENTO = 'departamento', 'Departamento'
        CUADRILLA = 'cuadrilla', 'Cuadrilla'
        TERRITORIAL = 'territorial', 'Territorial'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, default=1)
    phone = models.CharField(max_length=30, blank=True, default='')
    mobile = models.CharField(max_length=30, blank=True, default='')
    token_app_session = models.CharField(max_length=240, null=True, blank=True, default='')
    first_session = models.CharField(max_length=240, null=True, blank=True, default='Si')
    role_type = models.CharField(max_length=20, choices=Role.choices, null=True, blank=True)
    role_object_id = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.username} - {self.user.first_name} {self.user.last_name}"


@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, created, **kwargs):
    """
    Garantiza que cada usuario tenga un perfil asociado.
    """
    profile, _ = Profile.objects.get_or_create(user=instance)
    if not profile.group_id:
        default_group, _ = Group.objects.get_or_create(name='Usuarios')
        profile.group = default_group
        profile.save(update_fields=['group'])
