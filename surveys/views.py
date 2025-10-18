from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models.deletion import ProtectedError

from registration.models import Profile
from registration.utils import has_admin_role
from .models import Encuesta
from .forms import EncuestaForm

@login_required
def encuesta_listar(request):
    encuestas = Encuesta.objects.all().order_by('-id')
    paginator = Paginator(encuestas, 10)
    page_number = request.GET.get('page')
    encuestas_page = paginator.get_page(page_number)

    return render(request, 'surveys/encuesta_listar.html', {'encuestas': encuestas_page})


@login_required
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


@login_required
def encuesta_ver(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)
    return render(request, 'surveys/encuesta_ver.html', {'encuesta': encuesta})


@login_required
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


@login_required
def encuesta_bloquear(request, encuesta_id):
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)
    encuesta.estado = not encuesta.estado
    estado_str = "activada" if encuesta.estado else "bloqueada"
    encuesta.save(update_fields=['estado'])
    messages.success(request, f'Encuesta "{encuesta.titulo}" {estado_str} correctamente.')
    return redirect('encuesta_listar')


@login_required
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
