from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from registration.models import Profile
from orgs.forms import _assign_role, _clear_role, _format_profiles, _holds_current_role
from orgs.models import (
    Cuadrilla,
    CuadrillaMembership,
    Departamento,
    DepartamentoMembership,
    Direccion,
    DireccionMembership,
    Territorial,
)


# ---------------------------------------------------------------------------
# Shared serializers
# ---------------------------------------------------------------------------


class ProfileSummarySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["id", "username", "first_name", "last_name", "full_name", "role_type"]

    def get_full_name(self, obj: Profile) -> str:
        return obj.user.get_full_name().strip()


class BaseMembershipSerializer(serializers.ModelSerializer):
    usuario = ProfileSummarySerializer(source="usuario_id", read_only=True)
    usuario_id = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.select_related("user"),
        write_only=True,
    )


class DireccionMembershipSerializer(BaseMembershipSerializer):
    class Meta:
        model = DireccionMembership
        fields = [
            "direccion_membership_id",
            "usuario",
            "usuario_id",
            "es_encargado",
            "desde",
        ]
        read_only_fields = ["direccion_membership_id", "desde"]


class DepartamentoMembershipSerializer(BaseMembershipSerializer):
    class Meta:
        model = DepartamentoMembership
        fields = [
            "departamento_membership_id",
            "usuario",
            "usuario_id",
            "es_encargado",
            "desde",
        ]
        read_only_fields = ["departamento_membership_id", "desde"]


class CuadrillaMembershipSerializer(BaseMembershipSerializer):
    class Meta:
        model = CuadrillaMembership
        fields = [
            "cuadrilla_membership_id",
            "usuario",
            "usuario_id",
            "desde",
        ]
        read_only_fields = ["cuadrilla_membership_id", "desde"]


class DireccionSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = ["direccion_id", "nombre", "estado"]


class DepartamentoSummarySerializer(serializers.ModelSerializer):
    direccion = DireccionSummarySerializer(read_only=True)

    class Meta:
        model = Departamento
        fields = ["departamento_id", "nombre", "estado", "direccion"]


# ---------------------------------------------------------------------------
# Mixins
# ---------------------------------------------------------------------------


class MembershipSerializerMixin:
    """
    Mixin reutilizable para sincronizar miembros asociados a una entidad.
    """

    membership_model = None
    role_key = ""
    membership_foreign_key = ""

    def validate_memberships(self, value):
        if value is None:
            return value

        seen_profile_ids = set()
        instance_pk = getattr(self.instance, "pk", None)
        conflicts = []

        for member_data in value:
            profile: Profile = member_data["usuario_id"]
            if profile.pk in seen_profile_ids:
                raise serializers.ValidationError(
                    _("No se puede repetir un miembro dentro del listado.")
                )
            seen_profile_ids.add(profile.pk)
            if profile.role_type and not _holds_current_role(profile, self.role_key, instance_pk):
                conflicts.append(profile)

        if conflicts:
            raise serializers.ValidationError(
                _("Ya están asignados a otro rol: %(names)s.") % {
                    "names": _format_profiles(conflicts)
                }
            )
        return value

    def _sync_memberships(self, instance, memberships_data):
        if memberships_data is None:
            return

        existing_memberships = {
            membership.usuario_id_id: membership
            for membership in getattr(instance, "memberships").all()
        }
        selected_profiles = [member["usuario_id"] for member in memberships_data]
        selected_ids = {profile.pk for profile in selected_profiles}

        has_encargado_flag = hasattr(self.membership_model, "es_encargado")
        encargados_ids = set()
        if has_encargado_flag:
            encargados_ids = {
                member["usuario_id"].pk
                for member in memberships_data
                if member.get("es_encargado")
            }

        # Remove deselected members
        for profile_id, membership in list(existing_memberships.items()):
            if profile_id in selected_ids:
                continue
            profile = membership.usuario_id
            membership.delete()
            if _holds_current_role(profile, self.role_key, instance.pk):
                _clear_role(profile)

        # Add or update selected members
        for profile in selected_profiles:
            membership = existing_memberships.get(profile.pk)
            es_encargado = profile.pk in encargados_ids if has_encargado_flag else None

            if membership is None:
                fields = {
                    self.membership_foreign_key: instance,
                    "usuario_id": profile,
                }
                if has_encargado_flag:
                    fields["es_encargado"] = es_encargado
                membership = self.membership_model.objects.create(**fields)
            elif has_encargado_flag and es_encargado is not None and membership.es_encargado != es_encargado:
                membership.es_encargado = es_encargado
                membership.save(update_fields=["es_encargado"])

            _assign_role(profile, self.role_key, instance.pk)

    def _create_with_memberships(self, validated_data):
        memberships_data = validated_data.pop("memberships", None)
        with transaction.atomic():
            instance = super().create(validated_data)
            self._sync_memberships(instance, memberships_data)
        return instance

    def _update_with_memberships(self, instance, validated_data):
        memberships_data = validated_data.pop("memberships", None)
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if memberships_data is not None:
                self._sync_memberships(instance, memberships_data)
        return instance


# ---------------------------------------------------------------------------
# Serializers principales
# ---------------------------------------------------------------------------


class DireccionSerializer(MembershipSerializerMixin, serializers.ModelSerializer):
    memberships = DireccionMembershipSerializer(many=True, required=False)

    membership_model = DireccionMembership
    membership_foreign_key = "direccion"
    role_key = "direccion"

    class Meta:
        model = Direccion
        fields = ["direccion_id", "nombre", "estado", "memberships"]
        read_only_fields = ["direccion_id"]

    def create(self, validated_data):
        return self._create_with_memberships(validated_data)

    def update(self, instance, validated_data):
        return self._update_with_memberships(instance, validated_data)


class DepartamentoSerializer(MembershipSerializerMixin, serializers.ModelSerializer):
    direccion = serializers.PrimaryKeyRelatedField(
        queryset=Direccion.objects.filter(estado=True)
    )
    direccion_detalle = DireccionSummarySerializer(source="direccion", read_only=True)
    memberships = DepartamentoMembershipSerializer(many=True, required=False)

    membership_model = DepartamentoMembership
    membership_foreign_key = "departamento"
    role_key = "departamento"

    class Meta:
        model = Departamento
        fields = [
            "departamento_id",
            "nombre",
            "estado",
            "direccion",
            "direccion_detalle",
            "memberships",
        ]
        read_only_fields = ["departamento_id"]

    def create(self, validated_data):
        return self._create_with_memberships(validated_data)

    def update(self, instance, validated_data):
        return self._update_with_memberships(instance, validated_data)


class CuadrillaSerializer(MembershipSerializerMixin, serializers.ModelSerializer):
    departamento = serializers.PrimaryKeyRelatedField(
        queryset=Departamento.objects.filter(estado=True)
    )
    departamento_detalle = DepartamentoSummarySerializer(
        source="departamento", read_only=True
    )
    memberships = CuadrillaMembershipSerializer(many=True, required=False)

    membership_model = CuadrillaMembership
    membership_foreign_key = "cuadrilla"
    role_key = "cuadrilla"

    class Meta:
        model = Cuadrilla
        fields = [
            "cuadrilla_id",
            "nombre",
            "estado",
            "departamento",
            "departamento_detalle",
            "memberships",
        ]
        read_only_fields = ["cuadrilla_id"]

    def create(self, validated_data):
        return self._create_with_memberships(validated_data)

    def update(self, instance, validated_data):
        return self._update_with_memberships(instance, validated_data)


class TerritorialSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.select_related("user"),
        allow_null=True,
        required=False,
    )
    profile_detalle = ProfileSummarySerializer(source="profile", read_only=True)

    class Meta:
        model = Territorial
        fields = ["territorial_id", "nombre", "profile", "profile_detalle"]
        read_only_fields = ["territorial_id"]

    def validate_profile(self, profile):
        instance_pk = getattr(self.instance, "pk", None)
        if profile and profile.role_type and not _holds_current_role(profile, "territorial", instance_pk):
            raise serializers.ValidationError(
                _("El usuario seleccionado ya está asignado a otro rol.")
            )
        return profile

    def create(self, validated_data):
        profile = validated_data.get("profile")
        territorial = super().create(validated_data)
        if profile:
            _assign_role(profile, "territorial", territorial.pk)
        return territorial

    def update(self, instance, validated_data):
        profile_in_payload = "profile" in validated_data
        new_profile = validated_data.get("profile", instance.profile)
        previous_profile = instance.profile

        territorial = super().update(instance, validated_data)

        if profile_in_payload:
            if previous_profile and (not new_profile or previous_profile.pk != getattr(new_profile, "pk", None)):
                if _holds_current_role(previous_profile, "territorial", territorial.pk):
                    _clear_role(previous_profile)
            if new_profile:
                _assign_role(new_profile, "territorial", territorial.pk)
        return territorial
