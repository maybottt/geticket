from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaIncidenciaViewSet,
    TicketViewSet,
    AdjuntoViewSet,
    HistorialTicketViewSet,
    NotificacionViewSet,
    SatisfaccionTicketViewSet,
)

router = DefaultRouter()
router.register(r'categorias', CategoriaIncidenciaViewSet, basename='categorias')
router.register(r'tickets', TicketViewSet, basename='tickets')
router.register(r'adjuntos', AdjuntoViewSet, basename='adjuntos')
router.register(r'historial', HistorialTicketViewSet, basename='historial')
router.register(r'notificaciones', NotificacionViewSet, basename='notificaciones')
router.register(r'satisfaccion', SatisfaccionTicketViewSet, basename='satisfaccion')

urlpatterns = router.urls