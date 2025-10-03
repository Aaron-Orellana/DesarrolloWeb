
from django.db import models
from django.core.validators import RegexValidator, EmailValidator
# Create your models here.
from django.core.exceptions import ValidationError


def validar_latitud(valor):
    if valor is not None and (valor < -90 or valor > 90):
        raise ValidationError("La latitud debe estar entre -90 y 90 grados.")


def validar_longitud(valor):
    if valor is not None and (valor < -180 or valor > 180):
        raise ValidationError("La longitud debe estar entre -180 y 180 grados.")


class Ubicacion(models.Model):
    calle = models.CharField(max_length=200)
    numero_casa = models.CharField(max_length=20)
    latitud = models.FloatField(null=True, blank=True, validators=[validar_latitud])
    longitud = models.FloatField(null=True, blank=True, validators=[validar_longitud])

    def __str__(self):
        return f"{self.calle} {self.numero_casa}"

class Vecino(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?\d{7,15}$', message="Ingrese un teléfono válido")]
    )
    correo = models.EmailField(
        max_length=100,
        blank=True,  # hace que sea opcional
        null=True,
        validators=[EmailValidator(message="Ingrese un correo válido")]
    )

    def __str__(self):
        return self.nombre
