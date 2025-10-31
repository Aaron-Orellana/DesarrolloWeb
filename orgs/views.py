from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from registration.models import Profile
from registration.utils import has_admin_role, clear_profile_role
from .models import Direccion, Departamento, Territorial
from .forms import DireccionForm, DepartamentoForm, CuadrillaForm, TerritorialForm
from django.utils.timezone import now
from tickets.models import SolicitudIncidencia
from orgs.models import Cuadrilla
from django.db.models import Q
from django.core.paginator import Paginator

from core.decorators import role_required

@role_required("Secpla")
def direccion_listar(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')

    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip()
    responsable = request.GET.get('responsable', '').strip()
    direcciones = Direccion.objects.prefetch_related(
        'memberships__usuario_id__user'
    ).all().order_by('direccion_id')

    filtros = Q()
    if q:
        filtros &= Q(nombre__icontains=q)
    if estado:
        if estado == 'activa':
            filtros &= Q(estado=True)
        elif estado == 'bloqueada':
            filtros &= Q(estado=False)
    if responsable:
        responsable_filters = (
            Q(memberships__usuario_id__user__username__icontains=responsable) |
            Q(memberships__usuario_id__user__first_name__icontains=responsable) |
            Q(memberships__usuario_id__user__last_name__icontains=responsable)
        )
        filtros &= Q(memberships__es_encargado=True) & responsable_filters

    direcciones = direcciones.filter(filtros).distinct()
    paginator = Paginator(direcciones, 10)
    page_number = request.GET.get('page')
    direcciones_page = paginator.get_page(page_number)
    sin_resultados = not direcciones.exists()
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_string = query_params.urlencode()

    return render(request, 'orgs/direccion_listar.html', {
        'direcciones': direcciones_page,
        'sin_resultados': sin_resultados,
        'query_string': query_string,
        'request': request,
    })

@role_required("Secpla")
def direccion_crear(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')


    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dirección creada correctamente.')
            return redirect('direccion_listar')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = DireccionForm()

    return render(request, 'orgs/create_direccion.html', {'form': form})

@role_required("Secpla")
def direccion_editar(request, direccion_id):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')
    

    direccion = get_object_or_404(
        Direccion.objects.prefetch_related('memberships__usuario_id__user'),
        pk=direccion_id
    )

    if request.method == 'POST':
        form = DireccionForm(request.POST, instance=direccion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dirección actualizada correctamente.')
            return redirect('direccion_listar')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = DireccionForm(instance=direccion)

    return render(request, 'orgs/direccion_editar.html', {'form': form, 'direccion': direccion})


@role_required("Secpla")
def direccion_ver(request, direccion_id):
    direccion = get_object_or_404(
        Direccion.objects.prefetch_related('memberships__usuario_id__user'),
        pk=direccion_id
    )
    return render(request, 'orgs/direccion_ver.html', {'direccion': direccion})


@role_required("Secpla")
def direccion_bloquear(request, direccion_id):
    direccion = get_object_or_404(Direccion, pk=direccion_id)
    direccion.estado = not direccion.estado
    estado_str = "activada" if direccion.estado else "bloqueada"
    messages.success(request, f'dirección "{direccion.nombre}" {estado_str} correctamente.')
    direccion.save(update_fields=['estado'])
    return redirect('direccion_listar')


@role_required("Secpla")
def direccion_eliminar(request, direccion_id):
    direccion = get_object_or_404(Direccion, pk=direccion_id)
    try:
        direccion.delete()
        messages.success(request, f'Dirección {direccion.nombre} eliminada correctamente.')
    except:
        messages.error(request, 'No se puede eliminar: la dirección tiene departamentos asociados.')
    return redirect('direccion_listar')


@role_required("Secpla")
def territorial_listar(request):
    territoriales = Territorial.objects.select_related("profile__user").order_by("nombre")
    q = request.GET.get("q", "").strip()
    if q:
        territoriales = territoriales.filter(
            Q(nombre__icontains=q)
            | Q(profile__user__first_name__icontains=q)
            | Q(profile__user__last_name__icontains=q)
            | Q(profile__user__username__icontains=q)
        )

    paginator = Paginator(territoriales, 10)
    page_number = request.GET.get('page')
    territoriales_page = paginator.get_page(page_number)

    return render(request, 'orgs/territorial_listar.html', {
        'territoriales': territoriales_page,
        'query': q,
        'request': request,
    })


@role_required("Secpla")
def territorial_crear(request):
    if request.method == "POST":
        form = TerritorialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Territorial creado correctamente.")
            return redirect("territorial_listar")
        messages.error(request, "Corrige los errores del formulario.")
    else:
        form = TerritorialForm()
    return render(request, "orgs/territorial_crear.html", {"form": form})


@role_required("Secpla")
def territorial_editar(request, territorial_id):
    territorial = get_object_or_404(Territorial, pk=territorial_id)
    if request.method == "POST":
        form = TerritorialForm(request.POST, instance=territorial)
        if form.is_valid():
            form.save()
            messages.success(request, "Territorial actualizado correctamente.")
            return redirect("territorial_listar")
        messages.error(request, "Corrige los errores del formulario.")
    else:
        form = TerritorialForm(instance=territorial)
    return render(request, "orgs/territorial_editar.html", {"form": form, "territorial": territorial})


@role_required("Secpla")
def territorial_eliminar(request, territorial_id):
    territorial = get_object_or_404(Territorial, pk=territorial_id)
    profile = territorial.profile
    territorial.delete()
    if profile:
        clear_profile_role(profile)
    messages.success(request, "Territorial eliminado correctamente.")
    return redirect("territorial_listar")

@role_required("Secpla","Direcciones")
def departamento_listar(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')

    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip()
    direccion_id = request.GET.get('direccion', '').strip()
    departamentos = Departamento.objects.select_related('direccion').prefetch_related(
        'memberships__usuario_id__user'
    ).all().order_by('departamento_id')
    direcciones = Direccion.objects.all().order_by('nombre')  

    filtros = Q()
    if q:
        filtros &= Q(nombre__icontains=q)
    if estado:
        if estado == 'activo':
            filtros &= Q(estado=True)
        elif estado == 'bloqueado':
            filtros &= Q(estado=False)
    if direccion_id:
        filtros &= Q(direccion__direccion_id=direccion_id)

    departamentos = departamentos.filter(filtros).distinct()
    paginator = Paginator(departamentos, 10)
    page_number = request.GET.get('page')
    departamentos_page = paginator.get_page(page_number)
    sin_resultados = not departamentos.exists()
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_string = query_params.urlencode()

    return render(request, 'orgs/departamento_listar.html', {
        'departamentos': departamentos_page,
        'direcciones': direcciones,
        'sin_resultados': sin_resultados,
        'query_string': query_string,
        'request': request,
    })



@role_required("Secpla")
def departamento_crear(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')
    

    if request.method == 'POST':
        form = DepartamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Departamento creado correctamente.')
            return redirect('departamento_listar')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = DepartamentoForm()

    return render(request, 'orgs/departamento_crear.html', {'form': form})


@role_required("Secpla")
def departamento_editar(request, departamento_id):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')
    

    departamento = get_object_or_404(
        Departamento.objects.prefetch_related('memberships__usuario_id__user'),
        pk=departamento_id
    )

    if request.method == 'POST':
        form = DepartamentoForm(request.POST, instance=departamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Departamento actualizado correctamente.')
            return redirect('departamento_listar')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = DepartamentoForm(instance=departamento)

    return render(request, 'orgs/departamento_editar.html', {
        'form': form,
        'departamento': departamento
    })


@role_required("Secpla","Direcciones")
def departamento_ver(request, departamento_id):
    departamento = get_object_or_404(
        Departamento.objects.select_related('direccion').prefetch_related('memberships__usuario_id__user'),
        pk=departamento_id
    )
    return render(request, 'orgs/departamento_ver.html', {'departamento': departamento})

@role_required("Secpla","Direcciones")
def departamento_bloquear(request, departamento_id):
    departamento = get_object_or_404(Departamento, pk=departamento_id)
    departamento.estado = not departamento.estado
    
    estado_str = "activado" if departamento.estado else "bloqueado"
    departamento.save(update_fields=['estado'])
    messages.success(request, f'departamento "{departamento.nombre}" {estado_str} correctamente.')
    return redirect('departamento_listar')


@role_required("Secpla")
def departamento_eliminar(request, departamento_id):
    departamento = get_object_or_404(Departamento, pk=departamento_id)
    try:
        departamento.delete()
        messages.success(request, f'Departamento {departamento.nombre} eliminado correctamente.')
    except:
        messages.error(request, 'No se puede eliminar: puede tener dependencias.')
    return redirect('departamento_listar')

@role_required("Secpla","Cuadrillas")
def mis_incidencias_cuadrilla(request):
    if request.user.profile.role_type not in ['cuadrilla', 'secpla']:
        messages.error(request, "No tienes permiso para acceder a este panel.")
        return redirect('home')

    # Si es cuadrilla, obtenemos solo incidencias de su cuadrilla
    if request.user.profile.role_type == 'cuadrilla':
        try:
            cuadrilla = Cuadrilla.objects.get(pk=request.user.profile.role_object_id)
        except Cuadrilla.DoesNotExist:
            messages.error(request, "No tienes una cuadrilla asignada.")
            return redirect('home')
        incidencias = SolicitudIncidencia.objects.filter(cuadrilla=cuadrilla)
        es_supervisor = False  

    # Si es secpla temporalmente vera todas las incidencias y tendra permiso para actuar
    elif request.user.profile.role_type == 'secpla':
        incidencias = SolicitudIncidencia.objects.all()
        cuadrilla = None 
        es_supervisor = True  # Esto indica que puede ver todo y actuar por ahora

    context = {
        'incidencias': incidencias,
        'cuadrilla': cuadrilla,
        'es_supervisor': es_supervisor  
    }
    return render(request, 'orgs/mis_incidencias_cuadrilla.html', context)

@role_required("Secpla","Cuadrillas")
def marcar_en_proceso(request, pk):
    if request.user.profile.role_type not in ['cuadrilla', 'secpla']:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('mis_incidencias_cuadrilla')

    incidencia = get_object_or_404(SolicitudIncidencia, pk=pk)

    # Si es cuadrilla solo puede modificar incidencias de su propia cuadrilla
    if request.user.profile.role_type == 'cuadrilla':
        cuadrilla = Cuadrilla.objects.get(pk=request.user.profile.role_object_id)
        if incidencia.cuadrilla != cuadrilla:
            messages.error(request, "No puedes modificar incidencias de otra cuadrilla.")
            return redirect('mis_incidencias_cuadrilla')
    estado_anterior = incidencia.estado
    incidencia.estado = "En Proceso"
    incidencia.fecha_inicio = now()
    incidencia.save()

    incidencia.registrar_log(
        profile= request.user.profile,
        from_estado = estado_anterior, 
        to_estado = incidencia.estado,
        fecha = now()
    )

    messages.success(request, "La incidencia fue marcada como 'En Proceso'.")
    return redirect('mis_incidencias_cuadrilla')    

@role_required("Secpla","Departamentos")
def cuadrilla_listar(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'Hubo un error con tu perfil.')
        return redirect('login')

    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip().lower()
    departamento_id = request.GET.get('departamento', '').strip()
    cuadrillas = Cuadrilla.objects.select_related('departamento').prefetch_related('memberships__usuario_id__user').all().order_by('nombre')
    departamentos = Departamento.objects.filter(estado=True).order_by('nombre')

    filtros = Q()
    if q:
        filtros &= Q(nombre__icontains=q)
    if estado:
        filtros &= Q(estado=(estado == 'activo'))
    if departamento_id:
        filtros &= Q(departamento__departamento_id=departamento_id)

    cuadrillas = cuadrillas.filter(filtros).distinct()
    paginator = Paginator(cuadrillas, 10)
    page_number = request.GET.get('page')
    cuadrillas_page = paginator.get_page(page_number)
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_string = query_params.urlencode()

    return render(request, 'orgs/cuadrilla_listar.html', {
        'cuadrillas': cuadrillas_page,
        'departamentos': departamentos,
        'query_string': query_string,
        'request': request,
    })

@role_required("Secpla")
def cuadrilla_crear(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'Permiso denegado.')
        return redirect('login')

    if request.method == 'POST':
        form = CuadrillaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuadrilla creada correctamente.')
            return redirect('cuadrilla_listar')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = CuadrillaForm()

    return render(request, 'orgs/cuadrilla_crear.html', {'form': form})

@role_required("Secpla")
def cuadrilla_editar(request, cuadrilla_id):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'Permiso denegado.')
        return redirect('login')

    cuadrilla = get_object_or_404(Cuadrilla, pk=cuadrilla_id)

    if request.method == 'POST':
        form = CuadrillaForm(request.POST, instance=cuadrilla)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuadrilla actualizada correctamente.')
            return redirect('cuadrilla_listar')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = CuadrillaForm(instance=cuadrilla)

    return render(request, 'orgs/cuadrilla_editar.html', {
        'form': form, 
        'cuadrilla': cuadrilla
    })

@role_required("Secpla","Departamentos")
def cuadrilla_ver(request, cuadrilla_id):
    cuadrilla = get_object_or_404(Cuadrilla.objects.select_related('departamento').prefetch_related(
            'memberships__usuario_id__user'),pk=cuadrilla_id)
    return render(request, 'orgs/cuadrilla_ver.html', {'cuadrilla': cuadrilla})


@role_required("Secpla")
def territorial_ver(request, territorial_id):
    territorial = get_object_or_404(
        Territorial.objects.select_related('profile__user'),
        pk=territorial_id
    )
    return render(request, 'orgs/territorial_ver.html', {'territorial': territorial})

@role_required("Secpla","Departamentos")
def cuadrilla_bloquear(request, cuadrilla_id):
    cuadrilla = get_object_or_404(Cuadrilla, pk=cuadrilla_id)
    cuadrilla.estado = not cuadrilla.estado

    estado_str = "activada" if cuadrilla.estado else "desactivada"
    cuadrilla.save(update_fields=['estado'])
    messages.success(request, f'Cuadrilla "{cuadrilla.nombre}" {estado_str} correctamente.')
    return redirect('cuadrilla_listar')
