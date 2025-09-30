from django.db import models

class Departamento(models.Model):
    nombre = models.CharField(max_length=150)

    direccion = models.ForeignKey(
        'Direccion', 
        on_delete=models.PROTECT,
        db_column='Direccion_id',
        related_name='Departamento'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["direccion", "nombre"], name="unique_departamento_por_direccion")
        ]

    def __str__(self):
        return f"{self.nombre} ({self.direccion})"
# Create your models here.
