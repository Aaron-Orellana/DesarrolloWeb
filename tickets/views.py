from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SolicitudIncidencia, Multimedia
from orgs.models import Profile, Cuadrilla
from .forms import SolicitudIncidenciaForm 
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import CreateView
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
            return redirect('solicitud_listar')
        else:
            messages.error(request, 'Error al guardar. Revise los datos del formulario.')
    else:
        form = SolicitudIncidenciaForm(instance=solicitud)
    return render(request, 'tickets/solicitud_editar.html', {'form': form, 'solicitud': solicitud})


class MultimediaListView(LoginRequiredMixin, ListView):
    model = Multimedia
    template_name = 'tickets/multimedia_listar.html'
    context_object_name = 'multimedias'

    def get_queryset(self):
        solicitud_id = self.kwargs['solicitud_incidencia_id']
        return Multimedia.objects.filter(
            solicitud_incidencia_id=solicitud_id
        ).select_related('solicitud_incidencia')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['solicitud'] = SolicitudIncidencia.objects.get(pk=self.kwargs['solicitud_incidencia_id'])
        return context


class MultimediaCreateView(LoginRequiredMixin, CreateView):
    model = Multimedia
    fields = ['archivo', 'tipo']
    template_name = 'tickets/multimedia_crear.html'

    def get_initial(self):
        solicitud_incidencia_id = self.kwargs['solicitud_incidencia_id']
        return {'solicitud_incidencia': solicitud_incidencia_id}

    def form_valid(self, form):
        profile = self.request.user.profile
        solicitud = SolicitudIncidencia.objects.get(pk=self.kwargs['solicitud_incidencia_id'])
        #if not Cuadrilla.objects.filter(profile=profile, estado=True, pk=solicitud.cuadrilla_id).exists():
        #   raise PermissionDenied("No estás asignado a la cuadrilla de esta solicitud o la cuadrilla no está activa.")

        multimedia = form.save(commit=False)
        multimedia.solicitud_incidencia = solicitud
        multimedia.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('multimedia_listar', kwargs={'solicitud_incidencia_id': self.kwargs['solicitud_incidencia_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['solicitud'] = SolicitudIncidencia.objects.get(pk=self.kwargs['solicitud_incidencia_id'])
        return context