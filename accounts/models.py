from django.db import models

# Create your models here.
class Perfil(models.Model):
    tipo_perfil = models.ForeignKey('accounts.TipoPerfil', on_delete=models.PROTECT, db_column='TipoPerfil_id', related_name="perfiles")
    first_session = models.BooleanField(default=True)
    token_app_session = models.CharField(max_length=255,blank=True,null=True) 

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
        ordering = ['tipo_perfil']
    def __str__(self):
        return f"{self.tipo_perfil} - Primera sesión: {self.first_session}"
