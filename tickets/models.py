from django.utils import timezone
from django.db import models

# Create your models here.


class SolicitudIncidencia(models.Model):
    # PK
    solicitud_incidencia_id = models.BigAutoField(
        primary_key=True,
        db_column='Solicitud_Incidencia_ID'
    )

    # FKs (solo por nombre)
    encuesta = models.ForeignKey(
        'Encuesta',
        on_delete=models.PROTECT,
        db_column='Encuesta_id',
        related_name='solicitudes_incidencia'
    )
    incidencia = models.ForeignKey(
        'Incidencia',
        on_delete=models.PROTECT,
        db_column='Incidencia_id',
        related_name='solicitudes'
    )
    territorial = models.ForeignKey(
        'Territorial',
        on_delete=models.PROTECT,
        db_column='Territorial_id',
        related_name='solicitudes_incidencia'
    )
    vecino = models.ForeignKey(
        'Vecino',
        on_delete=models.PROTECT,
        db_column='Vecino_id',
        related_name='solicitudes_incidencia'
    )
    cuadrilla = models.ForeignKey(
        'Cuadrilla',
        on_delete=models.PROTECT,
        db_column='Cuadrilla_id',
        related_name='solicitudes_incidencia'
    )
    ubicacion = models.ForeignKey(
        'Ubicacion',
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
