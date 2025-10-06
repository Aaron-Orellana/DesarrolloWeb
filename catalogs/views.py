from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Incidencia
from orgs.models import Direccion, Departamento
from django.core.paginator import Paginator #Objeto para paginar resultados (usado en vistas)
from surveys.models import Encuesta
from registration.models import Profile

@login_required
def incidencia_crear(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile') 
    if profile.group_id != 1:
        return redirect('logout')

    direcciones = Direccion.objects.all()
    departamentos = Departamento.objects.all() 
    encuestas = Encuesta.objects.all().order_by('titulo')
    return render(request, 'catalogs/incidencia_crear.html', {  
        'direcciones': direcciones,
        'departamentos': departamentos,
        'encuestas': encuestas,
    })

@login_required
def incidencia_guardar(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile') 
    if profile.group_id != 1:
        return redirect('logout')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        direccion_id = request.POST.get('direccion')
        departamento_id = request.POST.get('departamento')

        if not nombre:
            messages.error(request, 'El nombre de la incidencia es requerido.')
            return redirect('incidencia_crear')

        if not direccion_id or not departamento_id:
            messages.error(request, 'Debe seleccionar una dirección y un departamento.')
            return redirect('incidencia_crear')

        try:
            direccion = Direccion.objects.get(direccion_id=direccion_id)
        except Direccion.DoesNotExist:
            messages.error(request, 'La dirección seleccionada no existe.')
            return redirect('incidencia_crear')

        try:
            departamento = Departamento.objects.get(departamento_id=departamento_id)
        except Departamento.DoesNotExist:
            messages.error(request, 'El departamento seleccionado no existe.')
            return redirect('incidencia_crear')

        if departamento.direccion != direccion:
            messages.error(request, 'El departamento seleccionado no pertenece a la dirección elegida.')
            return redirect('incidencia_crear')

        incidencia = Incidencia(
            nombre=nombre,
            descripcion=descripcion,
            direccion=direccion,
            departamento=departamento,
        )
        incidencia.save()

        messages.success(request, 'Incidencia creada exitosamente.')
        return redirect('incidencia_listar')

    return redirect('incidencia_crear')
@login_required
def incidencia_listar(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile') 
    if profile.group_id != 1:
        return redirect('logout')

    incidencias_list = Incidencia.objects.all().order_by('-incidencia_id')  #ID auto incrementable, mas bajo primero
    paginator = Paginator(incidencias_list, 10)
    page_number = request.GET.get('page')
    incidencias = paginator.get_page(page_number)
    
    return render(request, 'catalogs/incidencia_listar.html', {
        'incidencias': incidencias,
    })