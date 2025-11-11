from django import forms
from .models import SolicitudIncidencia 
from orgs.models import Cuadrilla 

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
            'vecino': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'informacion del vecino'}),
            'ubicacion': forms.Select(attrs={'class': 'form-select'}),
            'cuadrilla': forms.Select(attrs={'class': 'form-select'}), 
             'incidencia': forms.Select(attrs={'class': 'form-select'}), 

            'estado': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalle la naturaleza de la incidencia'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cuadrilla'].queryset = Cuadrilla.objects.filter(estado=True)
        if not self.instance.pk:
            self.initial['estado'] = 'Pendiente'