from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models.deletion import ProtectedError
from django.db.models import Q
from registration.models import Profile
from registration.utils import has_admin_role
from .models import Encuesta, Pregunta
from .forms import EncuestaForm,PreguntaForm
from core.decorators import role_required

@role_required("Secpla","Territoriales","Direcciones","Departamentos")
def encuesta_listar(request):
    encuestas = Encuesta.objects.all().order_by('-id')

    # Obtener parámetros GET
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip()
    prioridad = request.GET.get('prioridad', '').strip()

    # Construir queryset dinámico con Q
    filtros = Q()
    if q:
        filtros &= Q(titulo__icontains=q)
    if estado == 'activa':
        filtros &= Q(estado=True)
    elif estado == 'bloqueada':
        filtros &= Q(estado=False)
    if prioridad:
        filtros &= Q(prioridad__iexact=prioridad)

    encuestas = encuestas.filter(filtros)

    # Paginación
    paginator = Paginator(encuestas, 10)
    page_number = request.GET.get('page')
    encuestas_page = paginator.get_page(page_number)

    # Verificar si no hay resultados
    sin_resultados = not encuestas.exists()
    if sin_resultados:
        messages.info(request, 'No se encontraron resultados con los filtros seleccionados.')

    # Mantener filtros en la URL para paginación
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_string = query_params.urlencode()

    return render(request, 'surveys/encuesta_listar.html', {
        'encuestas': encuestas_page,
        'sin_resultados': sin_resultados,
        'query_string': query_string,  # se usa para paginación
        'request': request,  # para mantener valores en inputs
    })



@role_required("Secpla","Territoriales","Direcciones")
def encuesta_crear(request):
    if request.method == 'POST':
        form = EncuestaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Encuesta creada correctamente.')
            return redirect('encuesta_listar')
    else:
        form = EncuestaForm()

    return render(request, 'surveys/encuesta_crear.html', {'form': form})


@role_required("Secpla","Territoriales","Direcciones","Departamentos")
def encuesta_ver(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)
    return render(request, 'surveys/encuesta_ver.html', {'encuesta': encuesta})


@role_required("Secpla","Territoriales","Direcciones")
def encuesta_editar(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)

    if request.method == 'POST':
        form = EncuestaForm(request.POST, instance=encuesta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Encuesta actualizada correctamente.')
            return redirect('encuesta_listar')
        
    else:
        form = EncuestaForm(instance=encuesta)

    return render(request, 'surveys/encuesta_editar.html', {'form': form, 'encuesta': encuesta})


@role_required("Secpla","Territoriales","Direcciones")
def encuesta_bloquear(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)
    encuesta.estado = not encuesta.estado
    estado_str = "activada" if encuesta.estado else "bloqueada"
    encuesta.save(update_fields=['estado'])
    messages.success(request, f'Encuesta "{encuesta.titulo}" {estado_str} correctamente.')
    return redirect('encuesta_listar')


@role_required("Secpla","Direcciones")
def encuesta_eliminar(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)

    if request.method == 'POST':
        try:
            encuesta.delete()
            messages.success(request, f'Encuesta {encuesta.titulo} eliminada correctamente.')
            return redirect('encuesta_listar')
        except ProtectedError:
            messages.error(request, 'No se puede eliminar porque está asociada a otros registros.')

    return redirect('encuesta_listar')


@role_required("Secpla","Cuadrillas")
def pregunta_listar(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'Hubo un error con su perfil.')
        return redirect('logout')
    
    q = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '').strip()
    estado = request.GET.get('estado', '').strip()
    encuesta_titulo = request.GET.get('encuesta', '').strip()

    preguntas = Pregunta.objects.select_related('encuesta').all()

    if q:
        preguntas = preguntas.filter(
            Q(nombre__icontains=q) |
            Q(encuesta__titulo__icontains=q)
        )
    if tipo:
        preguntas = preguntas.filter(tipo__iexact=tipo)
    if estado:
        if estado == 'activa':
            preguntas = preguntas.filter(encuesta__estado=True)
        elif estado == 'inactiva':
            preguntas = preguntas.filter(encuesta__estado=False)
    if encuesta_titulo:
        preguntas = preguntas.filter(encuesta__titulo__icontains=encuesta_titulo)

    preguntas = preguntas.order_by('encuesta__titulo', 'nombre')

    if not preguntas.exists():
        messages.info(request, 'No se encontraron resultados con los filtros seleccionados.')

    return render(request, 'surveys/pregunta_listar.html', {
        'preguntas': preguntas
    })


@role_required("Secpla","Territoriales","Direcciones")
def pregunta_crear(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'Hubo un error con su perfil.')
        return redirect('logout')
    if request.method == 'POST':
        form = PreguntaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pregunta creada y asignada a encuesta con éxito.')
            return redirect('pregunta_listar') 
        else:
            messages.error(request, 'Error al guardar. Revise los datos del formulario.')
            
    else:
        form = PreguntaForm()
    return render(request, 'surveys/pregunta_crear.html', {'form': form, 'accion': 'Crear'})

@role_required("Secpla","Territoriales","Direcciones")
def pregunta_editar(request, pregunta_id):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'Hubo un error con su perfil.')
        return redirect('logout')
    pregunta = get_object_or_404(Pregunta, pk=pregunta_id)
    if request.method == 'POST':
        form = PreguntaForm(request.POST, instance=pregunta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pregunta actualizada con éxito.')
            return redirect('pregunta_listar')
        else:
            messages.error(request, 'Error al guardar. Revise los datos del formulario.')
            
    else:
        form = PreguntaForm(instance=pregunta)
    return render(request, 'surveys/pregunta_editar.html', {'form': form, 'accion': 'Editar', 'pregunta': pregunta})