from django import forms
from .models import Direccion, Departamento
from registration.models import Profile

# ---------- FORMULARIO DINÁMICO DE DIRECCIÓN ----------
class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['nombre', 'profile']
        labels = {
            'profile': 'Responsable',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la dirección'
            }),

            'profile': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile'].queryset = Profile.objects.select_related('user').order_by('user__username')


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
        self.fields['direccion'].queryset = Direccion.objects.filter(estado=True)
