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
class Cuadrilla(models.Model):
    cuadrilla_id = models.AutoField(primary_key=True) 
    nombre = models.CharField(max_length=100) 
    estado = models.CharField(max_length=20, default='Activo') 
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT, db_column='Departamento_id', related_name='Cuadrilla')
    usuario = models.IntegerField(db_column='Usuario_id') #models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Cuadrilla'
        verbose_name_plural = 'Cuadrillas'
# Create your models here.

#Creacion tabla Direccion
from django.db import models

class Direccion(models.Model):
    direccion_id = models.AutoField(primary_key=True, db_column='Direccion_id')
    nombre = models.CharField(max_length=150, unique=True)

    # Relación con usuario correspondiente
    usuario = models.ForeignKey(
        'accounts.Usuario',   #
        on_delete=models.PROTECT,
        db_column='Usuario_id',
        related_name='direcciones',
        null=True,  # 
        blank=True
    )

    class Meta:
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
