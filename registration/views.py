from .forms import (
    UserCreationFormWithEmail,
    EmailForm,
    AdminUserCreateForm,
    AdminUserUpdateForm,
)
from django.views.generic import CreateView, View
from django.views.generic.edit import UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User, Group
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from .models import Profile

class SignUpView(CreateView):
    form_class = UserCreationFormWithEmail
    template_name = 'registration/signup.html'

    def get_success_url(self):
        return reverse_lazy('login') + '?register'
    
    def get_form(self, form_class=None):
        form = super(SignUpView,self).get_form()
        #modificamos en tiempo real
        form.fields['username'].widget = forms.TextInput(attrs={'class':'form-control mb-2','placeholder':'Nombre de usuario'})
        form.fields['email'].widget = forms.EmailInput(attrs={'class':'form-control mb-2','placeholder':'Dirección de correo'})
        form.fields['password1'].widget = forms.PasswordInput(attrs={'class':'form-control mb-2','placeholder':'Ingrese su contraseña'})
        form.fields['password2'].widget = forms.PasswordInput(attrs={'class':'form-control mb-2','placeholder':'Re ingrese su contraseña'})    
        return form

@method_decorator(login_required, name='dispatch')
class ProfileUpdate(UpdateView):

    success_url = reverse_lazy('profile')
    template_name = 'registration/profiles_form.html'

    def get_object(self):
        #recuperasmo el objeto a editar
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

@method_decorator(login_required, name='dispatch')
class EmailUpdate(UpdateView):
    form_class = EmailForm
    success_url = reverse_lazy('check_group_main')
    template_name = 'registration/profile_email_form.html'

    def get_object(self):
        #recuperasmo el objeto a editar
        return self.request.user
    
    def get_form(self, form_class=None):
        form = super(EmailUpdate,self).get_form()
        #modificamos en tiempo real
        form.fields['email'].widget = forms.EmailInput(attrs={'class':'form-control mb-2','placeholder':'Dirección de correo'})
        return form
@login_required
def profile_edit(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        mobile = request.POST.get('mobile')
        phone = request.POST.get('phone')
        User.objects.filter(pk=request.user.id).update(first_name=first_name)
        User.objects.filter(pk=request.user.id).update(last_name=last_name)
        Profile.objects.filter(user_id=request.user.id).update(phone=phone)
        Profile.objects.filter(user_id=request.user.id).update(mobile=mobile)
        messages.add_message(request, messages.INFO, 'Perfil Editado con éxito') 
    profile = Profile.objects.get(user_id = request.user.id)
    template_name = 'registration/profile_edit.html'
    return render(request,template_name,{'profile':profile})


#Funcion nueva pata eliminar sesion activa y redirige automaticamente al forms de iniciar sesion
from django.contrib.auth import logout


def _admin_gate(request):
    """Devuelve el perfil del usuario si pertenece al grupo administrador (id=1)."""
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.info(request, 'Hubo un error con tu perfil.')
        return None, redirect('login')

    if profile.group_id != 1:
        return None, redirect('logout')

    return profile, None


@login_required
def user_list(request):
    _, response = _admin_gate(request)
    if response:
        return response

    users = User.objects.select_related('profile__group').order_by('username')
    user_entries = []
    for user in users:
        try:
            profile = user.profile
        except Profile.DoesNotExist:  # pragma: no cover - señal debería crearlo
            profile = None
        if profile:
            try:
                group_name = profile.group.name
            except ObjectDoesNotExist:
                group_name = '-'
        else:
            group_name = '-'
        user_entries.append({'user': user, 'group_name': group_name})
    return render(request, 'registration/user_list.html', {'users': user_entries})


@login_required
def user_create(request):
    _, response = _admin_gate(request)
    if response:
        return response

    if request.method == 'POST':
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('user_list')
        messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = AdminUserCreateForm()
    return render(request, 'registration/user_form.html', {'form': form, 'title': 'Crear usuario'})


@login_required
def user_edit(request, pk):
    _, response = _admin_gate(request)
    if response:
        return response

    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('user_list')
        messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = AdminUserUpdateForm(instance=user)
    return render(request, 'registration/user_form.html', {'form': form, 'title': 'Editar usuario'})


@login_required
def user_toggle_active(request, pk):
    _, response = _admin_gate(request)
    if response:
        return response

    if request.method != 'POST':
        return redirect('user_list')

    user = get_object_or_404(User, pk=pk)
    if user.pk == request.user.pk:
        messages.warning(request, 'No puedes bloquear tu propio usuario.')
        return redirect('user_list')

    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    estado = 'activado' if user.is_active else 'bloqueado'
    messages.success(request, f'Usuario {estado} correctamente.')
    return redirect('user_list')


@login_required
def user_delete(request, pk):
    _, response = _admin_gate(request)
    if response:
        return response

    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if user.pk == request.user.pk:
            messages.warning(request, 'No puedes eliminar tu propio usuario.')
            return redirect('user_list')
        user.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
        return redirect('user_list')

    return render(request, 'registration/user_confirm_delete.html', {'user_obj': user})

def logout_view(request):
    logout(request)
    # Para mostrar el template de confirmacion de cerrar sesion
    return render(request, 'registration/logout.html')
