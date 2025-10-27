"""
Utilities for managing profile roles that map to organizational entities.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple, Type

from django.contrib.auth.models import Group
from django.db import models, transaction
from django.db.models import Q

from orgs.models import (
    Cuadrilla,
    CuadrillaMembership,
    Departamento,
    DepartamentoMembership,
    Direccion,
    DireccionMembership,
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

MembershipConfig = Tuple[Type[models.Model], str, bool]

MEMBERSHIP_CONFIG: dict[str, MembershipConfig] = {
    "direccion": (DireccionMembership, "direccion", True),
    "departamento": (DepartamentoMembership, "departamento", True),
    "cuadrilla": (CuadrillaMembership, "cuadrilla", False),
}


def _default_group() -> Group:
    group, _ = Group.objects.get_or_create(name=DEFAULT_GROUP_NAME)
    return group


def build_role_choices(current_profile: Optional[Profile] = None) -> List[Tuple[str, str]]:
    """
    Return a list of role choices in the format expected by Django's ChoiceField.
    Roles con estado inactivo quedan excluidos automáticamente.
    """
    choices: List[Tuple[str, str]] = []
    for config in ROLE_CONFIG:
        queryset = config.model.objects.all()

        # Mostrar únicamente los objetos disponibles cuando hay columna profile.
        if hasattr(config.model, "profile"):
            queryset = queryset.filter(
                Q(profile__isnull=True) | Q(profile=current_profile)
            )

        if hasattr(config.model, "estado"):
            queryset = queryset.filter(estado=True)

        order_field = "nombre" if hasattr(config.model, "nombre") else "pk"
        queryset = queryset.order_by(order_field)

        for obj in queryset:
            nombre = getattr(obj, "nombre", str(obj))
            choices.append((f"{config.key}:{obj.pk}", f"{config.label}: {nombre}"))
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
    """
    Limpia cualquier referencia (profile FK o memberships) para permitir reasignar el rol.
    """
    for config in ROLE_CONFIG:
        if hasattr(config.model, "profile"):
            config.model.objects.filter(profile=profile).update(profile=None)

    DireccionMembership.objects.filter(usuario_id=profile).delete()
    DepartamentoMembership.objects.filter(usuario_id=profile).delete()
    CuadrillaMembership.objects.filter(usuario_id=profile).delete()

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

    membership_spec = MEMBERSHIP_CONFIG.get(role_key)
    if membership_spec:
        membership_model, fk_name, mark_encargado = membership_spec
        membership_kwargs = {
            fk_name: target,
            "usuario_id": profile,
        }
        membership, _ = membership_model.objects.get_or_create(**membership_kwargs)
        if mark_encargado and getattr(membership, "es_encargado", False) is False:
            membership.es_encargado = True
            membership.save(update_fields=["es_encargado"])
    else:
        # Modelos que siguen utilizando un FK directo al perfil (Secpla, Territorial, etc.)
        previous_profile = getattr(target, "profile", None)
        if previous_profile and previous_profile != profile:
            _reset_profile_role(previous_profile)
            default_group = _default_group()
            previous_profile.group = default_group
            previous_profile.save(update_fields=["role_type", "role_object_id", "group"])
            previous_profile.user.groups.set([default_group])

        target.profile = profile
        target.save(update_fields=["profile"])

    profile.role_type = role_key
    profile.role_object_id = target.pk
    group_name = ROLE_GROUP_NAMES.get(role_key, DEFAULT_GROUP_NAME)
    group, _ = Group.objects.get_or_create(name=group_name)
    profile.group = group
    profile.save(update_fields=["role_type", "role_object_id", "group"])
    profile.user.groups.set([group])


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
    default_group = _default_group()
    profile.group = default_group
    profile.save(update_fields=['role_type', 'role_object_id', 'group'])
    profile.user.groups.set([default_group])
