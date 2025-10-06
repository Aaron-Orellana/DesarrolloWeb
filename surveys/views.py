from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Encuesta
from catalogs.models import Incidencia

PRIORIDADES = ['Alta', 'Media', 'Baja']

@login_required
def encuesta_crear(request):
    incidencias = Incidencia.objects.all().order_by('nombre')
    return render(request, 'surveys/encuesta_crear.html', {
        'incidencias': incidencias,
        'prioridades': PRIORIDADES,
    })

@login_required
def encuesta_guardar(request):
    if request.method == 'POST':
        titulo = (request.POST.get('titulo') or '').strip()
        descripcion = (request.POST.get('descripcion') or '').strip()
        prioridad = (request.POST.get('prioridad') or '').strip()
        incidencia_id = request.POST.get('incidencia')

        if not titulo:
            messages.error(request, 'El título de la encuesta es obligatorio.')
            return redirect('encuesta_crear')

        if not incidencia_id:
            messages.error(request, 'Debe seleccionar un tipo de incidencia.')
            return redirect('encuesta_crear')

        if prioridad not in PRIORIDADES:
            messages.error(request, 'Debe seleccionar una prioridad válida.')
            return redirect('encuesta_crear')

        # Validar incidencia
        try:
            incidencia = Incidencia.objects.get(pk=incidencia_id)
        except Incidencia.DoesNotExist:
            messages.error(request, 'El tipo de incidencia seleccionado no existe.')
            return redirect('encuesta_crear')

        # Crear registro
        encuesta = Encuesta(
            titulo=titulo,
            descripcion=descripcion,
            prioridad=prioridad,
            incidencia=incidencia
        )
        encuesta.save()
        messages.success(request, 'Encuesta creada correctamente.')
        return redirect('encuesta_listar')

    return redirect('encuesta_crear')

@login_required
def encuesta_listar(request):
    encuestas_list = Encuesta.objects.select_related('incidencia').order_by('-id')
    return render(request, 'surveys/encuesta_listar.html', {'encuestas': encuestas_list})
