from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
import os
from registration.models import Profile
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
        related_name='solicitudes',
        null=True,
        blank=True
    )
    territorial = models.ForeignKey(
        'orgs.Territorial',
        on_delete=models.PROTECT,
        db_column='Territorial_id',
        related_name='solicitudes_incidencia',
        null=True, 
        blank=True
    )
    vecino = models.TextField()
    cuadrilla = models.ForeignKey(
        'orgs.Cuadrilla',
        on_delete=models.PROTECT,
        db_column='Cuadrilla_id',
        related_name='solicitudes_incidencia',
        null=True, 
        blank=True
    )
    ubicacion = models.ForeignKey(
        'locations.Ubicacion',
        on_delete=models.PROTECT,
        db_column='Ubicacion_id',
        related_name='solicitudes_incidencia',
        null=True, 
        blank=True
    )

    # Campos simples
    Estados = [
        ('Pendiente', 'Pendiente'),
        ('Derivada', 'Derivada'),
        ('En Proceso', 'En Proceso'),
        ('Finalizada', 'Finalizada'),
        ('Aprobada', 'Aprobada'),
        ('Rechazada', 'Rechazada'),
    ]
    estado = models.CharField(max_length=50, db_column='Estado',choices=Estados, default='Pendiente')

    descripcion = models.TextField(null=True, blank=True, db_column='Descripción')
    fecha = models.DateTimeField(default=timezone.now, db_column='Fecha')
    fecha_inicio = models.DateTimeField(null=True, blank=True, db_column='Fecha_inicio')
    
    
    Motivos = [
        ('Insuficiente', 'Insuficiente'),
        ('Incompleto', 'Incompleto'),
        ('Por mejorar', 'Por mejorar'),
        ('Otro motivo', 'Otro motivo'),
    ]
    motivo = models.CharField(max_length=50, db_column='Motivo',choices=Motivos, default='')

    otro = models.TextField()
    


    class Meta:
        verbose_name = 'Solicitud de Incidencia'
        verbose_name_plural = 'Solicitudes de Incidencia'

    def __str__(self):
        return f'Solicitud #{self.pk} - {self.estado}'
    
    def registrar_log(solicitud, profile, from_estado,to_estado,fecha, comentario = None):
        nota = f"El estado cambió de {from_estado} a {to_estado}."
        if comentario:
            nota += f"\n{comentario}"  # agrega el comentario si existe
        IncidenciaLog.objects.create(
        solicitud=solicitud,
        profile=profile,
        from_estado=from_estado,
        to_estado=to_estado,
        fecha=fecha,
        nota=nota
    )


class IncidenciaLog(models.Model):
    log_id = models.BigAutoField(primary_key=True, db_column='Incidencia_Log_ID')

    solicitud = models.ForeignKey(
        SolicitudIncidencia,
        on_delete=models.PROTECT,
        db_column='Solicitud_Incidencia_ID',
        related_name='logs'
    )

    profile = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        db_column='Usuario_id',
        related_name='incidencia_logs'
    )

    from_estado = models.CharField(max_length=50, db_column='Desde')
    to_estado = models.CharField(max_length=50, db_column='Hasta')
    fecha = models.DateTimeField(default=timezone.now, db_column='Fecha')
    nota = models.TextField(blank=True, null=True, db_column='Nota')

    

    class Meta:
        verbose_name = 'Log de Incidencia'
        verbose_name_plural = 'Logs de Incidencias'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.solicitud} | {self.estado_anterior} → {self.estado_actual} ({self.fecha:%d-%m-%Y %H:%M})"


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
    

class RespuestaCuadrilla(models.Model):
    #PK
    respuesta_id = models.BigAutoField(primary_key=True)
        
    #FK
    solicitud = models.ForeignKey(
        'tickets.SolicitudIncidencia',
        on_delete=models.CASCADE,
        related_name='respuestas_cuadrilla'
        )
        
    cuadrilla = models.ForeignKey(
        'orgs.Cuadrilla',
        on_delete=models.PROTECT,
        related_name='respuestas_cuadrilla'
        )
        
    #simples
    respuesta = models.TextField()
    fecha_respuesta = models.DateTimeField(default=timezone.now)
        
    def __str__(self):
        return f"Respuesta Cuadrilla #{self.pk} - Solicitud {self.solicitud_id}"
        

class MultimediaCuadrilla(models.Model):

    TIPOS = (
    ('imagen', 'Imagen'),
    ('video', 'Video'),)


    archivo = models.FileField(upload_to="evidencias_cuadrilla/", validators=[validar_tipo_archivo])
    tipo = models.CharField(max_length=10, choices=TIPOS)
        
    respuesta = models.ForeignKey(
        'tickets.RespuestaCuadrilla',
        on_delete=models.CASCADE,
        related_name='multimedia'
        )

