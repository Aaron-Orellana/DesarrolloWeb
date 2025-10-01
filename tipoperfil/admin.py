# tipoperfil/admin.py
from django.contrib import admin
from .models import TipoPerfil

@admin.register(TipoPerfil)
class TipoPerfilAdmin(admin.ModelAdmin):
    # Muestra la columna 'nombre' en la lista de objetos
    list_display = ('nombre',)
    # Campos que se muestran y pueden ser editados en el formulario
    fields = ('nombre',)
    # NO ponemos readonly_fields, para que se pueda modificar
