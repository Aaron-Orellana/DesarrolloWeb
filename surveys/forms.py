from django import forms
from .models import Encuesta

class EncuestaForm(forms.ModelForm):
    class Meta:
        model = Encuesta
        # Incluye los campos que quieres mostrar en el formulario
        fields = ['titulo', 'descripcion', 'prioridad', 'estado']
        # Opcional: puedes personalizar etiquetas
        labels = {
            'titulo': 'Título de la Encuesta',
            'descripcion': 'Descripción',
            'prioridad': 'Prioridad',
            'estado': 'Activo',
        }
        # Opcional: widgets para personalizar la apariencia de los campos
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el título'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ingrese la descripción'}),
            'prioridad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alta, Media, Baja'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
