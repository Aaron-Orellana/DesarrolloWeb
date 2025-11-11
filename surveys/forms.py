from django import forms
from .models import Encuesta, Pregunta

class EncuestaForm(forms.ModelForm):
    class Meta:
        model = Encuesta
        fields = ['titulo', 'descripcion', 'prioridad', 'estado', 'tipo_incidencia']
        labels = {
            'titulo': 'Título de la Encuesta',
            'descripcion': 'Descripción',
            'prioridad': 'Prioridad',
            'estado': 'Activo',
            'tipo_incidencia': 'Tipo de Incidencia'
        }
        
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el título'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ingrese la descripción'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tipo_incidencia': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ejemplo: Alumbrado, Limpieza, Seguridad...'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['prioridad'].empty_label = "---------"

class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ['encuesta', 'nombre']
        
        widgets = {
            'encuesta': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Escriba el texto completo de la pregunta'}),
           
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['encuesta'].queryset = Encuesta.objects.filter(estado=True)