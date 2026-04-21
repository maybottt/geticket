from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView, MeView, PasswordChangeView,
    AgenteListCreateView, AgenteDetailView,
    AgenteAprobarView, AgenteToggleActivoView,
    ClienteListCreateView, ClienteDetailView,
    AprobarClienteView, ClienteToggleActivoView, ClienteEliminarView,
    AdministradorListCreateView, AdministradorDetailView,
    RegistroClienteView, RegistroAgenteView,
    UsuarioListCreateView, UsuarioDetailView, AprobarUsuarioView,
)

urlpatterns = [
    # Auth
    path('auth/login/',           LoginView.as_view(),          name='login'),
    path('auth/refresh/',         TokenRefreshView.as_view(),   name='token_refresh'),
    path('auth/me/',              MeView.as_view(),             name='me'),
    path('auth/change-password/', PasswordChangeView.as_view(), name='change_password'),

    # Registro público
    path('auth/registro/cliente/', RegistroClienteView.as_view(), name='registro_cliente'),
    path('auth/registro/agente/',  RegistroAgenteView.as_view(),  name='registro_agente'),

    # Clientes
    path('clientes/',                        ClienteListCreateView.as_view(),  name='cliente_list_create'),
    path('clientes/<int:pk>/',               ClienteDetailView.as_view(),      name='cliente_detail'),
    path('clientes/<int:pk>/aprobar/',       AprobarClienteView.as_view(),     name='cliente_aprobar'),
    path('clientes/<int:pk>/toggle-activo/', ClienteToggleActivoView.as_view(),name='cliente_toggle_activo'),
    path('clientes/<int:pk>/eliminar/',      ClienteEliminarView.as_view(),    name='cliente_eliminar'),

    # Agentes
    path('agentes/',                        AgenteListCreateView.as_view(),  name='agente_list_create'),
    path('agentes/<int:pk>/',               AgenteDetailView.as_view(),      name='agente_detail'),
    path('agentes/<int:pk>/aprobar/',       AgenteAprobarView.as_view(),     name='agente_aprobar'),
    path('agentes/<int:pk>/toggle-activo/', AgenteToggleActivoView.as_view(),name='agente_toggle_activo'),

    # Administradores
    path('administradores/',          AdministradorListCreateView.as_view(), name='admin_list_create'),
    path('administradores/<int:pk>/', AdministradorDetailView.as_view(),     name='admin_detail'),

    # Usuarios (admin — gestión general)
    path('usuarios/',                  UsuarioListCreateView.as_view(), name='usuario_list_create'),
    path('usuarios/<int:pk>/',         UsuarioDetailView.as_view(),     name='usuario_detail'),
    path('usuarios/<int:pk>/aprobar/', AprobarUsuarioView.as_view(),   name='usuario_aprobar'),
]