from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView, ElegirRolView, SwitchRolView,
    MeView, PasswordChangeView,
    AgenteListCreateView, AgenteDetailView,
    ClienteListCreateView, ClienteDetailView, RegistroClienteView, 
    AprobarClienteView, ClienteToggleActivoView,
    ClienteEliminarView, RegistroUsuarioPublicoView,
    UsuarioListCreateView, UsuarioDetailView,
    AprobarUsuarioView,
    AsignarRolAgenteView, AsignarRolClienteView,
    RemoverRolAgenteView, RemoverRolClienteView, RegistroAgenteView, AgenteAprobarView, 
    AgenteToggleActivoView, 
)

urlpatterns = [
    # Auth
    path('auth/login/',           LoginView.as_view(),        name='login'),
    path('auth/elegir-rol/',      ElegirRolView.as_view(),    name='elegir_rol'),
    path('auth/switch-rol/',      SwitchRolView.as_view(),    name='switch_rol'),
    path('auth/refresh/',         TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/',              MeView.as_view(),           name='me'),
    path('auth/change-password/', PasswordChangeView.as_view(), name='change_password'),
    
    # Registro público
    path('auth/registro/cliente/', RegistroClienteView.as_view(), name='registro_cliente'),
    path('auth/registro/agente/',  RegistroAgenteView.as_view(),  name='registro_agente'),
    path('auth/registro/usuario/',   RegistroUsuarioPublicoView.as_view(), name='registro_usuario_publico'),

    # Clientes
    path('clientes/',          ClienteListCreateView.as_view(), name='cliente_list_create'),
    path('clientes/<int:pk>/', ClienteDetailView.as_view(),    name='cliente_detail'),
    path('clientes/<int:pk>/aprobar/',    AprobarClienteView.as_view(),    name='cliente_aprobar'),
    path('clientes/<int:pk>/toggle-activo/', ClienteToggleActivoView.as_view(), name='cliente_toggle_activo'),
    path('clientes/<int:pk>/eliminar/',   ClienteEliminarView.as_view(),   name='cliente_eliminar'),
 
    # Agentes
    path('agentes/',          AgenteListCreateView.as_view(), name='agente_list_create'),
    path('agentes/<int:pk>/', AgenteDetailView.as_view(),    name='agente_detail'),
    path('agentes/<int:pk>/aprobar/',      AgenteAprobarView.as_view(),      name='agente_aprobar'),
    path('agentes/<int:pk>/toggle-activo/',AgenteToggleActivoView.as_view(), name='agente_toggle_activo'),

    # Usuarios (admin)
    path('usuarios/',                     UsuarioListCreateView.as_view(), name='usuario_list_create'),
    path('usuarios/<int:pk>/',            UsuarioDetailView.as_view(),     name='usuario_detail'),
    path('usuarios/<int:pk>/aprobar/',    AprobarUsuarioView.as_view(),    name='usuario_aprobar'),
    path('usuarios/<int:pk>/asignar-agente/',  AsignarRolAgenteView.as_view(), name='usuario_asignar_agente'),
    path('usuarios/<int:pk>/asignar-cliente/', AsignarRolClienteView.as_view(), name='usuario_asignar_cliente'),
    path('usuarios/<int:pk>/remover-agente/',  RemoverRolAgenteView.as_view(), name='usuario_remover_agente'),
    path('usuarios/<int:pk>/remover-cliente/', RemoverRolClienteView.as_view(), name='usuario_remover_cliente'),

    
]