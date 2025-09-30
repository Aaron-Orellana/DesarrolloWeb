from django.db import models

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
# Create your models here.
