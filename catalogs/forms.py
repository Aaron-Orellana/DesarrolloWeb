from django import forms
from .models import Incidencia

class IncidenciaForm(forms.ModelForm):
    class Meta:
        model = Incidencia
        # Campos que quieres mostrar en el formulario
        fields = ['nombre', 'descripcion', 'direccion', 'departamento', 'encuesta']
        # Opcional: etiquetas más amigables
        labels = {
            'nombre': 'Nombre de la Incidencia',
            'descripcion': 'Descripción',
            'direccion': 'Dirección',
            'departamento': 'Departamento',
            'encuesta': 'Encuesta asociada',
        }
        # Opcional: widgets para mejorar la UI
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ingrese la descripción'}),
            'direccion': forms.Select(attrs={'class': 'form-select'}),
            'departamento': forms.Select(attrs={'class': 'form-select'}),
            'encuesta': forms.Select(attrs={'class': 'form-select'}),
        }
