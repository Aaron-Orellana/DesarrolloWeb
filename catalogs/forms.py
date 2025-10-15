from django import forms
from .models import Incidencia
from orgs.models import Direccion, Departamento
from surveys.models import Encuesta

class IncidenciaForm(forms.ModelForm):
    class Meta:
        model = Incidencia
        fields = ['nombre', 'descripcion', 'direccion', 'departamento', 'encuesta']
       
        labels = {
            'nombre': 'Nombre de la Incidencia',
            'descripcion': 'Descripción',
            'direccion': 'Dirección',
            'departamento': 'Departamento',
            'encuesta': 'Encuesta asociada',
        }
       
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ingrese la descripción'}),
            'direccion': forms.Select(attrs={'class': 'form-select'}),
            'departamento': forms.Select(attrs={'class': 'form-select'}),
            'encuesta': forms.Select(attrs={'class': 'form-select'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['direccion'].queryset = Direccion.objects.filter(estado='Activo').order_by('nombre')
        self.fields['departamento'].queryset = Departamento.objects.filter(estado='Activo').order_by('nombre')
        self.fields['encuesta'].queryset = Encuesta.objects.filter(estado=True).order_by('titulo')

      
