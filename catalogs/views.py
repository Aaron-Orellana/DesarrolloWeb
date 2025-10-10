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
        # Guardar encuesta si se selecciona
    encuesta_id = request.POST.get('encuesta')
    if encuesta_id:
        try:
            encuesta = Encuesta.objects.get(pk=encuesta_id)
            incidencia.encuesta = encuesta
        except Encuesta.DoesNotExist:
            incidencia.encuesta = None
    else:
        incidencia.encuesta = None

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

@login_required
def incidencia_ver(request, incidencia_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    if profile.group_id != 1:
        return redirect('logout')

    # Verificar si la incidencia existe
    if Incidencia.objects.filter(pk=incidencia_id).count() == 0:
        messages.error(request, 'La incidencia no existe.')
        return redirect('incidencia_listar')

    incidencia = Incidencia.objects.get(pk=incidencia_id)

    return render(request, 'catalogs/incidencia_ver.html', {
        'incidencia': incidencia,
    })

@login_required
def incidencia_editar(request, incidencia_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    if profile.group_id != 1:
        return redirect('logout')

    if Incidencia.objects.filter(pk=incidencia_id).count() == 0:
        messages.error(request, 'La incidencia no existe.')
        return redirect('incidencia_listar')

    incidencia = Incidencia.objects.get(pk=incidencia_id)
    direcciones = Direccion.objects.all()
    departamentos = Departamento.objects.all()
    encuestas = Encuesta.objects.all().order_by('titulo')

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        direccion_id = request.POST.get('direccion')
        departamento_id = request.POST.get('departamento')
        encuesta_id = request.POST.get('encuesta')

        # Validaciones básicas
        if not nombre:
            messages.error(request, 'El nombre es obligatorio.')
            return redirect('incidencia_editar', incidencia_id=incidencia_id)

        if not direccion_id or not departamento_id:
            messages.error(request, 'Debe seleccionar una dirección y un departamento.')
            return redirect('incidencia_editar', incidencia_id=incidencia_id)

        try:
            direccion = Direccion.objects.get(direccion_id=direccion_id)
        except Direccion.DoesNotExist:
            messages.error(request, 'La dirección seleccionada no existe.')
            return redirect('incidencia_editar', incidencia_id=incidencia_id)

        try:
            departamento = Departamento.objects.get(departamento_id=departamento_id)
        except Departamento.DoesNotExist:
            messages.error(request, 'El departamento seleccionado no existe.')
            return redirect('incidencia_editar', incidencia_id=incidencia_id)

        if departamento.direccion != direccion:
            messages.error(request, 'El departamento no pertenece a la dirección seleccionada.')
            return redirect('incidencia_editar', incidencia_id=incidencia_id)

        incidencia.nombre = nombre
        incidencia.descripcion = descripcion
        incidencia.direccion = direccion
        incidencia.departamento = departamento

        if encuesta_id:
            try:
                encuesta = Encuesta.objects.get(pk=encuesta_id)
                incidencia.encuesta = encuesta
                print("Encuesta asignada:", encuesta.titulo)
            except Encuesta.DoesNotExist:
                incidencia.encuesta = None
                print("Encuesta no encontrada.")
        else:
            incidencia.encuesta = None
            print("Sin encuesta seleccionada.")

        print("Encuesta seleccionada:", encuesta_id)
        print("Encuesta asignada al objeto:", incidencia.encuesta)


        incidencia.save()
        messages.success(request, 'Incidencia actualizada correctamente.')
        return redirect('incidencia_listar')

    return render(request, 'catalogs/incidencia_editar.html', {
        'incidencia': incidencia,
        'direcciones': direcciones,
        'departamentos': departamentos,
        'encuestas': encuestas,
    })

@login_required
def incidencia_eliminar(request, incidencia_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    if profile.group_id != 1:
        return redirect('logout')

    if Incidencia.objects.filter(pk=incidencia_id).count() == 0:
        messages.error(request, 'La incidencia no existe o ya fue eliminada.')
        return redirect('incidencia_listar')

    Incidencia.objects.filter(pk=incidencia_id).delete()
    messages.success(request, 'Incidencia eliminada correctamente.')
    return redirect('incidencia_listar')
