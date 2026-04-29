# usuarios/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password

from .models import Usuario, Agente, Cliente, Administrador
from instituciones.models import Institucion


# ──────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────

def get_rol(user):
    if hasattr(user, 'perfil_admin') and user.perfil_admin.estado == 'activo':
        return 'administrador'
    if hasattr(user, 'perfil_agente') and user.perfil_agente.estado == 'activo':
        return 'agente'
    if hasattr(user, 'perfil_cliente') and user.perfil_cliente.estado == 'activo':
        return 'cliente'
    return None


def get_token_para_usuario(user):
    rol = get_rol(user)
    refresh = RefreshToken.for_user(user)
    refresh['rol'] = rol
    return refresh


# ──────────────────────────────────────────
# Auth
# ──────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        from django.contrib.auth import authenticate
        user = authenticate(
            username=attrs['username'],
            password=attrs['password']
        )
        if not user:
            raise serializers.ValidationError('Credenciales incorrectas.')
        if user.estado != 'activo':
            raise serializers.ValidationError('Usuario inactivo o eliminado.')

        rol = get_rol(user)
        if not rol:
            raise serializers.ValidationError('El usuario no tiene un rol activo asignado.')

        attrs['user'] = user
        attrs['rol'] = rol
        return attrs


# ──────────────────────────────────────────
# Usuario
# ──────────────────────────────────────────

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'nombres', 'apellidos',
            'nro_celular', 'nro_celular_dos', 'user_telegram', 'ci',
            'estado', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'nombres', 'apellidos',
            'nro_celular', 'nro_celular_dos', 'user_telegram', 'ci', 'estado',
        ]


class PasswordChangeSerializer(serializers.Serializer):
    password_actual = serializers.CharField(write_only=True)
    password_nuevo = serializers.CharField(write_only=True, min_length=8)

    def validate_password_actual(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('La contraseña actual es incorrecta.')
        return value


class RegistroUsuarioBaseSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    nombres = serializers.CharField(max_length=100)
    apellidos = serializers.CharField(max_length=100)
    nro_celular = serializers.CharField(max_length=20, required=False, allow_blank=True)
    nro_celular_dos = serializers.CharField(max_length=20, required=False, allow_blank=True)
    user_telegram = serializers.CharField(max_length=50, required=False, allow_blank=True)
    ci = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError('Ya existe un usuario con este email.')
        return value

    def validate_username(self, value):
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError('Ya existe un usuario con este username.')
        return value


class UsuarioConRolSerializer(serializers.ModelSerializer):
    rol = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'nombres', 'apellidos',
            'nro_celular', 'nro_celular_dos', 'user_telegram', 'ci',
            'estado', 'created_at', 'rol',
        ]
        read_only_fields = ['id', 'created_at']

    def get_rol(self, obj):
        return get_rol(obj)


# ──────────────────────────────────────────
# Agente
# ──────────────────────────────────────────

class AgenteSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)

    class Meta:
        model = Agente
        fields = ['id', 'usuario', 'estado', 'created_at']
        read_only_fields = ['id', 'created_at']


class AgenteCreateSerializer(RegistroUsuarioBaseSerializer):
    estado = serializers.ChoiceField(choices=['activo', 'inactivo'], default='inactivo')

    def create(self, validated_data):
        password = validated_data.pop('password')
        estado = validated_data.pop('estado', 'inactivo')

        user = Usuario(**validated_data, estado='inactivo')
        user.set_password(password)
        user.save()

        return Agente.objects.create(usuario=user, estado=estado)


# ──────────────────────────────────────────
# Cliente
# ──────────────────────────────────────────

class ClienteSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    institucion = serializers.StringRelatedField()

    class Meta:
        model = Cliente
        fields = ['id', 'usuario', 'institucion', 'rol_institucion', 'estado', 'created_at']
        read_only_fields = ['id', 'created_at']


class ClienteCreateSerializer(RegistroUsuarioBaseSerializer):
    id_institucion = serializers.IntegerField()
    rol_institucion = serializers.CharField(max_length=50, required=False, allow_blank=True)
    estado = serializers.ChoiceField(
        choices=['activo', 'inactivo', 'eliminado'], default='inactivo', required=False
    )

    def validate_id_institucion(self, value):
        if not Institucion.objects.filter(pk=value, estado='activo').exists():
            raise serializers.ValidationError('Institución no encontrada o inactiva.')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        id_institucion = validated_data.pop('id_institucion')
        rol_institucion = validated_data.pop('rol_institucion', '')
        estado = validated_data.pop('estado', 'inactivo')

        user = Usuario(**validated_data, estado='inactivo')
        user.set_password(password)
        user.save()

        institucion = Institucion.objects.get(pk=id_institucion)

        return Cliente.objects.create(
            usuario=user,
            institucion=institucion,
            rol_institucion=rol_institucion,
            estado=estado,
        )


# ──────────────────────────────────────────
# Administrador
# ──────────────────────────────────────────

class AdministradorSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)

    class Meta:
        model = Administrador
        fields = ['id', 'usuario', 'estado', 'created_at']
        read_only_fields = ['id', 'created_at']


class AdministradorCreateSerializer(RegistroUsuarioBaseSerializer):
    estado = serializers.ChoiceField(choices=['activo', 'inactivo'], default='activo')

    def create(self, validated_data):
        password = validated_data.pop('password')
        estado = validated_data.pop('estado', 'activo')

        user = Usuario(**validated_data, estado='activo')
        user.set_password(password)
        user.save()

        return Administrador.objects.create(usuario=user, estado=estado)