from django.db import models


class Encuesta(models.Model):
    PRIORIDAD_CHOICES = [
        ('Alta', 'Alta'),
        ('Media', 'Media'),
        ('Baja', 'Baja'),
    ]

    titulo = models.CharField(max_length=240)
    descripcion = models.TextField()
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, blank=True, null=True)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    tipo_incidencia = models.CharField(max_length=100,null=True,blank=True,verbose_name='Tipo de Incidencia')

    class Meta:
        verbose_name = 'Encuesta'
        verbose_name_plural = 'Encuestas'
        ordering = ['prioridad', 'fecha_creacion']

    def __str__(self):
        return f"{self.titulo} ({'Activa' if self.estado else 'Inactiva'})"


class Pregunta(models.Model):
    pregunta_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    # Si Pregunta está en la misma app, puedes referenciar la clase directamente (como abajo con Encuesta)
    encuesta = models.ForeignKey(
        Encuesta,
        on_delete=models.PROTECT,
        db_column='Encuesta_id',
        related_name='preguntas'   # plural, minúscula
    )
   

    class Meta:
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'

    def __str__(self):
        return self.nombre


class Respuesta(models.Model):
    respuesta_texto = models.TextField(blank=True, null=True)
    valor = models.IntegerField(blank=True, null=True)

    pregunta = models.ForeignKey(
        'Pregunta',  # misma app: vale Clase o string
        on_delete=models.PROTECT,
        db_column='Pregunta_id',
        related_name='respuestas'
    )
    solicitud_incidencia = models.ForeignKey(
        'tickets.SolicitudIncidencia',  # otra app => "app.Model"
        on_delete=models.PROTECT,
        db_column='Solicitud_Incidencia_ID',
        related_name='respuestas'
    )

    class Meta:
        # OJO: usar NOMBRES DE CAMPOS del modelo, no db_column
        constraints = [
            models.UniqueConstraint(
                fields=['solicitud_incidencia', 'pregunta'],
                name='unique_respuesta_por_pregunta_solicitud'
            )
        ]

    def __str__(self):
        return f"{self.solicitud_incidencia} - {self.pregunta}"

