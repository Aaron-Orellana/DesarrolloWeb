from __future__ import annotations

from typing import Iterable, Optional, Set

from django import forms
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q

from registration.models import Profile
from registration.utils import DEFAULT_GROUP_NAME, ROLE_GROUP_NAMES

from .models import (
    Cuadrilla,
    CuadrillaMembership,
    Departamento,
    DepartamentoMembership,
    Direccion,
    DireccionMembership,
    Territorial,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ordered_profiles_queryset():
    return Profile.objects.select_related("user").order_by(
        "user__first_name",
        "user__last_name",
        "user__username",
    )


def _role_group(role_key: str) -> Group:
    group_name = ROLE_GROUP_NAMES.get(role_key, DEFAULT_GROUP_NAME)
    group, _ = Group.objects.get_or_create(name=group_name)
    return group


def _assign_role(profile: Profile, role_key: str, object_id: int) -> None:
    group = _role_group(role_key)
    profile.role_type = role_key
    profile.role_object_id = object_id
    profile.group = group
    profile.save(update_fields=["role_type", "role_object_id", "group"])
    profile.user.groups.set([group])


def _clear_role(profile: Profile) -> None:
    default_group, _ = Group.objects.get_or_create(name=DEFAULT_GROUP_NAME)
    profile.role_type = None
    profile.role_object_id = None
    profile.group = default_group
    profile.save(update_fields=["role_type", "role_object_id", "group"])
    profile.user.groups.set([default_group])


def _format_profiles(profiles: Iterable[Profile]) -> str:
    names = []
    for profile in profiles:
        user = profile.user
        full_name = user.get_full_name().strip()
        names.append(full_name or user.username)
    return ", ".join(names)


def _holds_current_role(profile: Profile, role_key: str, instance_pk: Optional[int]) -> bool:
    return (
        profile.role_type == role_key
        and instance_pk is not None
        and profile.role_object_id == instance_pk
    )


# ---------------------------------------------------------------------------
# Base form -> evitar duplicidad de usuarios
# ---------------------------------------------------------------------------

class BaseRoleMembershipForm(forms.ModelForm):
    role_key: str = ""
    membership_model = None
    membership_fk_name: str = ""

    miembros = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.none(),
        required=False,
        label="Miembros",
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 10}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = self._available_profiles_queryset()

        self.fields["miembros"].queryset = queryset
        self._current_member_ids = self._load_current_member_ids()
        if self._current_member_ids:
            self.fields["miembros"].initial = list(self._current_member_ids)

        if "encargados" in self.fields:
            self.fields["encargados"].queryset = queryset
            self.fields["encargados"].initial = self._load_encargados_ids()

    # ------------------------------------------------------------------ utils

    def _load_current_member_ids(self) -> Set[int]:
        if not getattr(self.instance, "pk", None):
            return set()
        return set(
            self.membership_model.objects.filter(
                **{self.membership_fk_name: self.instance}
            ).values_list("usuario_id_id", flat=True)
        )

    def _load_encargados_ids(self) -> Set[int]:
        if (
            not hasattr(self.membership_model, "es_encargado")
            or not getattr(self.instance, "pk", None)
        ):
            return set()
        return set(
            self.membership_model.objects.filter(
                **{self.membership_fk_name: self.instance},
                es_encargado=True,
            ).values_list("usuario_id_id", flat=True)
        )

    def _available_profiles_queryset(self):
        filters = Q(role_type__isnull=True)
        if getattr(self.instance, "pk", None):
            filters |= Q(
                role_type=self.role_key,
                role_object_id=self.instance.pk,
            )
        return _ordered_profiles_queryset().filter(filters).distinct()

    # ----------------------------------------------------------------- clean

    def clean(self):
        cleaned_data = super().clean()
        miembros = cleaned_data.get("miembros") or []
        instance_pk = getattr(self.instance, "pk", None)

        conflicts = [
            profile for profile in miembros
            if profile.role_type
            and not _holds_current_role(profile, self.role_key, instance_pk)
        ]
        if conflicts:
            self.add_error(
                "miembros",
                f"Ya están asignados a otro rol: {_format_profiles(conflicts)}.",
            )

        return cleaned_data

    # ----------------------------------------------------------------- persist

    def _sync_memberships(
        self,
        instance,
        miembros: Iterable[Profile],
        encargados_ids: Optional[Set[int]] = None,
    ) -> None:
        selected_profiles = list(miembros)
        selected_ids = {profile.pk for profile in selected_profiles}

        existing_qs = self.membership_model.objects.filter(
            **{self.membership_fk_name: instance}
        )
        existing = {
            membership.usuario_id_id: membership
            for membership in existing_qs
        }

        # Remove non-selected members
        for pk, membership in list(existing.items()):
            if pk in selected_ids:
                continue
            profile = membership.usuario_id
            membership.delete()
            if _holds_current_role(profile, self.role_key, instance.pk):
                _clear_role(profile)

        # Add or update selected members
        for profile in selected_profiles:
            membership = existing.get(profile.pk)
            es_encargado = (
                profile.pk in encargados_ids if encargados_ids is not None else None
            )

            if membership is None:
                fields = {self.membership_fk_name: instance, "usuario_id": profile}
                if hasattr(self.membership_model, "es_encargado") and es_encargado is not None:
                    fields["es_encargado"] = es_encargado
                membership = self.membership_model.objects.create(**fields)
            elif (
                hasattr(membership, "es_encargado")
                and es_encargado is not None
                and membership.es_encargado != es_encargado
            ):
                membership.es_encargado = es_encargado
                membership.save(update_fields=["es_encargado"])

            _assign_role(profile, self.role_key, instance.pk)

    @transaction.atomic
    def save(self, commit: bool = True):
        instance = super().save(commit=True)
        miembros = list(self.cleaned_data.get("miembros") or [])

        encargados_ids: Optional[Set[int]] = None
        if "encargados" in self.cleaned_data:
            encargados_ids = {
                profile.pk for profile in (self.cleaned_data.get("encargados") or [])
            }

        self._sync_memberships(instance, miembros, encargados_ids)
        return instance


# ---------------------------------------------------------------------------
# Concrete forms
# ---------------------------------------------------------------------------

class DireccionForm(BaseRoleMembershipForm):
    role_key = "direccion"
    membership_model = DireccionMembership
    membership_fk_name = "direccion"

    encargados = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.none(),
        required=False,
        label="Encargados",
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 6}),
        help_text="Selecciona cuáles de los miembros son encargados.",
    )

    class Meta:
        model = Direccion
        fields = ["nombre", "estado", "miembros", "encargados"]
        labels = {
            "nombre": "Nombre",
            "estado": "Activa",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ingrese el nombre de la dirección",
            }),
            "estado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        miembros = set(cleaned_data.get("miembros") or [])
        encargados = set(cleaned_data.get("encargados") or [])
        if encargados and not encargados.issubset(miembros):
            self.add_error(
                "encargados",
                "Los encargados deben formar parte del listado de miembros seleccionados.",
            )
        return cleaned_data


class DepartamentoForm(BaseRoleMembershipForm):
    role_key = "departamento"
    membership_model = DepartamentoMembership
    membership_fk_name = "departamento"

    encargados = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.none(),
        required=False,
        label="Encargados",
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 6}),
        help_text="Encargados dentro de los miembros seleccionados.",
    )

    class Meta:
        model = Departamento
        fields = ["nombre", "estado", "direccion", "miembros", "encargados"]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ingrese el nombre del departamento",
            }),
            "direccion": forms.Select(attrs={"class": "form-select"}),
            "estado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "nombre": "Nombre",
            "direccion": "Dirección",
            "estado": "Activo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["direccion"].queryset = Direccion.objects.filter(estado=True)

    def clean(self):
        cleaned_data = super().clean()
        miembros = set(cleaned_data.get("miembros") or [])
        encargados = set(cleaned_data.get("encargados") or [])
        if encargados and not encargados.issubset(miembros):
            self.add_error(
                "encargados",
                "Los encargados deben formar parte del listado de miembros seleccionados.",
            )
        return cleaned_data


class CuadrillaForm(BaseRoleMembershipForm):
    role_key = "cuadrilla"
    membership_model = CuadrillaMembership
    membership_fk_name = "cuadrilla"

    class Meta:
        model = Cuadrilla
        fields = ["nombre", "estado", "departamento", "miembros"]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ingrese el nombre de la cuadrilla",
            }),
            "departamento": forms.Select(attrs={"class": "form-select"}),
            "estado": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "nombre": "Nombre",
            "departamento": "Departamento",
            "estado": "Activa",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["departamento"].queryset = Departamento.objects.filter(estado=True)


class TerritorialForm(forms.ModelForm):
    profile = forms.ModelChoiceField(
        queryset=Profile.objects.none(),
        required=False,
        label="Responsable",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Territorial
        fields = ["nombre", "profile"]
        labels = {
            "nombre": "Nombre",
            "profile": "Responsable",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ingrese el nombre del territorial",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["profile"].queryset = self._available_profiles_queryset()
        if getattr(self.instance, "profile_id", None):
            self.fields["profile"].initial = self.instance.profile_id

    def _available_profiles_queryset(self):
        filters = Q(role_type__isnull=True)
        if getattr(self.instance, "pk", None):
            filters |= Q(
                role_type="territorial",
                role_object_id=self.instance.pk,
            )
        return _ordered_profiles_queryset().filter(filters).distinct()

    def clean_profile(self):
        profile = self.cleaned_data.get("profile")
        if not profile:
            return profile
        if profile.role_type and not _holds_current_role(profile, "territorial", getattr(self.instance, "pk", None)):
            raise forms.ValidationError(
                "El usuario seleccionado ya está asignado a otro rol."
            )
        return profile

    @transaction.atomic
    def save(self, commit: bool = True):
        territorial = super().save(commit=False)
        previous_profile_id = None
        if getattr(territorial, "pk", None):
            previous_profile_id = Territorial.objects.filter(pk=territorial.pk).values_list("profile_id", flat=True).first()

        territorial.save()

        new_profile = self.cleaned_data.get("profile")
        if previous_profile_id and (not new_profile or previous_profile_id != new_profile.pk):
            previous_profile = Profile.objects.filter(pk=previous_profile_id).first()
            if previous_profile and _holds_current_role(previous_profile, "territorial", territorial.pk):
                _clear_role(previous_profile)

        if new_profile:
            _assign_role(new_profile, "territorial", territorial.pk)
            territorial.profile = new_profile
        else:
            territorial.profile = None

        if commit:
            territorial.save(update_fields=["nombre", "profile"])
        else:
            territorial.save()

        return territorial
