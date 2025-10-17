from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Profile

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
    group = forms.ModelChoiceField(queryset=Group.objects.order_by('name'), label="Grupo")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")
    phone = forms.CharField(required=False, label="Teléfono fijo", max_length=30)
    mobile = forms.CharField(required=False, label="Teléfono móvil", max_length=30)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.fields['group'].initial:
            default_group = Group.objects.filter(pk=1).first()
            if default_group:
                self.fields['group'].initial = default_group.pk

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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.group = self.cleaned_data['group']
            profile.phone = self.cleaned_data.get('phone', '')
            profile.mobile = self.cleaned_data.get('mobile', '')
            profile.save()
        return user

class AdminUserUpdateForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.order_by('name'), label="Grupo")
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
        if profile:
            self.fields['group'].initial = profile.group_id
            self.fields['phone'].initial = profile.phone
            self.fields['mobile'].initial = profile.mobile

    def clean_email(self):
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Correo existe, prueba con otro")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.group = self.cleaned_data['group']
            profile.phone = self.cleaned_data.get('phone', '')
            profile.mobile = self.cleaned_data.get('mobile', '')
            profile.save()
        return user
