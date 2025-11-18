from django.db.models import ProtectedError, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from orgs.models import Cuadrilla, Departamento, Direccion, Territorial

from .serializers import (
    CuadrillaSerializer,
    DepartamentoSerializer,
    DireccionSerializer,
    TerritorialSerializer,
)


class ProtectedDestroyMixin:
    """
    Maneja errores de eliminación cuando existen dependencias relacionadas.
    """

    protected_error_message = "No es posible eliminar el registro porque tiene elementos asociados."

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return Response(
                {"detail": self.protected_error_message},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class DireccionViewSet(ProtectedDestroyMixin, viewsets.ModelViewSet):
    serializer_class = DireccionSerializer
    permission_classes = [AllowAny]
    queryset = Direccion.objects.prefetch_related(
        "memberships__usuario_id__user"
    ).order_by("direccion_id")

    protected_error_message = "No se puede eliminar la dirección porque tiene departamentos asociados."

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get("q", "").strip()
        estado = self.request.query_params.get("estado", "").strip().lower()
        responsable = self.request.query_params.get("responsable", "").strip()

        if q:
            queryset = queryset.filter(nombre__icontains=q)

        if estado in {"activa", "activo", "true", "1"}:
            queryset = queryset.filter(estado=True)
        elif estado in {"bloqueada", "inactivo", "false", "0"}:
            queryset = queryset.filter(estado=False)

        if responsable:
            responsable_filter = (
                Q(memberships__usuario_id__user__username__icontains=responsable)
                | Q(memberships__usuario_id__user__first_name__icontains=responsable)
                | Q(memberships__usuario_id__user__last_name__icontains=responsable)
            )
            queryset = queryset.filter(
                Q(memberships__es_encargado=True) & responsable_filter
            )

        return queryset.distinct()

    @action(detail=True, methods=["post"], url_path="toggle-estado")
    def toggle_estado(self, request, pk=None):
        direccion = self.get_object()
        direccion.estado = not direccion.estado
        direccion.save(update_fields=["estado"])
        serializer = self.get_serializer(direccion)
        return Response(serializer.data)


class DepartamentoViewSet(ProtectedDestroyMixin, viewsets.ModelViewSet):
    serializer_class = DepartamentoSerializer
    permission_classes = [AllowAny]
    queryset = Departamento.objects.select_related("direccion").prefetch_related(
        "memberships__usuario_id__user"
    ).order_by("departamento_id")

    protected_error_message = "No se puede eliminar el departamento porque tiene cuadrillas asociadas."

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get("q", "").strip()
        estado = self.request.query_params.get("estado", "").strip().lower()
        direccion_id = self.request.query_params.get("direccion", "").strip()

        if q:
            queryset = queryset.filter(nombre__icontains=q)

        if estado in {"activo", "activa", "true", "1"}:
            queryset = queryset.filter(estado=True)
        elif estado in {"bloqueado", "inactivo", "false", "0"}:
            queryset = queryset.filter(estado=False)

        if direccion_id:
            queryset = queryset.filter(direccion__direccion_id=direccion_id)

        return queryset.distinct()

    @action(detail=True, methods=["post"], url_path="toggle-estado")
    def toggle_estado(self, request, pk=None):
        departamento = self.get_object()
        departamento.estado = not departamento.estado
        departamento.save(update_fields=["estado"])
        serializer = self.get_serializer(departamento)
        return Response(serializer.data)


class CuadrillaViewSet(ProtectedDestroyMixin, viewsets.ModelViewSet):
    serializer_class = CuadrillaSerializer
    permission_classes = [AllowAny]
    queryset = Cuadrilla.objects.select_related(
        "departamento", "departamento__direccion"
    ).prefetch_related("memberships__usuario_id__user").order_by("nombre")

    protected_error_message = "No se puede eliminar la cuadrilla porque mantiene dependencias."

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get("q", "").strip()
        estado = self.request.query_params.get("estado", "").strip().lower()
        departamento_id = self.request.query_params.get("departamento", "").strip()

        if q:
            queryset = queryset.filter(nombre__icontains=q)

        if estado in {"activo", "activa", "true", "1"}:
            queryset = queryset.filter(estado=True)
        elif estado in {"bloqueado", "inactivo", "false", "0"}:
            queryset = queryset.filter(estado=False)

        if departamento_id:
            queryset = queryset.filter(departamento__departamento_id=departamento_id)

        return queryset.distinct()

    @action(detail=True, methods=["post"], url_path="toggle-estado")
    def toggle_estado(self, request, pk=None):
        cuadrilla = self.get_object()
        cuadrilla.estado = not cuadrilla.estado
        cuadrilla.save(update_fields=["estado"])
        serializer = self.get_serializer(cuadrilla)
        return Response(serializer.data)


class TerritorialViewSet(viewsets.ModelViewSet):
    serializer_class = TerritorialSerializer
    permission_classes = [AllowAny]
    queryset = Territorial.objects.select_related("profile__user").order_by("nombre")

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get("q", "").strip()
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q)
                | Q(profile__user__first_name__icontains=q)
                | Q(profile__user__last_name__icontains=q)
                | Q(profile__user__username__icontains=q)
            )
        return queryset
