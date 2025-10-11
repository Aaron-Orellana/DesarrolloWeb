from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Direccion, Departamento
from registration.models import Profile
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

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
        return redirect('logout')

@login_required
def departamento_guardar(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('check_profile')
    
    if profile.group_id != 1:
        return redirect('logout')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        direccion_id = request.POST.get('direccion_id', '').strip()
        
        if not nombre or not direccion_id:
            messages.warning(request, 'Debes ingresar toda la información')
            return redirect('departamento_crear')
        
        # Verificar que la dirección existe
        try:
            direccion = Direccion.objects.get(pk=direccion_id)
        except Direccion.DoesNotExist:
            print("direccion no existe")
            messages.error(request, 'La dirección seleccionada no existe')
            return redirect('departamento_crear')
        existe = Departamento.objects.filter(direccion=direccion, nombre=nombre).exists()
        if existe:
            messages.error(request, 'Ya existe un departamento con ese nombre en la dirección seleccionada.')
            return redirect('departamento_crear')
        # Guardar el departamento
        departamento_save = Departamento(
            nombre=nombre,
            direccion=direccion
        )
        departamento_save.save()
        
        messages.success(request, 'Departamento ingresado con éxito')
        return redirect('departamento_listar')  # Redirigir a la lista
    else:
        messages.warning(request, 'Método no permitido')
        return redirect('departamento_crear')

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
def departamento_ver(request, departamento_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('logout')
    if profile.group_id == 1:
        try:
            departamento_count = Departamento.objects.filter(pk=departamento_id).count()
            if departamento_count <= 0:
                messages.add_message(request, messages.INFO, 'Hubo un error')
                return redirect('check_profile')
            departamento_data = Departamento.objects.get(pk=departamento_id)
        except:
            messages.add_message(request, messages.INFO, 'Hubo un error')
            return redirect('check_profile')
        template_name = 'orgs/departamento_ver.html'
        return render(request, template_name, {'departamento_data':departamento_data})
    else:
        return redirect('logout')

@login_required
def departamento_editar(request,departamento_id=None):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error')
        return redirect('logout')
    if profile.group_id == 1:
        try:
            if request.method == 'POST':
                id_departamento = request.POST.get('id_departamento')
                nombre = request.POST.get('nombre', '').strip() 
                direccion_id = request.POST.get('direccion_id', '').strip()
                departamento_count = Departamento.objects.filter(pk=id_departamento).count()
                if departamento_count <= 0:
                    messages.add_message(request, messages.INFO, 'Hubo un error')
                    return redirect('logout')
                if nombre == '' or direccion_id == '':
                    messages.warning(request, 'Debes ingresar toda la información')
                    return redirect('departamento_editar', departamento_id=departamento_id)
                #Verificar que la Dirección exista
                try:
                    direccion_obj = Direccion.objects.get(pk=direccion_id)
                except Direccion.DoesNotExist:
                    messages.error(request, 'La dirección seleccionada no existe.')
                    return redirect('departamento_editar', departamento_id=id_departamento)
                #Validar si existe otro departamento con el mismo nombre en la direccion
                existe = Departamento.objects.filter(direccion=direccion_obj, nombre=nombre).exclude(pk=id_departamento).exists()
                if existe:
                    messages.error(request, 'Ya existe otro departamento con ese nombre en la dirección seleccionada.')
                    return redirect('departamento_editar', departamento_id=id_departamento)
                Departamento.objects.filter(pk=id_departamento).update(nombre=nombre)
                Departamento.objects.filter(pk=id_departamento).update(direccion_id=direccion_id)
                messages.success(request, 'Departamento actualizado con éxito')
                return redirect('departamento_listar')
        except:
            messages.add_message(request, messages.INFO, 'Hubo un error')
            return redirect('check_profile')
        try:
            departamento_count = Departamento.objects.filter(pk=departamento_id).count()
            if departamento_count <= 0:
                messages.add_message(request, messages.INFO, 'Hubo un error')
                return redirect('check_profile')
            departamento_data = Departamento.objects.get(pk=departamento_id)
            direcciones = Direccion.objects.all() 
        except:
            messages.add_message(request, messages.INFO, 'Hubo un error')
            return redirect('logout')
        template_name = 'orgs/departamento_editar.html'
        return render(request, template_name, {'departamento_data':departamento_data, 'direcciones':direcciones})
    else:
        return redirect('logout')

@login_required
def direccion_listar(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')

    if profile.group_id != 1:
        return redirect('logout')

    direcciones_qs = (
        Direccion.objects
        .select_related('usuario')
        .prefetch_related('Departamento')
        .order_by('direccion_id')
    )
    direcciones = list(direcciones_qs)

    usuario_ids = [d.usuario_id for d in direcciones if d.usuario_id]
    usuarios_por_id = {u.id: u for u in User.objects.filter(id__in=usuario_ids)}

    for direccion in direcciones:
        direccion.usuario_auth = usuarios_por_id.get(direccion.usuario_id)
        departamentos_rel = getattr(direccion, 'Departamento', None)
        if departamentos_rel is not None:
            direccion.departamentos_list = [dep.nombre for dep in departamentos_rel.all()]
        else:
            direccion.departamentos_list = []

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
        return redirect('direccion_crear')

    if not direccion:
        messages.warning(request, 'Debe ingresar una direccion')
        return redirect('direccion_crear')
    
    # validar que exista el usuario
    User = get_user_model()
    user = get_object_or_404(User, pk=usuario_id)
    
    # validar que no exista otra Dirección con ese usuario
    if Direccion.objects.filter(usuario_id=user.id).exists():
        messages.warning(request, 'Ese usuario ya tiene una Dirección asociada.')
        return redirect('direccion_crear')

    # crear (forma correcta: usar *_id o pasar la instancia)
    Direccion.objects.create(usuario_id=user.id, nombre=direccion)

    messages.success(request, 'Dirección creada exitosamente.')
    return redirect('direccion_listar')

@login_required
def direccion_ver(request,direccion_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')

    if profile.group_id != 1:
        return redirect('logout')
    try:
        direccion = Direccion.objects.get(pk=direccion_id)
    except Direccion.DoesNotExist:
        messages.error(request, 'La dirección no existe.')
        return redirect('direccion_listar')
    return render(request, 'orgs/direccion_ver.html',{'direccion':direccion})
        
@login_required
def direccion_editar(request,direccion_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')

    if profile.group_id != 1:
        return redirect('logout')
    try:
        direccion = Direccion.objects.get(pk=direccion_id)
    except Direccion.DoesNotExist:
        messages.error(request, 'La dirección no existe.')
        return redirect('direccion_listar')

    usados = Direccion.objects.exclude(pk=direccion_id).values_list('usuario_id', flat=True)
    usuarios = User.objects.exclude(id__in=usados)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        usuario_id = request.POST.get('usuario', '').strip()

        #validaciones
        if not nombre:
            messages.error(request,' El nombre es obligatorio.')
            return redirect('direccion_editar',direccion_id = direccion_id)
        if not usuario_id:
            messages.error(request, 'Debes seleccionar un usuario.')
            return redirect('direccion_crear')
        if Direccion.objects.filter(nombre=nombre).exclude(direccion_id=direccion_id).exists():
            messages.error(request, 'Ya existe una dirección con ese nombre.')
            return redirect('direccion_editar', direccion_id=direccion_id)
        try:
            usuario = User.objects.get(pk=usuario_id)
        except User.DoesNotExist:
            messages.error(request, 'El usuario seleccionado no existe.')
            return redirect('direccion_editar', direccion_id=direccion_id)
        direccion.nombre = nombre
        direccion.usuario = usuario
        direccion.save()
        messages.success(request, 'Direccion actualizada correctamente.')
        return redirect('direccion_listar')
    return render(request, 'orgs/direccion_editar.html', {
        'direccion': direccion,
        'usuarios': usuarios,})
    


def direccion_bloquea(request, direccion_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')

    if profile.group_id != 1:
        return redirect('logout')
    
    if profile.group_id == 1:
        direccion_count = Direccion.objects.filter(direccion_id=direccion_id).count()
        if direccion_count <= 0:
            messages.add_message(request, messages.INFO, 'Hubo un error')
            return redirect('logout')
        
        Direccion.objects.filter(direccion_id=direccion_id).update(estado='Bloqueado')
        messages.add_message(request, messages.INFO, 'Dirección bloqueada con éxito')
        return redirect('direccion_listar')
    else:
        return redirect('logout')

def direccion_desbloquea(request, direccion_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')

    if profile.group_id != 1:
        return redirect('logout')
    
    if profile.group_id == 1:
        direccion_count = Direccion.objects.filter(direccion_id=direccion_id).count()
        if direccion_count <= 0:
            messages.add_message(request, messages.INFO, 'Hubo un error')
            return redirect('logout')
        
        Direccion.objects.filter(direccion_id=direccion_id).update(estado='Activo')
        messages.add_message(request, messages.INFO, 'Dirección desbloqueada con éxito')
        return redirect('direccion_listar')
    else:
        return redirect('logout')

def direccion_elimina(request, direccion_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return redirect('login')

    if profile.group_id != 1:
        return redirect('logout')
    
    if profile.group_id == 1:
        direccion_count = Direccion.objects.filter(direccion_id=direccion_id).count()
        if direccion_count <= 0:
            messages.add_message(request, messages.INFO, 'Hubo un error')
            return redirect('check_profile')
        
        try:
            direccion = Direccion.objects.get(direccion_id=direccion_id)
            direccion.delete()
            messages.add_message(request, messages.INFO, 'Dirección eliminada con éxito')
        except:
            messages.add_message(request, messages.INFO, 'No se puede eliminar la dirección porque está asociada a un departamento')
        return redirect('direccion_listar')
    else:
        return redirect('logout')
