from django.contrib import admin
from orgs.models import Territorial

@admin.register(Territorial)
class TerritorialAdmin(admin.ModelAdmin):
    list_display = ("id","nombre", "usuario")
    list_filter = ("usuario",)
    search_fields = ("nombre", "usuario__username", "usuario__email")