from django.db import models

# Create your models here.


class Incidencia(models.Model):
    """
    Modelo para la tabla 'Incidencia (Tipos)'.

    NOTA SOBRE FOREIGN KEYS:
    Usamos el formato "app_label.ModelName" en lugar de importar las clases,
    porque las tablas relacionadas (Direccion y Departamento) se encuentran
    en otras apps del proyecto. Esto evita dependencias circulares y facilita
    la modularización.
    """

    # PK
    incidencia_id = models.BigAutoField(
        primary_key=True,
        db_column='Incidencia_ID'
    )

    # Campos simples
    nombre = models.CharField(max_length=100, db_column='Nombre')
    descripcion = models.TextField(null=True, blank=True, db_column='Descripción')

    # FKs
    direccion = models.ForeignKey(
        'orgs.Direccion',   # app orgs, modelo Direccion
        on_delete=models.PROTECT,
        db_column='Direccion_id',
        related_name='incidencias'
    )
    departamento = models.ForeignKey(
        'orgs.Departamento',   # app orgs, modelo Departamento
        on_delete=models.PROTECT,
        db_column='Departamento_id',
        related_name='incidencias'
    )

    class Meta:
        verbose_name = 'Tipo de Incidencia'
        verbose_name_plural = 'Tipos de Incidencia'
        indexes = [
            models.Index(fields=['nombre'], name='incidencia_nombre_idx'),
        ]

    def __str__(self):
        return self.nombre