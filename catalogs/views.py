from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from registration.models import Profile
from orgs.models import Direccion, Departamento

from surveys.models import Encuesta
from .models import Incidencia
from .forms import IncidenciaForm


@login_required
def incidencia_listar(request):
    profile = Profile.objects.filter(user_id=request.user.id).first()
    if not profile or profile.group_id != 1:
        return redirect('logout')

    incidencias_list = Incidencia.objects.all().order_by('-incidencia_id')
    paginator = Paginator(incidencias_list, 10)
    page_number = request.GET.get('page')
    incidencias = paginator.get_page(page_number)

    return render(request, 'catalogs/incidencia_listar.html', {'incidencias': incidencias})


@login_required
def incidencia_crear(request):
    profile = Profile.objects.filter(user_id=request.user.id).first()
    if not profile or profile.group_id != 1:
        return redirect('logout')

    if request.method == 'POST':
        form = IncidenciaForm(request.POST)
        if form.is_valid():
            incidencia = form.save()
            messages.success(request, f'Incidencia "{incidencia.nombre}" creada correctamente.')
            return redirect('incidencia_listar')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = IncidenciaForm()

    return render(request, 'catalogs/incidencia_crear.html', {'form': form})


@login_required
def incidencia_ver(request, incidencia_id):
    profile = Profile.objects.filter(user_id=request.user.id).first()
    if not profile or profile.group_id != 1:
        return redirect('logout')

    incidencia = get_object_or_404(Incidencia, pk=incidencia_id)
    return render(request, 'catalogs/incidencia_ver.html', {'incidencia': incidencia})


@login_required
def incidencia_editar(request, incidencia_id):
    profile = Profile.objects.filter(user_id=request.user.id).first()
    if not profile or profile.group_id != 1:
        return redirect('logout')

    incidencia = get_object_or_404(Incidencia, pk=incidencia_id)

    if request.method == 'POST':
        form = IncidenciaForm(request.POST, instance=incidencia)
        if form.is_valid():
            form.save()
            messages.success(request, f'Incidencia "{incidencia.nombre}" actualizada correctamente.')
            return redirect('incidencia_listar')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = IncidenciaForm(instance=incidencia)

    return render(request, 'catalogs/incidencia_editar.html', {'form': form, 'incidencia': incidencia})


@login_required
def incidencia_eliminar(request, incidencia_id):
    profile = Profile.objects.filter(user_id=request.user.id).first()
    if not profile or profile.group_id != 1:
        return redirect('logout')

    incidencia = get_object_or_404(Incidencia, pk=incidencia_id)
    incidencia.delete()
    messages.success(request, f'Incidencia "{incidencia.nombre}" eliminada correctamente.')
    return redirect('incidencia_listar')


@login_required
def incidencia_bloquear(request, incidencia_id):
    profile = Profile.objects.filter(user_id=request.user.id).first()
    if not profile or profile.group_id != 1:
        return redirect('logout')

    incidencia = get_object_or_404(Incidencia, pk=incidencia_id)
    incidencia.estado = not incidencia.estado
    incidencia.save(update_fields=['estado'])

    estado_str = "bloqueada" if not incidencia.estado else "activada"
    messages.success(request, f'Incidencia "{incidencia.nombre}" {estado_str} correctamente.')
    return redirect('incidencia_listar')

