from django.db.models import Count
from django.shortcuts import render
from core.decorators import role_required
from django.contrib.auth.models import User
from tickets.models import SolicitudIncidencia
from orgs.models import Cuadrilla, Departamento, Direccion, Territorial
from registration.models import Profile
 

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

    raw_counts = incidencias_base.values("estado").annotate(total=Count("estado"))
    estado_totales = {estado: 0 for estado, _ in SolicitudIncidencia.Estados}
    for registro in raw_counts:
        estado_totales[registro["estado"]] = registro["total"]

    total_solicitudes = sum(estado_totales.values())

    incidencias_abiertas = incidencias_base.filter(estado__in=["Pendiente", "En Proceso"])
    incidencias_derivadas = incidencias_base.filter(estado="Derivada")
    incidencias_rechazadas = incidencias_base.filter(estado="Rechazada")

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

@role_required('Secpla','Direcciones')
def dashboard_direccion(request):
    profile = request.user.profile
    direccion = None

    membership = profile.direccion_memberships.first()
    if membership:
        direccion = membership.direccion

    if not direccion:
        return render(request, "dashboards/dashboard_direccion.html", {
            "direccion": None
        })


    cuadrillas = Cuadrilla.objects.filter(departamento__direccion=direccion).values_list("pk", flat=True)

    # Solicitudes asociadas a cuadrillas
    incidencias = SolicitudIncidencia.objects.filter(cuadrilla_id__in=cuadrillas
    ).select_related(
        'incidencia',
        'encuesta',
        'cuadrilla',
        'cuadrilla__departamento',
    ).order_by("-fecha")

    total = incidencias.count()

    # Filtro por estado
    estado_filtro = request.GET.get("estado", "todo")
    incidencias_filtradas = incidencias
    if estado_filtro != "todo":
        incidencias_filtradas = incidencias.filter(estado__iexact=estado_filtro)
    
    raw_counts = incidencias.values("estado").annotate(total=Count("estado"))
    estado_totales = {estado: 0 for estado, _ in SolicitudIncidencia.Estados if estado != "Pendiente"}
    for raw in raw_counts:
        estado_totales[raw["estado"]] = raw["total"]


    context = {
        "direccion": direccion,
        "total": total,
        "estado_totales": estado_totales,
        "estado_filtro": estado_filtro,
        "incidencias_filtradas": incidencias_filtradas,
    }

    return render(request, "dashboards/dashboard_direccion.html", context)