from django.shortcuts import render
from core.decorators import role_required
from tickets.models import SolicitudIncidencia

#--------
# Dashboard para Territorial
#--------

#@role_required('Secpla', 'Territorial')
def territorial_dashboard(request):
    # Esta vista renderiza el dashboard específico para usuarios con el rol 'territorial'.
    # Esta vista deberia mostrar: de manera numerica las solicitudes totales separadas por tipo.
    
    incidencias_pendientes = SolicitudIncidencia.objects.filter(estado='Pendiente')
    incidencias_derivadas = SolicitudIncidencia.objects.filter(estado='Derivada')
    incidencias_en_proceso = SolicitudIncidencia.objects.filter(estado='En Proceso')
    incidencias_finalizadas = SolicitudIncidencia.objects.filter(estado='Finalizada')
    incidencias_aprobadas = SolicitudIncidencia.objects.filter(estado='Aprobada')
    incidencias_rechazadas = SolicitudIncidencia.objects.filter(estado='Rechazada')


    return render(request, 'territorial.html', {
        'incidencias_pendientes': incidencias_pendientes,
        'incidencias_derivadas': incidencias_derivadas,
        'incidencias_en_proceso': incidencias_en_proceso,
        'incidencias_finalizadas': incidencias_finalizadas,
        'incidencias_aprobadas': incidencias_aprobadas,
        'incidencias_rechazadas': incidencias_rechazadas,
    })

