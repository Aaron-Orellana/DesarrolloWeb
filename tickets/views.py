from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SolicitudIncidencia
from orgs.models import Profile
from .forms import SolicitudIncidenciaForm 
@login_required
def solicitud_listar(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')
    solicitudes = SolicitudIncidencia.objects.select_related('incidencia', 'cuadrilla', 'ubicacion', 'territorial', 'vecino').all().order_by('-fecha')
    return render(request, 'tickets/solicitud_listar.html', {'solicitudes': solicitudes})

@login_required
def solicitud_crear(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except Profile.DoesNotExist:
        messages.error(request, 'Hubo un error con tu perfil.')
        return redirect('logout')
    if request.method == 'POST':
        form = SolicitudIncidenciaForm(request.POST)
        if form.is_valid():
            form.save() 
            messages.success(request, 'Solicitud de incidencia creada correctamente.')
            return redirect('solicitud_listar')
        else:
            messages.error(request, 'Error al guardar. Revise los datos del formulario.')
    else:
        form = SolicitudIncidenciaForm()
    return render(request, 'tickets/solicitud_crear.html', {'form': form})

@login_required
def solicitud_editar(request, solicitud_incidencia_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except Profile.DoesNotExist:
        messages.error(request, 'Hubo un error con tu perfil.')
        return redirect('logout')
    solicitud = get_object_or_404(SolicitudIncidencia, pk=solicitud_incidencia_id)
    if request.method == 'POST':
        form = SolicitudIncidenciaForm(request.POST, instance=solicitud)
        if form.is_valid():
            form.save() 
            messages.success(request, f'Solicitud #{solicitud.pk} actualizada con éxito.')
            return redirect('solicitud_detalle', solicitud_incidencia_id=solicitud.pk)
        else:
            messages.error(request, 'Error al guardar. Revise los datos del formulario.')
    else:
        form = SolicitudIncidenciaForm(instance=solicitud)
    return render(request, 'tickets/solicitud_editar.html', {'form': form, 'solicitud': solicitud})