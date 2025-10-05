from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Direccion, Departamento
from registration.models import Profile
from django.contrib import messages
from django.contrib.auth.models import User

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



@login_required
def main_direccion(request):
    # Seguridad básica por perfil
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')

    if profile.group_id != 1:  # solo Admin SECPLA
        return redirect('logout')

    direcciones_qs = Direccion.objects.select_related('usuario').all().order_by('direccion_id')
    direcciones = list(direcciones_qs)

    usuario_ids = [d.usuario_id for d in direcciones if d.usuario_id]
    usuarios_por_id = {u.id: u for u in User.objects.filter(id__in=usuario_ids)}

    for direccion in direcciones:
        direccion.usuario_auth = usuarios_por_id.get(direccion.usuario_id)

    template_name = 'orgs/main_direccion.html'
    ctx = {'direcciones': direcciones}
    return render(request, template_name, ctx)


# Formulario crear
@login_required
def direccion_crear(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')

    if profile.group_id != 1:
        return redirect('logout')

    # Puedes filtrar usuarios si quieres (p. ej., que no estén ya usados en Direccion)
    usados = Direccion.objects.values_list('usuario_id', flat=True)
    User = get_user_model()
    usuarios = User.objects.exclude(id__in=usados)

    template_name = 'orgs/create_direccion.html'
    ctx = {'usuarios': usuarios}
    return render(request, template_name, ctx)


# Guardar
@login_required
def direccion_guardar(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')

    if profile.group_id != 1:
        return redirect('logout')

    if request.method != 'POST':
        return redirect('main_direccion')

    usuario_id = request.POST.get('usuario_id', '').strip()
    direccion = request.POST.get('direccion')

    if not usuario_id:
        messages.warning(request, 'Debes seleccionar un usuario.')
        return redirect('create_direccion')

    if not direccion:
        messages.warning(request, 'Debe ingresar una direccion')
        return redirect('create_direccion')
    
    # validar que exista el usuario
    User = get_user_model()
    user = get_object_or_404(User, pk=usuario_id)
    
    # validar que no exista otra Dirección con ese usuario
    if Direccion.objects.filter(usuario_id=user.id).exists():
        messages.warning(request, 'Ese usuario ya tiene una Dirección asociada.')
        return redirect('create_direccion')

    # crear (forma correcta: usar *_id o pasar la instancia)
    Direccion.objects.create(usuario_id=user.id, nombre=direccion)

    messages.success(request, 'Dirección creada exitosamente.')
    return redirect('main_direccion')
