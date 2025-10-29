from django.shortcuts import render
from core.decorators import role_required
from django.contrib.auth.models import User
from tickets.models import SolicitudIncidencia  

@role_required("Secpla")
def dashboard_secpla(request):
    total_usuarios = User.objects.filter(is_active=True).count()
    incidencias_creadas = SolicitudIncidencia.objects.count()
    incidencias_derivadas = SolicitudIncidencia.objects.filter(estado="Derivada").count()
    incidencias_rechazadas = SolicitudIncidencia.objects.filter(estado="Rechazada").count()
    incidencias_finalizadas = SolicitudIncidencia.objects.filter(estado="Finalizada").count()

    context = {
        "total_usuarios": total_usuarios,
        "incidencias_creadas": incidencias_creadas,
        "incidencias_derivadas": incidencias_derivadas,
        "incidencias_rechazadas": incidencias_rechazadas,
        "incidencias_finalizadas": incidencias_finalizadas,
    }
    return render(request, "dashboards/dashboard_secpla.html", context)
