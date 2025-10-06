from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from orgs.models import Direccion

from registration.models import Profile

@login_required
def direccion_crear(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'Error: No se encontró el perfil del usuario.')
        return redirect('login')

    if profile.group_id != 1:
        return redirect('logout')

    User = get_user_model()
    usuarios = User.objects.all().order_by('username')

    return render(request, 'locations/direccion_crear.html', {
        'usuarios': usuarios,
    })


@login_required
def direccion_guardar(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'Error: No se encontró el perfil del usuario.')
        return redirect('login')

    if profile.group_id != 1:
        return redirect('logout')

    if request.method != 'POST':
        messages.warning(request, 'Método no permitido.')
        return redirect('direccion_crear')

    usuario_id = request.POST.get('usuario_id', '').strip()
    nombre = request.POST.get('nombre', '').strip()

    if not usuario_id:
        messages.error(request, 'Debe seleccionar un usuario.')
        return redirect('direccion_crear')

    if not nombre:
        messages.error(request, 'Debe ingresar un nombre para la dirección.')
        return redirect('direccion_crear')

    User = get_user_model()
    user = get_object_or_404(User, pk=usuario_id)

    if Direccion.objects.filter(usuario_id=user.id).exists():
        messages.warning(request, 'Ese usuario ya tiene una dirección asociada.')
        return redirect('direccion_crear')

    Direccion.objects.create(usuario_id=user.id, nombre=nombre)
    messages.success(request, 'Dirección creada correctamente.')
    return redirect('main_direccion')

