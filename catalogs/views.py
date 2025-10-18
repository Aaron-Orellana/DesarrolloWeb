from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from registration.models import Profile
from registration.utils import has_admin_role
from orgs.models import Direccion, Departamento

from surveys.models import Encuesta
from .models import Incidencia
from .forms import IncidenciaForm


@login_required
def incidencia_listar(request):

    incidencias_list = Incidencia.objects.all().order_by('-incidencia_id')
    paginator = Paginator(incidencias_list, 10)
    page_number = request.GET.get('page')
    incidencias = paginator.get_page(page_number)

    return render(request, 'catalogs/incidencia_listar.html', {'incidencias': incidencias})


@login_required
def incidencia_crear(request):
    direcciones = Direccion.objects.filter(estado=True).order_by('nombre')
    departamentos = Departamento.objects.filter(estado=True).order_by('nombre')
    encuestas = Encuesta.objects.filter(estado=True).order_by('titulo')

    if request.method == 'POST':
        form = IncidenciaForm(request.POST)
        if form.is_valid():
            incidencia = form.save(commit=False)
            
            if incidencia.departamento.direccion != incidencia.direccion:
                messages.error(request, 'El departamento no pertenece a la dirección seleccionada.')
                return redirect('incidencia_crear')
            incidencia.save()
            messages.success(request, f'✅ Incidencia "{incidencia.nombre}" creada correctamente.')
            return redirect('incidencia_listar')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = IncidenciaForm()

    return render(request, 'catalogs/incidencia_crear.html', {
        'form': form,
        'direcciones': direcciones,
        'departamentos': departamentos,
        'encuestas': encuestas
    })


@login_required
def incidencia_ver(request, incidencia_id):
    incidencia = get_object_or_404(Incidencia, pk=incidencia_id)
    return render(request, 'catalogs/incidencia_ver.html', {'incidencia': incidencia})


@login_required
def incidencia_editar(request, incidencia_id):
    incidencia = get_object_or_404(Incidencia, pk=incidencia_id)

    if request.method == 'POST':
        form = IncidenciaForm(request.POST, instance=incidencia)
        if form.is_valid():
            incidencia = form.save(commit=False)
            if incidencia.departamento.direccion != incidencia.direccion:
                messages.error(request, 'El departamento no pertenece a la dirección seleccionada.')
                return redirect('incidencia_editar', incidencia_id=incidencia_id)
            
            incidencia.save()
            messages.success(request, f'Incidencia "{incidencia.nombre}" actualizada correctamente.')
            return redirect('incidencia_listar')
        else:
            messages.error(request, 'Corregir errores del formulario.')
    else:
        form = IncidenciaForm(instance=incidencia)

    return render(request, 'catalogs/incidencia_editar.html', {'form': form, 'incidencia': incidencia})



@login_required
def incidencia_eliminar(request, incidencia_id):

    incidencia = get_object_or_404(Incidencia, pk=incidencia_id)
    incidencia.delete()
    messages.success(request, f'Incidencia "{incidencia.nombre}" eliminada correctamente.')
    return redirect('incidencia_listar')


@login_required
def incidencia_bloquear(request, incidencia_id):

    incidencia = get_object_or_404(Incidencia, pk=incidencia_id)
    incidencia.estado = not incidencia.estado
    estado_str = "activada" if incidencia.estado else "bloqueada"
    incidencia.save(update_fields=['estado'])
    messages.success(request, f'Incidencia "{incidencia.nombre}" {estado_str} correctamente.')
    return redirect('incidencia_listar')

    
