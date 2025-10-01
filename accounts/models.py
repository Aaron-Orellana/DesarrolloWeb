from django.db import models
from django.contrib.auth.models import AbstractUser

class TipoPerfil(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

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

class Usuario(AbstractUser):
    email = models.EmailField(unique=True)   # Email único
    telefono = models.CharField(max_length=20, blank=True, null=True)
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name="usuarios")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.email} - {self.perfil.nombre}"
