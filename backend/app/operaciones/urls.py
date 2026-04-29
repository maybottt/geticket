from rest_framework.routers import DefaultRouter
from .views import (
    CanalEntradaViewSet, HorarioViewSet,
    AgenteAreaViewSet, AgenteHorarioViewSet
)

router = DefaultRouter()
router.register(r'canales', CanalEntradaViewSet, basename='canales')
router.register(r'horarios', HorarioViewSet, basename='horarios')
router.register(r'agente-areas', AgenteAreaViewSet, basename='agente-areas')
router.register(r'agente-horarios', AgenteHorarioViewSet, basename='agente-horarios')

urlpatterns = router.urls