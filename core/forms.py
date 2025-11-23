# core/forms.py
from django import forms

class BaseBootstrapForm(forms.ModelForm):

    bootstrap_input_class = "form-control"
    bootstrap_select_class = "form-select"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            widget = field.widget

            # Entradas de texto y áreas de texto
            if isinstance(widget, (forms.TextInput, forms.EmailInput,
                                   forms.NumberInput, forms.PasswordInput,
                                   forms.DateInput, forms.Textarea)):
                existing_classes = widget.attrs.get("class", "")
                widget.attrs["class"] = f"{existing_classes} {self.bootstrap_input_class}".strip()

                # Palceholder base
                if "placeholder" not in widget.attrs:
                    widget.attrs["placeholder"] = f"Ingrese {field.label}"

            # Seleccion
            elif isinstance(widget, forms.Select):
                existing_classes = widget.attrs.get("class", "")
                widget.attrs["class"] = f"{existing_classes} {self.bootstrap_select_class}".strip()

            # Casilla de verificación
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "form-check-input"
