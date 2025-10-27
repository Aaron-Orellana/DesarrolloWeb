from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from .utils import assign_role_to_profile, build_role_choices, parse_role_value

class UserCreationFormWithEmail(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Requerido, 254 caracteres como máximo y debe ser válido")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Correo existe, prueba con otro")
        return email

class EmailForm(forms.ModelForm):
    email = forms.EmailField(required=True, help_text="Requerido, 254 caracteres como máximo y debe ser válido")

    class Meta:
        model = User
        fields = ['email']        

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if 'email' in self.changed_data:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Correo existe, prueba con otro")
        return email

class AdminUserCreateForm(forms.ModelForm):
    role = forms.ChoiceField(label="Rol", required=False, choices=())
    password1 = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")
    phone = forms.CharField(required=False, label="Teléfono fijo", max_length=30)
    mobile = forms.CharField(required=False, label="Teléfono móvil", max_length=30)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_role_field()

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Correo existe, prueba con otro")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def clean_role(self):
        value = self.cleaned_data.get("role")
        if not value:
            raise forms.ValidationError("Selecciona un rol")
        try:
            parse_role_value(value)
        except ValueError:
            raise forms.ValidationError("Rol inválido")
        return value

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data.get('phone', '')
            profile.mobile = self.cleaned_data.get('mobile', '')
            profile.save()
            role_key, object_id = parse_role_value(self.cleaned_data['role'])
            assign_role_to_profile(profile, role_key, object_id)
        return user

    def _init_role_field(self, profile=None):
        choices = build_role_choices(profile)
        if choices:
            self.fields['role'].choices = [('', 'Seleccione un rol')] + choices
        else:
            self.fields['role'].choices = [('', 'No hay roles disponibles')]
            self.fields['role'].disabled = True


class AdminUserUpdateForm(forms.ModelForm):
    role = forms.ChoiceField(label="Rol", required=True, choices=())
    phone = forms.CharField(required=False, label="Teléfono fijo", max_length=30)
    mobile = forms.CharField(required=False, label="Teléfono móvil", max_length=30)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            profile = self.instance.profile
        except Profile.DoesNotExist:
            profile = None
        self._init_role_field(profile)
        if profile:
            self.fields['phone'].initial = profile.phone
            self.fields['mobile'].initial = profile.mobile

    def clean_email(self):
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Correo existe, prueba con otro")
        return email

    def clean_role(self):
        value = self.cleaned_data.get("role")
        if not value:
            raise forms.ValidationError("Selecciona un rol")
        try:
            parse_role_value(value)
        except ValueError:
            raise forms.ValidationError("Rol inválido")
        return value

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data.get('phone', '')
            profile.mobile = self.cleaned_data.get('mobile', '')
            profile.save()
            role_key, object_id = parse_role_value(self.cleaned_data['role'])
            assign_role_to_profile(profile, role_key, object_id)
        return user

    def _init_role_field(self, profile=None):
        choices = build_role_choices(profile)
        if choices:
            self.fields['role'].choices = [('', 'Seleccione un rol')] + choices
        else:
            self.fields['role'].choices = [('', 'No hay roles disponibles')]
            self.fields['role'].disabled = True
        if profile and profile.role_type and profile.role_object_id:
            self.fields['role'].initial = f"{profile.role_type}:{profile.role_object_id}"
