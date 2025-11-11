from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SolicitudIncidencia, Multimedia, RespuestaCuadrilla, MultimediaCuadrilla
from orgs.models import Profile, Cuadrilla
from .forms import SolicitudIncidenciaForm 
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import CreateView
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import datetime
from django.utils.timezone import now
from core.decorators import role_required, RoleRequiredMixin

@role_required("Secpla","Territoriales","Direcciones","Departamentos","Cuadrillas")
def solicitud_listar(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')

    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip()
    cuadrilla = request.GET.get('cuadrilla', '').strip()
    fecha = request.GET.get('fecha', '').strip()

    solicitudes = SolicitudIncidencia.objects.select_related(
        'incidencia', 'cuadrilla', 'ubicacion', 'territorial', 'encuesta'
    ).all().order_by('-fecha')

    filtros = Q()
    if q:
        filtros &= Q(encuesta__titulo__icontains=q) | Q(incidencia__nombre__icontains=q) | Q(vecino__email__icontains=q)
    if estado:
        filtros &= Q(estado__iexact=estado)  
    if cuadrilla:
        filtros &= Q(cuadrilla__nombre__icontains=cuadrilla)
    if fecha:
        try:
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
            filtros &= Q(fecha__date=fecha_dt.date())
        except ValueError:
            messages.warning(request, "Formato de fecha desde inválido. Usa YYYY-MM-DD.")

    solicitudes = solicitudes.filter(filtros)
    paginator = Paginator(solicitudes, 10)
    page_number = request.GET.get('page')
    solicitudes_page = paginator.get_page(page_number)
    sin_resultados = not solicitudes.exists()
    if sin_resultados:
        messages.info(request, 'No se encontraron resultados con los filtros seleccionados.')
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_string = query_params.urlencode()

    return render(request, 'tickets/solicitud_listar.html', {
        'solicitudes': solicitudes_page,
        'sin_resultados': sin_resultados,
        'query_string': query_string,
        'request': request,
    })

@role_required("Secpla","Territoriales","Direcciones")
def solicitud_crear(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except Profile.DoesNotExist:
        messages.error(request, 'Hubo un error con tu perfil.')
        return redirect('logout')
    if request.method == 'POST':
        form = SolicitudIncidenciaForm(request.POST)
        comentario = request.POST.get('comentario', '').strip()
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.territorial = request.user.profile.territorial
            if solicitud.cuadrilla:
                estado_anterior = solicitud.estado
                solicitud.estado = 'Derivada'

            solicitud.save()
            if solicitud.cuadrilla:
                solicitud.registrar_log(
                    profile= request.user.profile,
                    from_estado = estado_anterior, 
                    to_estado = solicitud.estado,
                    fecha = now(),
                    comentario =comentario
                    )
            messages.success(request, 'Solicitud de incidencia creada correctamente.')
            return redirect('solicitud_listar')
        else:
            messages.error(request, 'Error al guardar. Revise los datos del formulario.')
    else:
        form = SolicitudIncidenciaForm()
    return render(request, 'tickets/solicitud_crear.html', {'form': form})

@role_required("Secpla","Territoriales","Direcciones")
def solicitud_editar(request, solicitud_incidencia_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except Profile.DoesNotExist:
        messages.error(request, 'Hubo un error con tu perfil.')
        return redirect('logout')
    solicitud = get_object_or_404(SolicitudIncidencia, pk=solicitud_incidencia_id)
    cuadrilla_anterior = solicitud.cuadrilla
    if request.method == 'POST':
        form = SolicitudIncidenciaForm(request.POST, instance=solicitud)
        comentario = request.POST.get('comentario', '').strip()
        if form.is_valid():
            solicitud = form.save(commit=False)
            estado_anterior = solicitud.estado
            cuadrilla_actual = solicitud.cuadrilla
            
            if cuadrilla_anterior != cuadrilla_actual:
                if cuadrilla_actual:
                    solicitud.estado = 'Derivada'
                else:
                    solicitud.estado = 'Pendiente'
                

            solicitud.save()
            if estado_anterior != solicitud.estado:
                solicitud.registrar_log(
                    profile=request.user.profile,
                    from_estado=estado_anterior,
                    to_estado=solicitud.estado,
                    fecha=now(),
                    comentario = comentario
                )

            messages.success(request, f'Solicitud #{solicitud.pk} actualizada con éxito.')
            return redirect('solicitud_listar')
        else:
            messages.error(request, 'Error al guardar. Revise los datos del formulario.')
    else:
        form = SolicitudIncidenciaForm(instance=solicitud)
    return render(request, 'tickets/solicitud_editar.html', {'form': form, 'solicitud': solicitud})


@role_required("Secpla","Territoriales","Direcciones","Departamentos","Cuadrillas")
def solicitud_ver(request, solicitud_incidencia_id):
    solicitud = get_object_or_404(SolicitudIncidencia, pk=solicitud_incidencia_id)
    logs = solicitud.logs.all() 
    return render(request, 'tickets/solicitud_ver.html', {'solicitud': solicitud,'logs': logs,})





class MultimediaListView(RoleRequiredMixin, ListView):
    allowed_roles = ["Secpla","Territoriales","Direcciones","Departamentos","Cuadrillas"]
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


class MultimediaCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ["Secpla","Territoriales","Direcciones","Departamentos","Cuadrillas"]
    model = Multimedia
    fields = ['archivo', 'tipo']
    template_name = 'tickets/multimedia_crear.html'

    def get_initial(self):
        solicitud_incidencia_id = self.kwargs['solicitud_incidencia_id']
        return {'solicitud_incidencia': solicitud_incidencia_id}

    def form_valid(self, form):
        profile = self.request.user.profile
        solicitud = SolicitudIncidencia.objects.get(pk=self.kwargs['solicitud_incidencia_id'])
        if not Cuadrilla.objects.filter(profile=profile, estado=True, pk=solicitud.cuadrilla_id).exists():
            raise PermissionDenied("No estás asignado a la cuadrilla de esta solicitud o la cuadrilla no está activa.")

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
    
    
