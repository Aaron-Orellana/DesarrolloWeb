from django.contrib import admin
from tickets.models import Multimedia
from django.utils.html import format_html

@admin.register(Multimedia)
class MultimediaAdmin(admin.ModelAdmin):
    list_display = ("id", "solicitud", "tipo", "preview")
    list_filter = ("tipo", "solicitud__estado")

    def preview(self, obj):
        if obj.tipo == "imagen" and obj.archivo:
            return format_html('<img src="{}" width="100" />', obj.archivo.url)
        elif obj.tipo == "video":
            return "Video"
        return "—"
    preview.short_description = "Vista previa"

