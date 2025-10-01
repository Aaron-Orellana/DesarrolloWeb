from django.contrib import admin
from .models import Vecino

@admin.register(Vecino)
class VecinoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'correo')
    search_fields = ('nombre', 'telefono')
