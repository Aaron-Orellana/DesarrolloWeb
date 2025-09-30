from django.db import models

# Create your models here.
class Encuesta(models.Model):
    titulo = models.CharField(max_length=240)
    descripcion = models.TextField()
    prioridad = models.CharField(max_length=20)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Encuesta'
        verbose_name_plural = 'Encuestas'
        ordering = ['prioridad','fecha_creacion']
    
    def __str__(self):
        return f"{self.titulo} ({'Activa' if self.estado else 'Inactiva'})"

class Respuesta(models.Model):
    respuesta_texto = models.TextField(blank=True, null=True)
    valor = models.IntegerField(blank=True, null=True)


    pregunta = models.ForeignKey(
        'Pregunta',
        on_delete=models.PROTECT,
        db_column='Pregunta_id',
        related_name='Respuesta'
    )
    solicitudincidencia = models.ForeignKey(
        'tickets.SolicitudIncidencia',
        on_delete=models.PROTECT,
        db_column='Solicitud_Incidencia_id',
        related_name='Respuesta'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["solicitud", "pregunta"], name="unique_respuesta_por_pregunta_solicitud")
        ]

    def __str__(self):
        return f"{self.solicitud} - {self.pregunta}"
class Pregunta(models.Model):
    pregunta_id = models.AutoField(primary_key=True) 
    nombre = models.CharField(max_length=200)
    encuesta = models.ForeignKey(Encuesta, on_delete=models.PROTECT, db_column='Encuesta_id', related_name='Pregunta')  # Clave foránea a Encuesta
    tipo = models.CharField(max_length=50) 

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'

