from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from .models import Encuesta
from registration.models import Profile

PRIORIDADES = ['Alta', 'Media', 'Baja']

@login_required
def encuesta_crear(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile') 
    if profile.group_id != 1:
        return redirect('logout')


    return render(request, 'surveys/encuesta_crear.html', {
        'prioridades': PRIORIDADES,
    })

@login_required
def encuesta_guardar(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile') 
    if profile.group_id != 1:
        return redirect('logout')
    if request.method == 'POST':
        titulo = (request.POST.get('titulo') or '').strip()
        descripcion = (request.POST.get('descripcion') or '').strip()
        prioridad = (request.POST.get('prioridad') or '').strip()

        if not titulo:
            messages.error(request, 'El campo "Título" es obligatorio.')
            return redirect('encuesta_crear')
        if prioridad not in PRIORIDADES:
            messages.error(request, 'Debe seleccionar una prioridad válida.')
            return redirect('encuesta_crear')

        Encuesta.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            prioridad=prioridad
        )

        messages.success(request, 'Encuesta creada correctamente.')
        return redirect('encuesta_listar')

    return redirect('encuesta_crear')

@login_required
def encuesta_listar(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile') 
    if profile.group_id != 1:
        return redirect('logout')
    encuestas = Encuesta.objects.all().order_by('-id')
    return render(request, 'surveys/encuesta_listar.html', {'encuestas': encuestas})



@login_required
def encuesta_detalle(request, encuesta_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile') 
    
    if profile.group_id != 1:
        return redirect('logout')
    
    try:
        encuesta = Encuesta.objects.get(pk=encuesta_id)
    except Encuesta.DoesNotExist:
        messages.error(request, 'La encuesta no existe.')
        return redirect('encuesta_listar')
    return render(request, 'surveys/encuesta_detalle.html', {'encuesta': encuesta})


@login_required
def encuesta_editar(request, encuesta_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')

    if profile.group_id != 1:
        return redirect('logout')

    try:
        encuesta = Encuesta.objects.get(pk=encuesta_id)
    except Encuesta.DoesNotExist:
        messages.error(request, 'La encuesta no existe.')
        return redirect('encuesta_listar')

    if request.method == 'POST':
        titulo = (request.POST.get('titulo') or '').strip()
        descripcion = (request.POST.get('descripcion') or '').strip()
        prioridad = (request.POST.get('prioridad') or '').strip()

        if not titulo:
            messages.error(request, 'El campo "Título" es obligatorio.')
        elif prioridad not in PRIORIDADES:
            messages.error(request, 'Debe seleccionar una prioridad válida.')
        else:
            encuesta.titulo = titulo
            encuesta.descripcion = descripcion
            encuesta.prioridad = prioridad
            encuesta.save()
            messages.success(request, 'Encuesta actualizada correctamente.')
            return redirect('encuesta_detalle', encuesta_id=encuesta.id)

        form_values = {
            'titulo': titulo,
            'descripcion': descripcion,
            'prioridad': prioridad,
        }
    else:
        form_values = {
            'titulo': encuesta.titulo,
            'descripcion': encuesta.descripcion,
            'prioridad': encuesta.prioridad,
        }

    return render(
        request,
        'surveys/encuesta_editar.html',
        {
            'encuesta': encuesta,
            'prioridades': PRIORIDADES,
            'form_values': form_values,
        }
    )


@login_required
def encuesta_cambiar_estado(request, encuesta_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')

    if profile.group_id != 1:
        return redirect('logout')

    try:
        encuesta = Encuesta.objects.get(pk=encuesta_id)
    except Encuesta.DoesNotExist:
        messages.error(request, 'La encuesta no existe.')
        return redirect('encuesta_listar')

    if request.method != 'POST':
        return redirect('encuesta_detalle', encuesta_id=encuesta.id)

    accion = request.POST.get('accion')
    if accion == 'bloquear' and encuesta.estado:
        encuesta.estado = False
        encuesta.save(update_fields=['estado'])
        messages.success(request, 'Encuesta bloqueada correctamente.')
    elif accion == 'activar' and not encuesta.estado:
        encuesta.estado = True
        encuesta.save(update_fields=['estado'])
        messages.success(request, 'Encuesta activada correctamente.')
    else:
        messages.error(request, 'La acción seleccionada no es válida para el estado actual.')

    return redirect('encuesta_detalle', encuesta_id=encuesta.id)


@login_required
def encuesta_eliminar(request, encuesta_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')

    if profile.group_id != 1:
        return redirect('logout')

    try:
        encuesta = Encuesta.objects.get(pk=encuesta_id)
    except Encuesta.DoesNotExist:
        messages.error(request, 'La encuesta no existe.')
        return redirect('encuesta_listar')

    if request.method != 'POST':
        return redirect('encuesta_detalle', encuesta_id=encuesta.id)

    try:
        encuesta.delete()
        messages.success(request, 'Encuesta eliminada correctamente.')
        return redirect('encuesta_listar')
    except ProtectedError:
        messages.error(request, 'No se puede eliminar la encuesta porque está asociada a otros registros.')
        return redirect('encuesta_detalle', encuesta_id=encuesta.id)
