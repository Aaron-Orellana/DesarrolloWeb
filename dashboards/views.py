from django.db.models import Count
from django.shortcuts import render

from tickets.models import SolicitudIncidencia
from registration.models import Profile
from orgs.models import Territorial
from core.decorators import role_required

#--------
# Dashboard para Territorial
#--------

@role_required("Secpla", "Territoriales")
def territorial_dashboard(request):
    """
    Dashboard para usuarios territoriales con métricas, listados y filtros básicos.
    """
    profile = getattr(request.user, "profile", None)
    territorial = None

    if isinstance(profile, Profile) and profile.role_type == Profile.Role.TERRITORIAL and profile.role_object_id:
        territorial = Territorial.objects.filter(pk=profile.role_object_id).first()

    incidencias_base = (
        SolicitudIncidencia.objects.select_related(
            "incidencia",
            "encuesta",
            "territorial",
            "cuadrilla",
            "vecino",
        )
        .order_by("-fecha")
    )

    if territorial:
        incidencias_base = incidencias_base.filter(territorial=territorial)
    else:
        incidencias_base = incidencias_base.none()

    # Totales por estado
    raw_counts = incidencias_base.values("estado").annotate(total=Count("estado"))
    estado_totales = {estado: 0 for estado, _ in SolicitudIncidencia.Estados}
    for registro in raw_counts:
        estado_totales[registro["estado"]] = registro["total"]

    total_solicitudes = sum(estado_totales.values())

    # Listados específicos
    incidencias_abiertas = incidencias_base.filter(estado__in=["Pendiente", "En Proceso"])
    incidencias_derivadas = incidencias_base.filter(estado="Derivada")
    incidencias_rechazadas = incidencias_base.filter(estado="Rechazada")

    # Listado general con filtro por estado
    estado_filtro = request.GET.get("estado", "todas")
    incidencias_filtradas = incidencias_base
    if estado_filtro and estado_filtro != "todas":
        incidencias_filtradas = incidencias_filtradas.filter(estado__iexact=estado_filtro)

    estados_para_filtrar = ["Derivada", "En Proceso", "Finalizada"]

    return render(
        request,
        "dashboards/territorial_dashboard.html",
        {
            "territorial": territorial,
            "estado_totales": estado_totales,
            "total_solicitudes": total_solicitudes,
            "incidencias_abiertas": incidencias_abiertas,
            "incidencias_derivadas": incidencias_derivadas,
            "incidencias_rechazadas": incidencias_rechazadas,
            "incidencias_filtradas": incidencias_filtradas,
            "estado_filtro": estado_filtro,
            "estados_para_filtrar": estados_para_filtrar,
        },
    )
