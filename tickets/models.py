from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
import os
# Create your models here.


class SolicitudIncidencia(models.Model):
    # PK
    solicitud_incidencia_id = models.BigAutoField(
        primary_key=True,
        db_column='Solicitud_Incidencia_ID'
    )

    # FKs (solo por nombre)
    encuesta = models.ForeignKey(
        'surveys.Encuesta',
        on_delete=models.PROTECT,
        db_column='Encuesta_id',
        related_name='solicitudes_incidencia'
    )
    incidencia = models.ForeignKey(
        'catalogs.Incidencia',
        on_delete=models.PROTECT,
        db_column='Incidencia_id',
        related_name='solicitudes'
    )
    territorial = models.ForeignKey(
        'orgs.Territorial',
        on_delete=models.PROTECT,
        db_column='Territorial_id',
        related_name='solicitudes_incidencia'
    )
    vecino = models.ForeignKey(
        'locations.Vecino',
        on_delete=models.PROTECT,
        db_column='Vecino_id',
        related_name='solicitudes_incidencia'
    )
    cuadrilla = models.ForeignKey(
        'orgs.Cuadrilla',
        on_delete=models.PROTECT,
        db_column='Cuadrilla_id',
        related_name='solicitudes_incidencia'
    )
    ubicacion = models.ForeignKey(
        'locations.Ubicacion',
        on_delete=models.PROTECT,
        db_column='Ubicacion_id',
        related_name='solicitudes_incidencia'
    )

    # Campos simples
    estado = models.CharField(max_length=50, db_column='Estado')
    descripcion = models.TextField(null=True, blank=True, db_column='Descripción')
    fecha = models.DateTimeField(default=timezone.now, db_column='Fecha')

    class Meta:
        db_table = 'Solicitud_Incidencia'
        verbose_name = 'Solicitud de Incidencia'
        verbose_name_plural = 'Solicitudes de Incidencia'
        indexes = [
            models.Index(fields=['estado'], name='sol_inc_estado_idx'),
            models.Index(fields=['fecha'], name='sol_inc_fecha_idx'),
        ]

    def __str__(self):
        return f'Solicitud #{self.pk} - {self.estado}'


class HistorialEstadoEncuesta(models.Model):
    # PK
    historial_id = models.BigAutoField(
        primary_key=True,
        db_column='Historial_Estado_ID'
    )

    # FK hacia SolicitudIncidencia
    solicitud = models.ForeignKey(
        SolicitudIncidencia,
        on_delete=models.CASCADE,
        db_column='Solicitud_Incidencia_ID',
        related_name='historial_estados'
    )

    # Campos simples
    estado = models.CharField(max_length=50, db_column='Estado')
    usuario = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        db_column='Usuario_id',
        related_name='historial_estados'
    )
    fecha = models.DateTimeField(auto_now_add=True, db_column='Fecha')

    class Meta:
        db_table = 'Historial_Estado_Encuesta'
        verbose_name = 'Historial de Estado'
        verbose_name_plural = 'Historial de Estados'
        indexes = [
            models.Index(fields=['estado'], name='hist_estado_idx'),
            models.Index(fields=['fecha'], name='hist_fecha_idx'),
        ]

    def __str__(self):
        return f'{self.solicitud} - {self.estado} ({self.fecha})'


def validar_tipo_archivo(valor):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.mp4', '.mov']
    ext = os.path.splitext(valor.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError("Formato de archivo que no permitido (usa jpg, png, mp4 o mov).")

class Multimedia(models.Model):
    # PK
    multimedia_id = models.BigAutoField(
        primary_key=True,
        db_column='Multimedia_ID'
    )
    TIPOS = (
        ('imagen', 'Imagen'),
        ('video', 'Video'),
    )
    #FK
    solicitud_incidencia= models.ForeignKey(
        'tickets.SolicitudIncidencia',
        on_delete=models.PROTECT,
        db_column='Solicitud_incidencia_id',
        related_name='multimedia'
    )
    archivo = models.FileField(upload_to="evidencias/", validators=[validar_tipo_archivo])
    tipo = models.CharField(max_length=10, choices=TIPOS)

    def __str__(self):
        return f"Tipo: {self.tipo} - Solicitud: {self.solicitud_incidencia.pk}"
