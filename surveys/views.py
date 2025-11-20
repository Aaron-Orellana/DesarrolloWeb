from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models.deletion import ProtectedError
from django.db.models import Q
from registration.models import Profile
from registration.utils import has_admin_role
from .models import Encuesta, Pregunta
from .forms import EncuestaForm,PreguntaForm, PreguntaFormSet
from core.decorators import role_required
from django.db import transaction

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
        encuesta_form = EncuestaForm(request.POST)
        formset = PreguntaFormSet(request.POST)
        if encuesta_form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    encuesta = encuesta_form.save()
                    formset.instance = encuesta
                    formset.save()
                    messages.success(request, 'Encuesta creada correctamente.')
                    return redirect('encuesta_listar')
            except:
                messages.error(request, "Error al guardar la encuesta")
        else:
            messages.error(request, 'Corrige los errores en los formularios (Encuesta y Pregunta).')
            encuesta_form = EncuestaForm(request.POST)
    else:
        encuesta_form = EncuestaForm()
        formset = PreguntaFormSet()

    return render(request, 'surveys/encuesta_crear.html', {'encuesta_form': encuesta_form, 'formset': formset})


@role_required("Secpla","Territoriales","Direcciones","Departamentos")
def encuesta_ver(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)
    return render(request, 'surveys/encuesta_ver.html', {'encuesta': encuesta})


@role_required("Secpla","Territoriales","Direcciones")
def encuesta_editar(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)
    if encuesta.estado == True:
        messages.error(request,'No se puede editar una encuesta que está "Activa".')
        return redirect('encuesta_listar')
    if request.method == 'POST':
        encuesta_form = EncuestaForm(request.POST, instance=encuesta)
        formset = PreguntaFormSet(
            request.POST,
            instance=encuesta,
            prefix='preguntas',
            queryset=Pregunta.objects.filter(encuesta=encuesta, fue_borrado=False),
        )
        if encuesta_form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    encuesta = encuesta_form.save()

                    for idx, form in enumerate(formset.forms):
                        # Tomar flag DELETE directamente del POST para asegurarlo
                        raw_delete = formset.data.get(f"{formset.prefix}-{idx}-DELETE")
                        delete_flag = form.cleaned_data.get('DELETE') or (raw_delete in ("on", "true", "True", "1"))

                        # Ignorar formularios en blanco sin cambios
                        if not delete_flag and not form.has_changed() and not form.cleaned_data.get('nombre'):
                            continue

                        pregunta = form.save(commit=False)
                        if delete_flag:
                            if pregunta.pk:
                                pregunta.fue_borrado = True
                                pregunta.save(update_fields=['fue_borrado'])
                            continue

                        pregunta.encuesta = encuesta
                        pregunta.fue_borrado = False
                        pregunta.save()

                    messages.success(request, 'Encuesta y preguntas actualizadas correctamente.')
                    return redirect('encuesta_listar')
            except Exception as e:
                messages.error(request, f"Error al guardar la encuesta: {e}")
        else:
            print("Errores encuesta_form:", encuesta_form.errors)
            print("Errores formset:", formset.errors)
            print("Errores no-form del formset:", formset.non_form_errors())
            messages.error(request, "Corrige los errores antes de guardar. Revisa la consola para más detalles.")
        
    else:
        encuesta_form = EncuestaForm(instance=encuesta)
        #Solo mostrar preguntas NO borradas
        formset = PreguntaFormSet(
            instance=encuesta,
            queryset=Pregunta.objects.filter(encuesta=encuesta, fue_borrado=False),
            prefix='preguntas'
        )
    #Hacer los campos existentes solo lectura
    for form in formset.forms:
        if form.instance.pk:
            # Mostrar solo lectura en la interfaz
            form.fields['nombre'].widget.attrs['readonly'] = True
            # Asegurar que el valor se envíe al POST
            form.fields['nombre'].required = False

    return render(request, 'surveys/encuesta_editar.html', {'encuesta_form': encuesta_form, 'formset': formset, 'encuesta': encuesta})


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
