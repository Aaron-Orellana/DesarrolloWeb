from django import forms
from .models import Ubicacion


class UbicacionForm(forms.ModelForm):
    class Meta:
        model = Ubicacion
        fields = ["calle", "numero_casa", "latitud", "longitud"]
        widgets = {
            "calle": forms.TextInput(attrs={"class": "form-control", "placeholder": "Calle, avenida o sector"}),
            "numero_casa": forms.TextInput(attrs={"class": "form-control", "placeholder": "Número o referencia"}),
            "latitud": forms.NumberInput(attrs={"class": "form-control", "step": "0.000001"}),
            "longitud": forms.NumberInput(attrs={"class": "form-control", "step": "0.000001"}),
        }
