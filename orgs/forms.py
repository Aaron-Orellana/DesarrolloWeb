from django import forms
from .models import Direccion, Departamento

# ---------- FORMULARIO DINÁMICO DE DIRECCIÓN ----------
class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['nombre', 'estado', 'usuario']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la dirección'
            }),
            'estado': forms.Select(choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')], attrs={
                'class': 'form-select'
            }),
            'usuario': forms.Select(attrs={'class': 'form-select'}),
        }


# ---------- FORMULARIO DINÁMICO DE DEPARTAMENTO ----------
class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = ['nombre', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del departamento'
            }),
            'direccion': forms.Select(attrs={'class': 'form-select'}),
        }

    # Ejemplo de comportamiento dinámico:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar direcciones activas
        self.fields['direccion'].queryset = Direccion.objects.filter(estado='Activo')
