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
            'cuadrilla', 
            'estado', 
            'descripcion',
            'incidencia',
        ]
        labels = {
            'encuesta': 'Encuesta Asociada',
            'ubicacion': 'Ubicación de la Incidencia',
            'cuadrilla': 'Cuadrilla Asignada',
            'estado': 'Estado de la Solicitud',
            'descripcion': 'Descripción Detallada',
        }
        widgets = {
            'encuesta': forms.Select(attrs={'class': 'form-select'}),
            'vecino': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Información del vecino'}),
            'ubicacion': forms.Select(attrs={'class': 'form-select'}),
            'cuadrilla': forms.Select(attrs={'class': 'form-select'}), 
            'incidencia': forms.Select(attrs={'class': 'form-select'}), 
            'estado': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalle la naturaleza de la incidencia'}),
        }
        
    def __init__(self, *args, **kwargs):
        encuesta_id = kwargs.pop('encuesta_id', None)
        super().__init__(*args, **kwargs)
        self.fields['cuadrilla'].queryset = Cuadrilla.objects.filter(estado=True)

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
