from django.db import models
from django.core.validators import RegexValidator, EmailValidator

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
