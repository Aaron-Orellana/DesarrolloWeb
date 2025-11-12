from django import forms 
from .models import SolicitudIncidencia, RespuestaCuadrilla
from orgs.models import Cuadrilla 
from surveys.models import Pregunta  

class SolicitudIncidenciaForm(forms.ModelForm):
    class Meta:
        model = SolicitudIncidencia
        fields = [
            'encuesta', 
            'vecino', 
            'ubicacion', 
            'descripcion',
        ]
        labels = {
            'encuesta': 'Encuesta Asociada',
            'ubicacion': 'Ubicación de la Incidencia',
            'descripcion': 'Descripción Detallada',
        }
        widgets = {
            'encuesta': forms.Select(attrs={'class': 'form-select'}),
            'vecino': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Información del vecino'}),
            'ubicacion': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalle la naturaleza de la incidencia'}),
        }
        
    def __init__(self, *args, **kwargs):
        encuesta_id = kwargs.pop('encuesta_id', None)
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.initial['estado'] = 'Pendiente'


        if encuesta_id:
            preguntas = Pregunta.objects.filter(encuesta_id=encuesta_id)
            for pregunta in preguntas:
                
                self.fields[f'pregunta_{pregunta.pregunta_id}'] = forms.CharField(
                    label=pregunta.nombre,
                    widget=forms.Textarea(attrs={
                        'class': 'form-control',
                        'rows': 2,
                        'placeholder': 'Respuesta...'
                    }),
                    required=True
                )


class RespuestaCuadrillaForm(forms.ModelForm):
    class Meta:
        model = RespuestaCuadrilla
        fields = ['respuesta']
        widgets = {
            'respuesta': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa la solución realizada.'
            }),
        }

class RechazaIncidenciaForm(forms.ModelForm):
    class Meta:
        model = SolicitudIncidencia
        fields = ['motivo', 'otro']
        widgets = {
            'motivo': forms.Select(attrs={'class': 'form-select'}),
            'otro': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Información del vecino'}),
        }