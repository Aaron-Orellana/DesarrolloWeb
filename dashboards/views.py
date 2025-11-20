from pyexpat.errors import messages
from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404, redirect
from core.decorators import role_required
from django.contrib.auth.models import User
from tickets.models import Multimedia, SolicitudIncidencia, RespuestaCuadrilla, MultimediaCuadrilla
from orgs.models import Cuadrilla, Departamento, Direccion, Territorial
from registration.models import Profile
from django.utils import timezone
from django.contrib import messages
from tickets.forms  import RechazaIncidenciaForm, SolicitudIncidenciaForm

@role_required("Secpla")
def dashboard_secpla(request):
    
    total_usuarios = User.objects.filter(is_active=True).count()
    incidencias_creadas = SolicitudIncidencia.objects.filter(estado="Creada").count()
    incidencias_derivadas = SolicitudIncidencia.objects.filter(estado="Derivada").count()
    incidencias_rechazadas = SolicitudIncidencia.objects.filter(estado="Rechazada").count()
    incidencias_finalizadas = SolicitudIncidencia.objects.filter(estado="Finalizada").count()

    
    incidencias = SolicitudIncidencia.objects.all().select_related(
        "incidencia", "territorial", "cuadrilla", "encuesta"
    ).order_by("-fecha")

    context = {
        "total_usuarios": total_usuarios,
        "incidencias_creadas": incidencias_creadas,
        "incidencias_derivadas": incidencias_derivadas,
        "incidencias_rechazadas": incidencias_rechazadas,
        "incidencias_finalizadas": incidencias_finalizadas,
        "incidencias": incidencias, 
    }

    return render(request, "dashboards/dashboard_secpla.html", context)


from django.contrib.auth.models import User
from django.core.paginator import Paginator

@role_required("Secpla")
def listar_usuarios(request):
    """Lista todos los usuarios registrados"""
    usuarios = User.objects.all().order_by("username")
    paginator = Paginator(usuarios, 10)  
    page = request.GET.get("page")
    usuarios_pag = paginator.get_page(page)
    return render(request, "dashboards/listar_usuarios.html", {"usuarios": usuarios_pag})


@role_required("Secpla")
def listar_incidencias_creadas(request):
    incidencias = SolicitudIncidencia.objects.filter(estado="Creada")
    return render(request, "dashboards/listar_incidencias.html", {
        "titulo": "Incidencias Creadas",
        "incidencias": incidencias
    })


@role_required("Secpla")
def listar_incidencias_derivadas(request):
    incidencias = SolicitudIncidencia.objects.filter(estado="Derivada")
    return render(request, "dashboards/listar_incidencias.html", {
        "titulo": "Incidencias Derivadas",
        "incidencias": incidencias
    })


@role_required("Secpla")
def listar_incidencias_rechazadas(request):
    incidencias = SolicitudIncidencia.objects.filter(estado="Rechazada")
    return render(request, "dashboards/listar_incidencias.html", {
        "titulo": "Incidencias Rechazadas",
        "incidencias": incidencias
    })


@role_required("Secpla")
def listar_incidencias_finalizadas(request):
    incidencias = SolicitudIncidencia.objects.filter(estado="Finalizada")
    return render(request, "dashboards/listar_incidencias.html", {
        "titulo": "Incidencias Finalizadas",
        "incidencias": incidencias
    })

@role_required("Secpla", "Territoriales")
def territorial_dashboard(request):
    """
    Dashboard para usuarios territoriales con métricas, listados y filtros básicos.
    """
    territorial = Territorial.objects.filter(pk=request.user.profile.role_object_id).first()

    incidencias_base = (
        SolicitudIncidencia.objects.select_related(
            "incidencia",
            "encuesta",
            "territorial",
            "cuadrilla"
        )
        .order_by("-fecha")
        .filter(territorial=territorial)
    )

    raw_counts = (
    SolicitudIncidencia.objects
        .filter(territorial=territorial)
        .values("estado")
        .annotate(total=Count("pk"))
        .order_by("estado")
    )
    estado_totales = {estado: 0 for estado, _ in SolicitudIncidencia.Estados}
    for registro in raw_counts:
        estado_totales[registro["estado"]] = registro["total"]

    for e, i in estado_totales.items():
        print(e, i)
    total_solicitudes = incidencias_base.count()

    incidencias_abiertas = incidencias_base.filter(estado__in=["Pendiente", "En Proceso"])
    incidencias_derivadas = incidencias_base.filter(estado="Derivada")
    incidencias_rechazadas = incidencias_base.filter(estado="Rechazada")
    incidencias_finalizadas = incidencias_base.filter(estado="Finalizada")
    incidencias_aprobadas = incidencias_base.filter(estado="Aprobada")


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
            "estados_totales": estado_totales,
            "total_solicitudes": total_solicitudes,
            "incidencias_abiertas": incidencias_abiertas,
            "incidencias_derivadas": incidencias_derivadas,
            "incidencias_rechazadas": incidencias_rechazadas,
            "incidencias_filtradas": incidencias_filtradas,
            "incidencias_finalizadas": incidencias_finalizadas,
            "incidencias_aprobadas": incidencias_aprobadas,
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

ESTADOS_PENDIENTES = ['Pendiente', '', None]
ESTADOS_TOMADAS = ['Derivada']
ESTADOS_ASIGNADAS = ['En Proceso']
ESTADOS_COMPLETADAS = ['Finalizada', 'Aprobada']
ESTADOS_RECHAZADAS = ['Rechazada']
ESTADOS_EN_PROCESO = ['En Proceso']

@role_required('Secpla', 'Departamentos')
def dashboard_departamento(request):
    profile = request.user.profile
    membership = profile.departamento_memberships.select_related('departamento').first()

    if not membership:
        return render(request, "dashboards/dashboard_departamento.html", {
            "departamento": None
        })

    departamento = membership.departamento
    es_encargado = membership.es_encargado

    pendientes = SolicitudIncidencia.objects.filter(
        cuadrilla__isnull=True
    ).exclude(
        estado__in=ESTADOS_RECHAZADAS
    ).select_related('incidencia').order_by('-fecha')

    tomadas = SolicitudIncidencia.objects.filter(
        cuadrilla__departamento=departamento
    ).exclude(
        estado__in=ESTADOS_EN_PROCESO + ESTADOS_COMPLETADAS
    ).select_related('incidencia', 'cuadrilla').order_by('-fecha')

    asignadas = SolicitudIncidencia.objects.filter(
        cuadrilla__departamento=departamento,
        estado__in=ESTADOS_EN_PROCESO
    ).select_related('incidencia', 'cuadrilla').order_by('-fecha')

    completadas = SolicitudIncidencia.objects.filter(
        cuadrilla__departamento=departamento,
        estado__in=ESTADOS_COMPLETADAS
    ).select_related('incidencia', 'cuadrilla').order_by('-fecha')

    counts = {
        'pendientes': pendientes.count(),
        'tomadas': tomadas.count(),
        'asignadas': asignadas.count(),
        'completadas': completadas.count(),
    }

    context = {
        'departamento': departamento,
        'es_encargado': es_encargado,
        'total_general': sum(counts.values()),
        'counts': counts,
        'pendientes': pendientes,
        'tomadas': tomadas,
        'asignadas': asignadas,
        'completadas': completadas,
        'cuadrillas_disponibles': departamento.Cuadrilla.filter(estado=True).order_by('nombre'),
    }

    return render(request, "dashboards/dashboard_departamento.html", context)

@role_required('Secpla', 'Cuadrillas')
def dashboard_cuadrilla(request):
    """Dashboard para cuadrillas: ver incidencias asignadas y subir evidencia de solución."""
    profile = request.user.profile
    cuadrilla = None

    # Obtener la cuadrilla asociada al usuario
    membership = getattr(profile, "cuadrilla_memberships", None)
    if membership:
        cuadrilla = profile.cuadrilla_memberships.first().cuadrilla

    if not cuadrilla:
        messages.warning(request, "No tienes una cuadrilla asignada.")
        return render(request, "dashboards/dashboard_cuadrilla.html", {"cuadrilla": None})

    # Filtrar incidencias asignadas a esa cuadrilla
    incidencias = (
        SolicitudIncidencia.objects.filter(cuadrilla=cuadrilla)
        .select_related("incidencia", "territorial", "cuadrilla")
        .order_by("-fecha")
    )

    context = {
        "cuadrilla": cuadrilla,
        "incidencias": incidencias,
    }

    return render(request, "dashboards/dashboard_cuadrilla.html", context)

@role_required('Cuadrillas')
def responder_incidencia(request, incidencia_id):
    """Permite a la cuadrilla responder una incidencia con imágenes y comentario."""
    incidencia = get_object_or_404(SolicitudIncidencia, pk=incidencia_id)
    cuadrilla = incidencia.cuadrilla

    if request.method == "POST":
        respuesta_texto = request.POST.get("respuesta")
        archivos = request.FILES.getlist("archivos")

        
        archivo_invalido = False

        
        Respuesta = RespuestaCuadrilla.objects.create(
            solicitud=incidencia,
            cuadrilla=cuadrilla,
            respuesta=respuesta_texto
        )

        
        for archivo in archivos:
            if archivo.content_type.startswith("image"):
                tipo = "imagen"
            elif archivo.content_type.startswith("video"):
                tipo = "video"
            else:
                messages.error(request, f"El archivo '{archivo.name}' no es válido. Solo imágenes o videos.")
                archivo_invalido = True 
                continue

            MultimediaCuadrilla.objects.create(
                respuesta=Respuesta,
                archivo=archivo,
                tipo=tipo,
            )

       
        if archivo_invalido:
            return render(request, "dashboards/respuesta_incidencia.html", {
                "incidencia": incidencia,
                "respuesta_texto": respuesta_texto  
            })

      
        incidencia.estado = "Finalizada"
        incidencia.save()

        messages.success(request, "Respuesta registrada correctamente. La incidencia ha sido finalizada.")
        return redirect("dashboard_cuadrilla")

    return render(request, "dashboards/respuesta_incidencia.html", {"incidencia": incidencia})
def asignar_cuadrilla(request, incidencia_id):
    incidencia = get_object_or_404(SolicitudIncidencia, pk=incidencia_id)
    profile = request.user.profile

    membership = profile.departamento_memberships.first()
    if not membership or not membership.es_encargado:
        messages.error(request, "No tienes permiso para asignar cuadrillas.")
        return redirect('dashboard_departamento')

    if incidencia.cuadrilla and incidencia.cuadrilla.departamento != membership.departamento:
        messages.error(request, "Esta incidencia no pertenece a tu departamento.")
        return redirect('dashboard_departamento')

    if request.method == "POST":
        cuadrilla_id = request.POST.get("cuadrilla_id")
        if not cuadrilla_id:
            messages.error(request, "Debes seleccionar una cuadrilla.")
            return redirect('dashboard_departamento')

        try:
            nueva_cuadrilla = Cuadrilla.objects.get(
                pk=cuadrilla_id,
                departamento=membership.departamento
            )
            incidencia.cuadrilla = nueva_cuadrilla
            incidencia.save()
            messages.success(request, f"Cuadrilla '{nueva_cuadrilla.nombre}' asignada.")
        except Cuadrilla.DoesNotExist:
            messages.error(request, "Cuadrilla no válida.")

    return redirect('dashboard_departamento')

def tomar_solicitud(request, incidencia_id):
    membership = request.user.profile.departamento_memberships.select_related('departamento').first()
    if not membership or not membership.es_encargado:
        messages.error(request, "No tienes permiso para tomar solicitudes.")
        return redirect('dashboard_departamento')

    incidencia = get_object_or_404(
        SolicitudIncidencia,
        pk=incidencia_id,
        cuadrilla__isnull=True,
    )

    cuadrilla_default = membership.departamento.Cuadrilla.first()

    if not cuadrilla_default:
        messages.error(request, "Tu departamento no tiene cuadrillas configuradas.")
        return redirect('dashboard_departamento')

    incidencia.cuadrilla = cuadrilla_default
    incidencia.estado = 'Derivada'
    incidencia.save(update_fields=['cuadrilla', 'estado'])

    messages.success(
        request,
        f"Solicitud #{incidencia_id} tomada y asignada a la cuadrilla '{cuadrilla_default.nombre}'."
    )
    return redirect('dashboard_departamento')

def poner_en_proceso(request, incidencia_id):
    membership = request.user.profile.departamento_memberships.select_related('departamento').first()
    if not membership or not membership.es_encargado:
        messages.error(request, "No tienes permiso.")
        return redirect('dashboard_departamento')

    incidencia = get_object_or_404(
        SolicitudIncidencia,
        pk=incidencia_id,
        cuadrilla__departamento=membership.departamento
    )

    if incidencia.estado in ['En Proceso', 'Finalizada', 'Aprobada']:
        messages.warning(request, f"La solicitud #{incidencia_id} ya está en proceso o completada.")
    else:
        incidencia.estado = 'En Proceso'
        incidencia.save(update_fields=['estado'])
        messages.success(request, f"Solicitud #{incidencia_id} pasada a 'En Proceso'.")

    return redirect('dashboard_departamento')

@role_required("Territoriales")
def aprobar_incidencia(request, incidencia_id):

    incidencia = get_object_or_404(SolicitudIncidencia, pk=incidencia_id)
    
    respuesta = RespuestaCuadrilla.objects.filter(solicitud=incidencia).last()
    evidencias = MultimediaCuadrilla.objects.filter(respuesta=respuesta) if respuesta else None

    if request.method == "POST":
        incidencia.estado = "Aprobada"
        incidencia.save()


        incidencia.registrar_log(
            profile=request.user.profile,
            from_estado="Finalizada",
            to_estado="Aprobada",
            fecha=timezone.now(),
            comentario="Aprobada por el territorial."
        )

        messages.success(request, "La incidencia fue aprobada correctamente.")
        return redirect("dashboard_territorial")

    context = {
        "incidencia": incidencia,
        "respuesta": respuesta,
        "evidencias": evidencias
    }
    return render(request, "dashboards/aprobar_incidencia.html", context)

@role_required('Territoriales')
def rechazar_incidencia(request, incidencia_id):
    obj = SolicitudIncidencia.objects.get(pk=incidencia_id)
    form = RechazaIncidenciaForm(instance=obj)
    if request.method == 'POST':
        form = RechazaIncidenciaForm(request.POST,instance=obj)
        if form.is_valid():
            form.save(commit=False)
            obj.estado = 'Rechazada'
            form.save()
            obj.save()
            return redirect('/dashboards/territorial/')
    context = {
        'form':form
    }
    return render(request, 'dashboards/rechazar_incidencia.html', context)

@role_required("Territoriales")
def redirigir_incidencia(request, incidencia_id):
    incidencia = get_object_or_404(SolicitudIncidencia, pk=incidencia_id)

    if incidencia.estado != "Rechazada":
        messages.warning(request, "Solo puedes redirigir incidencias que estén en estado Rechazada.")
        return redirect("dashboard_territorial")

    form = SolicitudIncidenciaForm(request.POST or None, instance=incidencia)

    if request.method == "POST":
        comentario = request.POST.get("comentario", "").strip()
        if form.is_valid():
            solicitud_actualizada = form.save(commit=False)
            estado_anterior = incidencia.estado
            solicitud_actualizada.estado = "Pendiente"
            solicitud_actualizada.cuadrilla = None
            solicitud_actualizada.save()

            solicitud_actualizada.registrar_log(
                profile=request.user.profile,
                from_estado=estado_anterior,
                to_estado=solicitud_actualizada.estado,
                fecha=timezone.now(),
                comentario=comentario or "Incidencia redirigida por el territorial."
            )

            messages.success(request, f"La solicitud #{incidencia.solicitud_incidencia_id} se redirigió correctamente.")
            return redirect("dashboard_territorial")
        else:
            messages.error(request, "Revisa los datos del formulario antes de redirigir la incidencia.")

    respuesta_cuadrilla = RespuestaCuadrilla.objects.filter(solicitud=incidencia).first()
    evidencias_cuadrilla = MultimediaCuadrilla.objects.filter(respuesta=respuesta_cuadrilla) if respuesta_cuadrilla else None
    evidencias_vecino = incidencia.multimedia.all()
    logs = incidencia.logs.all()

    comentario = request.POST.get("comentario", "") if request.method == "POST" else ""

    context = {
        "incidencia": incidencia,
        "form": form,
        "respuesta_cuadrilla": respuesta_cuadrilla,
        "evidencias_cuadrilla": evidencias_cuadrilla,
        "evidencias_vecino": evidencias_vecino,
        "logs": logs,
        "comentario": comentario,
    }

    return render(request, "dashboards/redirigir_incidencia.html", context)
    
