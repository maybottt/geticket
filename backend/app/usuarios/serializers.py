from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Agrega datos del usuario al token de respuesta."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id':        self.user.pk,
            'username':  self.user.username,
            'email':     self.user.email,
            'nombres':   self.user.nombres,
            'apellidos': self.user.apellidos,
            'is_admin':  self.user.is_admin,
            'rol':       self._get_rol(self.user),
        }
        return data

    def _get_rol(self, user):
        if user.is_admin:
            return 'administrador'
        if hasattr(user, 'agente'):
            return 'agente'
        if hasattr(user, 'cliente'):
            return 'cliente'
        return None


class UsuarioSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Usuario
        fields = [
            'id', 'username', 'email', 'nombres', 'apellidos',
            'nro_celular', 'user_telegram', 'ci',
            'is_admin', 'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']