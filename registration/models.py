from django.contrib.auth.models import Group, User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, default=1) 
    token_app_session = models.CharField(max_length = 240,null=True, blank=True, default='')
    first_session = models.CharField(max_length = 240,null=True, blank=True, default='Si')

    class Meta:
        ordering = ['user__username']

@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, created, **kwargs):
    """
    Crea automáticamente un Profile para cada usuario nuevo (lo exige la app
    al momento de redirigir desde check_profile). Además, garantiza que los
    usuarios existentes siempre tengan un perfil asociado.
    """
    default_group = Group.objects.filter(pk=1).first()
    profile, profile_created = Profile.objects.get_or_create(
        user=instance,
        defaults={'group': default_group} if default_group else {},
    )

    # Si el perfil ya existía y todavía no tiene grupo asignado,
    # lo asociamos al grupo por defecto en caso de estar disponible.
    if not profile_created and default_group and profile.group_id is None:
        profile.group = default_group
        profile.save(update_fields=['group'])


