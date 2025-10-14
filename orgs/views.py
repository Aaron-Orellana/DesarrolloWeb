from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from registration.models import Profile
from .models import Direccion, Departamento
from .forms import DireccionForm, DepartamentoForm  



@login_required
def direccion_listar(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')
    
    if profile.group_id != 1:
        return redirect('logout')

    direcciones = Direccion.objects.select_related('usuario').all().order_by('direccion_id')
    return render(request, 'orgs/direccion_listar.html', {'direcciones': direcciones})



@login_required

def direccion_crear(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')

    if profile.group_id != 1:
        return redirect('logout')

    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dirección creada correctamente.')
            return redirect('direccion_listar')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = DireccionForm()

    return render(request, 'orgs/create_direccion.html', {'form': form})

@login_required
def direccion_editar(request, direccion_id):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')
    
    if profile.group_id != 1:
        return redirect('logout')

    direccion = get_object_or_404(Direccion, pk=direccion_id)

    if request.method == 'POST':
        form = DireccionForm(request.POST, instance=direccion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dirección actualizada correctamente.')
            return redirect('direccion_listar')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = DireccionForm(instance=direccion)

    return render(request, 'orgs/direccion_editar.html', {'form': form, 'direccion': direccion})


@login_required
def direccion_ver(request, direccion_id):
    direccion = get_object_or_404(Direccion, pk=direccion_id)
    return render(request, 'orgs/direccion_ver.html', {'direccion': direccion})


@login_required
def direccion_bloquear(request, direccion_id):
    direccion = get_object_or_404(Direccion, pk=direccion_id)
    if direccion.estado == 'Activo':
        direccion.estado = 'Inactivo'
        messages.warning(request, f'La dirección "{direccion.nombre}" fue bloqueada.')
    else:
        direccion.estado = 'Activo'
        messages.success(request, f'La dirección "{direccion.nombre}" fue activada.')
    direccion.save()
    return redirect('direccion_listar')


@login_required
def direccion_eliminar(request, direccion_id):
    direccion = get_object_or_404(Direccion, pk=direccion_id)
    try:
        direccion.delete()
        messages.success(request, 'Dirección eliminada correctamente.')
    except:
        messages.error(request, 'No se puede eliminar: la dirección tiene departamentos asociados.')
    return redirect('direccion_listar')

@login_required
def departamento_listar(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')
    
    if profile.group_id != 1:
        return redirect('logout')

    departamentos = Departamento.objects.select_related('direccion').all()
    return render(request, 'orgs/departamento_listar.html', {'departamentos': departamentos})


@login_required
def departamento_crear(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')
    
    if profile.group_id != 1:
        return redirect('logout')

    if request.method == 'POST':
        form = DepartamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Departamento creado correctamente.')
            return redirect('departamento_listar')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = DepartamentoForm()

    return render(request, 'orgs/departamento_crear.html', {'form': form})


@login_required
def departamento_editar(request, departamento_id):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')
    
    if profile.group_id != 1:
        return redirect('logout')

    departamento = get_object_or_404(Departamento, pk=departamento_id)

    if request.method == 'POST':
        form = DepartamentoForm(request.POST, instance=departamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Departamento actualizado correctamente.')
            return redirect('departamento_listar')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = DepartamentoForm(instance=departamento)

    return render(request, 'orgs/departamento_editar.html', {
        'form': form,
        'departamento_data': departamento
    })


@login_required
def departamento_ver(request, departamento_id):
    departamento = get_object_or_404(Departamento, pk=departamento_id)
    return render(request, 'orgs/departamento_ver.html', {'departamento_data': departamento})

@login_required
def departamento_bloquear(request, departamento_id):
    departamento = get_object_or_404(Departamento, pk=departamento_id)
    if departamento.estado == 'Activo':
        departamento.estado = 'Inactivo'
        messages.warning(request, f'El departamento "{departamento.nombre}" fue bloqueado.')
    else:
        departamento.estado = 'Activo'
        messages.success(request, f'El departamento "{departamento.nombre}" fue activado.')
    departamento.save()
    return redirect('departamento_listar')


@login_required
def departamento_eliminar(request, departamento_id):
    departamento = get_object_or_404(Departamento, pk=departamento_id)
    try:
        departamento.delete()
        messages.success(request, 'Departamento eliminado correctamente.')
    except:
        messages.error(request, 'No se puede eliminar: puede tener dependencias.')
    return redirect('departamento_listar')

