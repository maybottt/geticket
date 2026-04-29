from rest_framework.routers import DefaultRouter
from .views import (
    InstitucionViewSet, SistemaViewSet,
    InstitucionSistemaViewSet, AreaViewSet
)

router = DefaultRouter()
router.register(r'instituciones', InstitucionViewSet, basename='instituciones')
router.register(r'sistemas', SistemaViewSet, basename='sistemas')
router.register(r'institucion-sistemas', InstitucionSistemaViewSet, basename='institucion-sistemas')
router.register(r'areas', AreaViewSet, basename='areas')

urlpatterns = router.urls