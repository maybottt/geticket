# usuarios/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoginView,
    PasswordChangeView,
    RegistroClienteView,
    UsuarioViewSet,
    MiPerfilView,
    AgenteViewSet,
    ClienteViewSet,
    AdministradorViewSet,
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')
router.register(r'agentes', AgenteViewSet, basename='agentes')
router.register(r'clientes', ClienteViewSet, basename='clientes')
router.register(r'administradores', AdministradorViewSet, basename='administradores')

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/password-change/', PasswordChangeView.as_view(), name='password-change'),
    path('auth/registro-cliente/', RegistroClienteView.as_view(), name='registro-cliente'),
    path('perfil/', MiPerfilView.as_view(), name='mi-perfil'),
    path('', include(router.urls)),
]