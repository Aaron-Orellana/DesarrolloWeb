from django import forms
from django.db import transaction
from registration.models import Profile

from .models import (
    CuadrillaMembership,
    Departamento,
    DepartamentoMembership,
    Direccion,
    DireccionMembership,
    Secpla,
    Territorial,
)


def _ordered_profiles_queryset():
    """
    Perfila la lista de usuarios disponibles ordenada por nombre completo / username.
    """
    return Profile.objects.select_related('user').order_by(
        'user__first_name',
        'user__last_name',
        'user__username',
    )


def _blocked_profile_ids(
    *,
    exclude_direccion: Direccion | None = None,
    exclude_departamento: Departamento | None = None,
    exclude_cuadrilla=None,
    exclude_secpla=None,
    exclude_territorial=None,
):
    blocked: set[int] = set()

    direcciones_qs = DireccionMembership.objects.all()
    if exclude_direccion:
        direcciones_qs = direcciones_qs.exclude(direccion=exclude_direccion)
    blocked.update(direcciones_qs.values_list('usuario_id_id', flat=True))

    departamentos_qs = DepartamentoMembership.objects.all()
    if exclude_departamento:
        departamentos_qs = departamentos_qs.exclude(departamento=exclude_departamento)
    blocked.update(departamentos_qs.values_list('usuario_id_id', flat=True))

    cuadrillas_qs = CuadrillaMembership.objects.all()
    if exclude_cuadrilla:
        cuadrillas_qs = cuadrillas_qs.exclude(cuadrilla=exclude_cuadrilla)
    blocked.update(cuadrillas_qs.values_list('usuario_id_id', flat=True))

    secpla_qs = Secpla.objects.filter(profile__isnull=False)
    if exclude_secpla:
        secpla_qs = secpla_qs.exclude(pk=getattr(exclude_secpla, 'pk', exclude_secpla))
    blocked.update(secpla_qs.values_list('profile_id', flat=True))

    territorial_qs = Territorial.objects.filter(profile__isnull=False)
    if exclude_territorial:
        territorial_qs = territorial_qs.exclude(pk=getattr(exclude_territorial, 'pk', exclude_territorial))
    blocked.update(territorial_qs.values_list('profile_id', flat=True))

    return blocked


def _available_profiles_for_direccion(instance: Direccion | None):
    qs = _ordered_profiles_queryset()
    blocked_ids = _blocked_profile_ids(exclude_direccion=instance)
    if blocked_ids:
        qs = qs.exclude(pk__in=blocked_ids)
    return qs


def _available_profiles_for_departamento(instance: Departamento | None):
    qs = _ordered_profiles_queryset()
    blocked_ids = _blocked_profile_ids(exclude_departamento=instance)
    if blocked_ids:
        qs = qs.exclude(pk__in=blocked_ids)
    return qs


class DireccionForm(forms.ModelForm):
    miembros = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.none(),
        required=False,
        label='Miembros',
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 10}),
        help_text='Usuarios que pertenecen a la dirección.',
    )
    encargados = forms.ModelChoiceField(
        queryset=Profile.objects.none(),
        required=False,
        label='Encargados',
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Selecciona que miembro es encargado.',
    )

    class Meta:
        model = Direccion
        fields = ['nombre', 'estado', 'miembros', 'encargados']
        labels = {
            'nombre': 'Nombre',
            'estado': 'Activa',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la dirección'
            }),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        perfiles_qs = _available_profiles_for_direccion(self.instance)
        self.fields['miembros'].queryset = perfiles_qs
        self.fields['encargados'].queryset = perfiles_qs

        if self.instance.pk:
            memberships = list(
                self.instance.memberships.select_related('usuario_id__user')
            )
            miembros_ids = [m.usuario_id_id for m in memberships]
            encargados_ids = [m.usuario_id_id for m in memberships if m.es_encargado]
            self.fields['miembros'].initial = miembros_ids
            self.fields['encargados'].initial = encargados_ids

    def clean(self):
        cleaned_data = super().clean()
        miembros = set(cleaned_data.get('miembros') or [])
        encargados = set(cleaned_data.get('encargados') or [])
        if encargados and not encargados.issubset(miembros):
            self.add_error(
                'encargados',
                'Los encargados deben formar parte del listado de miembros seleccionados.'
            )

        if miembros:
            conflicts = DireccionMembership.objects.filter(usuario_id__in=miembros)
            if self.instance.pk:
                conflicts = conflicts.exclude(direccion=self.instance)
            conflicts = conflicts.select_related('usuario_id__user', 'direccion')
            if conflicts.exists():
                conflict_names = ", ".join(
                    membership.usuario_id.user.get_full_name() or membership.usuario_id.user.username
                    for membership in conflicts
                )
                self.add_error(
                    'miembros',
                    f'Los siguientes usuarios ya pertenecen a otra dirección: {conflict_names}.'
                )
            departamentos_conflict = DepartamentoMembership.objects.filter(
                usuario_id__in=miembros
            ).select_related('usuario_id__user', 'departamento')
            if departamentos_conflict.exists():
                conflict_names = ", ".join(
                    membership.usuario_id.user.get_full_name() or membership.usuario_id.user.username
                    for membership in departamentos_conflict
                )
                self.add_error(
                    'miembros',
                    f'Estos usuarios ya pertenecen a un departamento y no pueden estar en una dirección: {conflict_names}.'
                )
            cuadrillas_conflict = CuadrillaMembership.objects.filter(
                usuario_id__in=miembros
            ).select_related('usuario_id__user', 'cuadrilla')
            if cuadrillas_conflict.exists():
                conflict_names = ", ".join(
                    membership.usuario_id.user.get_full_name() or membership.usuario_id.user.username
                    for membership in cuadrillas_conflict
                )
                self.add_error(
                    'miembros',
                    f'Estos usuarios ya pertenecen a una cuadrilla: {conflict_names}.'
                )
            secpla_conflict = Secpla.objects.filter(profile_id__in=[profile.pk for profile in miembros]).select_related('profile__user')
            if secpla_conflict.exists():
                conflict_names = ", ".join(
                    secpla.profile.user.get_full_name() or secpla.profile.user.username
                    for secpla in secpla_conflict
                )
                self.add_error(
                    'miembros',
                    f'Estos usuarios ya ejercen como Secpla: {conflict_names}.'
                )
            territorial_conflict = Territorial.objects.filter(profile_id__in=[profile.pk for profile in miembros]).select_related('profile__user')
            if territorial_conflict.exists():
                conflict_names = ", ".join(
                    territorial.profile.user.get_full_name() or territorial.profile.user.username
                    for territorial in territorial_conflict
                )
                self.add_error(
                    'miembros',
                    f'Estos usuarios ya ejercen como Territorial: {conflict_names}.'
                )
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        direccion = super().save(commit=commit)
        if commit:
            self._sync_memberships(direccion)
        return direccion

    def _sync_memberships(self, direccion: Direccion) -> None:
        miembros = list(self.cleaned_data.get('miembros') or [])
        encargados = {profile.pk for profile in (self.cleaned_data.get('encargados') or [])}
        existing = {
            membership.usuario_id_id: membership
            for membership in direccion.memberships.all()
        }

        selected_ids = {profile.pk for profile in miembros}
        # Eliminar usuarios que ya no pertenecen.
        to_delete = [pk for pk in existing.keys() if pk not in selected_ids]
        if to_delete:
            direccion.memberships.filter(usuario_id_id__in=to_delete).delete()

        for profile in miembros:
            membership = existing.get(profile.pk)
            es_encargado = profile.pk in encargados
            if membership is None:
                DireccionMembership.objects.create(
                    direccion=direccion,
                    usuario_id=profile,
                    es_encargado=es_encargado,
                )
            elif membership.es_encargado != es_encargado:
                membership.es_encargado = es_encargado
                membership.save(update_fields=['es_encargado'])


class DepartamentoForm(forms.ModelForm):
    miembros = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.none(),
        required=False,
        label='Miembros',
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 10}),
        help_text='Usuarios asociados al departamento.',
    )
    encargados = forms.ModelChoiceField(
        queryset=Profile.objects.none(),
        required=False,
        label='Encargados',
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Selecciona que miembro es encargado.',
    )

    class Meta:
        model = Departamento
        fields = ['nombre', 'estado', 'direccion', 'miembros', 'encargados']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del departamento'
            }),
            'direccion': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre',
            'direccion': 'Dirección',
            'estado': 'Activo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['direccion'].queryset = Direccion.objects.filter(estado=True)
        perfiles_qs = _ordered_profiles_queryset()
        perfiles_qs = _available_profiles_for_departamento(self.instance)
        self.fields['miembros'].queryset = perfiles_qs
        self.fields['encargados'].queryset = perfiles_qs

        if self.instance.pk:
            memberships = list(
                self.instance.memberships.select_related('usuario_id__user')
            )
            miembros_ids = [m.usuario_id_id for m in memberships]
            encargados_ids = [m.usuario_id_id for m in memberships if m.es_encargado]
            self.fields['miembros'].initial = miembros_ids
            self.fields['encargados'].initial = encargados_ids

    def clean(self):
        cleaned_data = super().clean()
        miembros = set(cleaned_data.get('miembros') or [])
        encargados = set(cleaned_data.get('encargados') or [])
        if encargados and not encargados.issubset(miembros):
            self.add_error(
                'encargados',
                'Los encargados deben formar parte del listado de miembros seleccionados.'
            )
        if miembros:
            conflicts = DepartamentoMembership.objects.filter(usuario_id__in=miembros)
            if self.instance.pk:
                conflicts = conflicts.exclude(departamento=self.instance)
            conflicts = conflicts.select_related('usuario_id__user', 'departamento')
            if conflicts.exists():
                conflict_names = ", ".join(
                    membership.usuario_id.user.get_full_name() or membership.usuario_id.user.username
                    for membership in conflicts
                )
                self.add_error(
                    'miembros',
                    f'Ya son parte de otro departamento: {conflict_names}.'
                )
            direcciones_conflict = DireccionMembership.objects.filter(
                usuario_id__in=miembros
            ).select_related('usuario_id__user', 'direccion')
            if direcciones_conflict.exists():
                conflict_names = ", ".join(
                    membership.usuario_id.user.get_full_name() or membership.usuario_id.user.username
                    for membership in direcciones_conflict
                )
                self.add_error(
                    'miembros',
                    f'Estos usuarios ya pertenecen a una dirección y no pueden estar en un departamento: {conflict_names}.'
                )
            cuadrillas_conflict = CuadrillaMembership.objects.filter(
                usuario_id__in=miembros
            ).select_related('usuario_id__user', 'cuadrilla')
            if cuadrillas_conflict.exists():
                conflict_names = ", ".join(
                    membership.usuario_id.user.get_full_name() or membership.usuario_id.user.username
                    for membership in cuadrillas_conflict
                )
                self.add_error(
                    'miembros',
                    f'Estos usuarios ya pertenecen a una cuadrilla: {conflict_names}.'
                )
            secpla_conflict = Secpla.objects.filter(profile_id__in=[profile.pk for profile in miembros]).select_related('profile__user')
            if secpla_conflict.exists():
                conflict_names = ", ".join(
                    secpla.profile.user.get_full_name() or secpla.profile.user.username
                    for secpla in secpla_conflict
                )
                self.add_error(
                    'miembros',
                    f'Estos usuarios ya ejercen como Secpla: {conflict_names}.'
                )
            territorial_conflict = Territorial.objects.filter(profile_id__in=[profile.pk for profile in miembros]).select_related('profile__user')
            if territorial_conflict.exists():
                conflict_names = ", ".join(
                    territorial.profile.user.get_full_name() or territorial.profile.user.username
                    for territorial in territorial_conflict
                )
                self.add_error(
                    'miembros',
                    f'Estos usuarios ya ejercen como Territorial: {conflict_names}.'
                )
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        departamento = super().save(commit=commit)
        if commit:
            self._sync_memberships(departamento)
        return departamento

    def _sync_memberships(self, departamento: Departamento) -> None:
        miembros = list(self.cleaned_data.get('miembros') or [])
        encargados = {profile.pk for profile in (self.cleaned_data.get('encargados') or [])}
        existing = {
            membership.usuario_id_id: membership
            for membership in departamento.memberships.all()
        }

        selected_ids = {profile.pk for profile in miembros}
        to_delete = [pk for pk in existing.keys() if pk not in selected_ids]
        if to_delete:
            departamento.memberships.filter(usuario_id_id__in=to_delete).delete()

        for profile in miembros:
            membership = existing.get(profile.pk)
            es_encargado = profile.pk in encargados
            if membership is None:
                DepartamentoMembership.objects.create(
                    departamento=departamento,
                    usuario_id=profile,
                    es_encargado=es_encargado,
                )
            elif membership.es_encargado != es_encargado:
                membership.es_encargado = es_encargado
                membership.save(update_fields=['es_encargado'])
