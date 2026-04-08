from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView, ElegirRolView, SwitchRolView,
    MeView, PasswordChangeView,
    AgenteListCreateView, AgenteDetailView,
    ClienteListCreateView, ClienteDetailView, RegistroClienteView, 
)

urlpatterns = [
    # Auth
    path('auth/login/',           LoginView.as_view(),        name='login'),
    path('auth/elegir-rol/',      ElegirRolView.as_view(),    name='elegir_rol'),
    path('auth/switch-rol/',      SwitchRolView.as_view(),    name='switch_rol'),
    path('auth/refresh/',         TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/',              MeView.as_view(),           name='me'),
    path('auth/change-password/', PasswordChangeView.as_view(), name='change_password'),

    # Agentes
    path('agentes/',          AgenteListCreateView.as_view(), name='agente_list_create'),
    path('agentes/<int:pk>/', AgenteDetailView.as_view(),    name='agente_detail'),

    # Clientes
    path('clientes/',          ClienteListCreateView.as_view(), name='cliente_list_create'),
    path('clientes/<int:pk>/', ClienteDetailView.as_view(),    name='cliente_detail'),

    # Público 
    path('auth/registro/', RegistroClienteView.as_view(), name='registro_cliente'),

    path('clientes/<int:pk>/aprobar/', AprobarClienteView.as_view(), name='cliente_aprobar'),
]