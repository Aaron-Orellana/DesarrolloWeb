"""
Utilities for managing profile roles that map to organizational entities.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from django.contrib.auth.models import Group
from django.db import transaction

from orgs.models import (
    Cuadrilla,
    Departamento,
    Direccion,
    Secpla,
    Territorial,
)
from .models import Profile


@dataclass(frozen=True)
class RoleConfig:
    key: str
    model: type
    label: str


ROLE_CONFIG: Tuple[RoleConfig, ...] = (
    RoleConfig("secpla", Secpla, "Secpla"),
    RoleConfig("direccion", Direccion, "Dirección"),
    RoleConfig("departamento", Departamento, "Departamento"),
    RoleConfig("cuadrilla", Cuadrilla, "Cuadrilla"),
    RoleConfig("territorial", Territorial, "Territorial"),
)

ROLE_GROUP_NAMES = {
    "secpla": "Administradores",
    "direccion": "Direcciones",
    "departamento": "Departamentos",
    "cuadrilla": "Cuadrillas",
    "territorial": "Territoriales",
}

DEFAULT_GROUP_NAME = "Usuarios"


def _default_group() -> Group:
    group, _ = Group.objects.get_or_create(name=DEFAULT_GROUP_NAME)
    return group


def build_role_choices(current_profile: Optional[Profile] = None) -> List[Tuple[str, str]]:
    """
    Return a list of role choices in the format expected by Django's ChoiceField.
    Only roles that are currently libres or asignados al `current_profile` are included.
    """
    choices: List[Tuple[str, str]] = []
    for config in ROLE_CONFIG:
        queryset = config.model.objects.select_related("profile").order_by("nombre")
        for obj in queryset:
            assigned_profile = getattr(obj, "profile", None)
            if assigned_profile and assigned_profile != current_profile:
                continue
            choices.append((f"{config.key}:{obj.pk}", f"{config.label}: {obj.nombre}"))
    return choices


def get_role_display(profile: Optional[Profile]) -> str:
    """
    Human readable representation of the current role for display purposes.
    """
    if not profile or not profile.role_type or not profile.role_object_id:
        return "-"
    for config in ROLE_CONFIG:
        if config.key != profile.role_type:
            continue
        obj = config.model.objects.filter(pk=profile.role_object_id).only("nombre").first()
        if obj:
            return f"{config.label}: {obj.nombre}"
    return profile.get_role_type_display() or "-"


def _get_role_config(role_key: str) -> RoleConfig:
    for config in ROLE_CONFIG:
        if config.key == role_key:
            return config
    raise ValueError(f"Rol desconocido: {role_key}")


def _reset_profile_role(profile: Profile) -> None:
    for config in ROLE_CONFIG:
        config.model.objects.filter(profile=profile).update(profile=None)
    profile.role_type = None
    profile.role_object_id = None


@transaction.atomic
def assign_role_to_profile(profile: Profile, role_key: str, object_id: int) -> None:
    """
    Asociate `profile` with the ORGS object identified by `role_key`/`object_id`.
    It also sincroniza el campo group del perfil según la tabla de mappeo.
    """
    config = _get_role_config(role_key)
    target = config.model.objects.select_for_update().get(pk=object_id)

    # Liberar cualquier rol previo vinculado al perfil.
    _reset_profile_role(profile)

    # Si otro perfil estaba asignado a este mismo objeto, lo limpiamos.
    previous_profile = getattr(target, "profile", None)
    if previous_profile and previous_profile != profile:
        _reset_profile_role(previous_profile)
        previous_profile.group = _default_group()
        previous_profile.save(update_fields=["role_type", "role_object_id", "group"])

    target.profile = profile
    target.save(update_fields=["profile"])

    profile.role_type = role_key
    profile.role_object_id = target.pk
    group_name = ROLE_GROUP_NAMES.get(role_key, DEFAULT_GROUP_NAME)
    group, _ = Group.objects.get_or_create(name=group_name)
    profile.group = group
    profile.save()


def parse_role_value(raw_value: str) -> Tuple[str, int]:
    """
    Convert the value recibido desde el ChoiceField en (role_key, object_id).
    """
    try:
        role_key, object_id = raw_value.split(":", 1)
        return role_key, int(object_id)
    except (ValueError, AttributeError):
        raise ValueError("Valor de rol inválido")


def has_admin_role(profile: Optional[Profile]) -> bool:
    return bool(profile and profile.role_type == Profile.Role.SECPLA)


def clear_profile_role(profile: Optional[Profile]) -> None:
    if not profile:
        return
    _reset_profile_role(profile)
    profile.group = _default_group()
    profile.save(update_fields=['role_type', 'role_object_id', 'group'])
