# usuarios/permissions.py
from rest_framework.permissions import BasePermission

from usuarios.serializers import get_rol


class EsAdministrador(BasePermission):
    def has_permission(self, request, view):
        return get_rol(request.user) == 'administrador'

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class EsAgente(BasePermission):
    def has_permission(self, request, view):
        return get_rol(request.user) == 'agente'

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class EsCliente(BasePermission):
    def has_permission(self, request, view):
        return get_rol(request.user) == 'cliente'

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class EsPropietarioOAdmin(BasePermission):
    """
    Permite acceso si el usuario es administrador, o si es el propietario
    del recurso (el recurso tiene un campo 'usuario' que es el User).
    """
    def has_object_permission(self, request, view, obj):
        if get_rol(request.user) == 'administrador':
            return True
        # Verificamos si el objeto tiene atributo 'usuario'
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        return False