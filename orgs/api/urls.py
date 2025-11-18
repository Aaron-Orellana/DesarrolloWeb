from rest_framework.routers import DefaultRouter

from .views import (
    CuadrillaViewSet,
    DepartamentoViewSet,
    DireccionViewSet,
    TerritorialViewSet,
)

router = DefaultRouter()
router.register(r"direcciones", DireccionViewSet, basename="orgs-direcciones")
router.register(r"departamentos", DepartamentoViewSet, basename="orgs-departamentos")
router.register(r"cuadrillas", CuadrillaViewSet, basename="orgs-cuadrillas")
router.register(r"territoriales", TerritorialViewSet, basename="orgs-territoriales")

urlpatterns = router.urls
