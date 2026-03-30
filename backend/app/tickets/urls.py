from django.urls import path
from .views import (
    SolicitudListCreateView,
    TicketListView, TicketDetailView,
    TicketAsignarView, TicketDesasignarView, TicketAsignarAutomaticoView,
    TicketEscalarView, TicketSolucionarView,
    TicketConfirmarView, TicketCerrarView, TicketRechazarView,
    NotificacionListView,
)

urlpatterns = [
    # Solicitudes y creación de tickets
    path('solicitudes/', SolicitudListCreateView.as_view(), name='solicitud_list_create'),

    # Tickets
    path('tickets/',          TicketListView.as_view(),   name='ticket_list'),
    path('tickets/<int:pk>/', TicketDetailView.as_view(), name='ticket_detail'),

    # Acciones
    path('tickets/<int:pk>/asignar/',            TicketAsignarView.as_view(),          name='ticket_asignar'),
    path('tickets/<int:pk>/desasignar/',         TicketDesasignarView.as_view(),        name='ticket_desasignar'),
    path('tickets/<int:pk>/asignar-automatico/', TicketAsignarAutomaticoView.as_view(), name='ticket_asignar_auto'),
    path('tickets/<int:pk>/escalar/',            TicketEscalarView.as_view(),           name='ticket_escalar'),
    path('tickets/<int:pk>/solucionar/',         TicketSolucionarView.as_view(),        name='ticket_solucionar'),
    path('tickets/<int:pk>/confirmar/',          TicketConfirmarView.as_view(),         name='ticket_confirmar'),
    path('tickets/<int:pk>/cerrar/',             TicketCerrarView.as_view(),            name='ticket_cerrar'),
    path('tickets/<int:pk>/rechazar/',           TicketRechazarView.as_view(),          name='ticket_rechazar'),

    # Notificaciones
    path('notificaciones/', NotificacionListView.as_view(), name='notificacion_list'),
]