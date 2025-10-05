from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Direccion, Departamento
from registration.models import Profile
from django.contrib import messages

@login_required
def departamento_crear(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    direcciones = Direccion.objects.all()
    if profile.group_id == 1:
        template_name = 'orgs/departamento_crear.html'
        return render(request, template_name, {'direcciones':direcciones})
    else:
        redirect('logout')

@login_required
def departamento_guardar(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    if profile.group_id == 1:
        if request.method == 'POST':
            nombre = request.POST.get('nombre')
            direccion_id = request.POST.get('direccion_id')
            if nombre == '' or direccion_id == '':
                messages.add_message(request,messages.INFO,'Debes ingresar toda la información')
                return redirect('departamento_crear')
            departamento_save = Departamento(
                nombre = nombre,
                direccion_id = direccion_id,
            )
            departamento_save.save()
            messages.add_message(request,messages.INFO,'Departamento ingresado con éxito')
            return redirect('orgs/departamento/')
        else:
            messages.add_message(request, messages.INFO, 'Hubo un error')
            return redirect('check_group_main')
    else:
        return redirect('logout')

@login_required
def departamento_listar(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    if profile.group_id == 1:
        departamentos = Departamento.objects.select_related('direccion').all()
        return render(request, 'orgs/departamento_listar.html', {'departamentos': departamentos})
    else:
        return redirect('logout')

@login_required
def direccion_listar(request):
    direcciones = Direccion.objects.all()
    return render(request, 'orgs/direccion_listar.html', {'direcciones': direcciones})
