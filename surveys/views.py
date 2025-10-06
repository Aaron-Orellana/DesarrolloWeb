from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Encuesta

PRIORIDADES = ['Alta', 'Media', 'Baja']

@login_required
def encuesta_crear(request):
    return render(request, 'surveys/encuesta_crear.html', {
        'prioridades': PRIORIDADES,
    })

@login_required
def encuesta_guardar(request):
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
    encuestas = Encuesta.objects.all().order_by('-id')
    return render(request, 'surveys/encuesta_listar.html', {'encuestas': encuestas})
