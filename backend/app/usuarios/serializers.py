from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Usuario, Agente, Cliente


# ──────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────

def get_roles(user):
    """Devuelve la lista de roles que tiene el usuario."""
    roles = []
    if user.is_admin:
        roles.append('administrador')
    if hasattr(user, 'agente') and user.agente.estado == 'activo':
        roles.append('agente')
    if hasattr(user, 'cliente'):
        roles.append('cliente')
    return roles


def get_token_para_rol(user, rol):
    """Genera un RefreshToken con el rol_activo en el payload."""
    roles_disponibles = get_roles(user)
    if rol not in roles_disponibles:
        raise serializers.ValidationError(
            f'El usuario no tiene el rol "{rol}".'
        )
    refresh = RefreshToken.for_user(user)
    refresh['rol_activo'] = rol
    refresh['roles']      = roles_disponibles
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
        if not user.is_active:
            raise serializers.ValidationError('Usuario inactivo.')

        roles = get_roles(user)
        if not roles:
            raise serializers.ValidationError('El usuario no tiene ningún rol asignado.')

        attrs['user']  = user
        attrs['roles'] = roles
        return attrs


class ElegirRolSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    rol     = serializers.CharField()

    def validate(self, attrs):
        try:
            user = Usuario.objects.get(pk=attrs['user_id'], is_active=True)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError('Usuario no encontrado.')

        roles = get_roles(user)
        if attrs['rol'] not in roles:
            raise serializers.ValidationError(
                f'El usuario no tiene el rol "{attrs["rol"]}".'
            )
        attrs['user']  = user
        attrs['roles'] = roles
        return attrs


class SwitchRolSerializer(serializers.Serializer):
    rol = serializers.CharField()

    def validate_rol(self, value):
        user  = self.context['request'].user
        roles = get_roles(user)
        if value not in roles:
            raise serializers.ValidationError(
                f'No tienes el rol "{value}".'
            )
        return value


# ──────────────────────────────────────────
# Usuario
# ──────────────────────────────────────────

class UsuarioSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Usuario
        fields = [
            'id', 'username', 'email', 'nombres', 'apellidos',
            'nro_celular', 'user_telegram', 'ci',
            'is_admin', 'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class UsuarioUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Usuario
        fields = [
            'username', 'email', 'nombres', 'apellidos',
            'nro_celular', 'user_telegram', 'ci', 'is_active',
        ]


class PasswordChangeSerializer(serializers.Serializer):
    password_actual = serializers.CharField(write_only=True)
    password_nuevo  = serializers.CharField(write_only=True, min_length=8)

    def validate_password_actual(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('La contraseña actual es incorrecta.')
        return value

class RegistroUsuarioPublicoSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    nombres = serializers.CharField(max_length=100)
    apellidos = serializers.CharField(max_length=100)
    nro_celular = serializers.CharField(max_length=20, required=False, allow_blank=True)
    user_telegram = serializers.CharField(max_length=50, required=False, allow_blank=True)
    ci = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return value

    def validate_username(self, value):
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este username.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario(**validated_data, is_active=False)
        user.set_password(password)
        user.save()
        return user

class UsuarioConRolesSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    is_agente = serializers.BooleanField(source='agente', read_only=True)
    is_cliente = serializers.BooleanField(source='cliente', read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'nombres', 'apellidos',
            'nro_celular', 'user_telegram', 'ci',
            'is_admin', 'is_active', 'created_at', 'roles',
            'is_agente', 'is_cliente'
        ]
        read_only_fields = ['id', 'created_at']

    def get_roles(self, obj):
        return get_roles(obj)


# ──────────────────────────────────────────
# Agente
# ──────────────────────────────────────────

class AgenteSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)

    class Meta:
        model  = Agente
        fields = ['id', 'usuario', 'estado', 'created_at']
        read_only_fields = ['id', 'created_at']


class AgenteCreateSerializer(serializers.Serializer):
    username      = serializers.CharField(max_length=150)
    email         = serializers.EmailField()
    password      = serializers.CharField(write_only=True, min_length=8)
    nombres       = serializers.CharField(max_length=100)
    apellidos     = serializers.CharField(max_length=100)
    nro_celular   = serializers.CharField(max_length=20,  required=False, allow_blank=True)
    user_telegram = serializers.CharField(max_length=50,  required=False, allow_blank=True)
    ci            = serializers.CharField(max_length=20,  required=False, allow_blank=True)
    estado        = serializers.ChoiceField(choices=['activo', 'inactivo'], default='activo')

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError('Ya existe un usuario con este email.')
        return value

    def validate_username(self, value):
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError('Ya existe un usuario con este username.')
        return value

    def create(self, validated_data):
        estado   = validated_data.pop('estado', 'activo')
        password = validated_data.pop('password')
        user     = Usuario(**validated_data, is_active=False)
        user.set_password(password)
        user.save()
        return Agente.objects.create(usuario=user, estado=estado)


# ──────────────────────────────────────────
# Cliente
# ──────────────────────────────────────────

class ClienteSerializer(serializers.ModelSerializer):
    usuario     = UsuarioSerializer(read_only=True)
    institucion = serializers.StringRelatedField()

    class Meta:
        model  = Cliente
        fields = ['id', 'usuario', 'institucion', 'rol_institucion', 'estado', 'created_at']
        read_only_fields = ['id', 'created_at']


class ClienteCreateSerializer(serializers.Serializer):
    username        = serializers.CharField(max_length=150)
    email           = serializers.EmailField()
    password        = serializers.CharField(write_only=True, min_length=8)
    nombres         = serializers.CharField(max_length=100)
    apellidos       = serializers.CharField(max_length=100)
    nro_celular     = serializers.CharField(max_length=20, required=False, allow_blank=True)
    user_telegram   = serializers.CharField(max_length=50, required=False, allow_blank=True)
    ci              = serializers.CharField(max_length=20, required=False, allow_blank=True)
    id_institucion  = serializers.IntegerField()
    rol_institucion = serializers.ChoiceField(
        choices=['medico', 'cajero', 'almacenes'], required=False, allow_null=True
    )
    estado = serializers.ChoiceField(
        choices=['activo', 'inactivo', 'eliminado'], default='inactivo', required=False
    )

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError('Ya existe un usuario con este email.')
        return value

    def validate_username(self, value):
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError('Ya existe un usuario con este username.')
        return value

    def validate_id_institucion(self, value):
        from instituciones.models import Institucion
        if not Institucion.objects.filter(pk=value, estado='activo').exists():
            raise serializers.ValidationError('Institución no encontrada o inactiva.')
        return value

    def create(self, validated_data):
        from instituciones.models import Institucion
        id_institucion  = validated_data.pop('id_institucion')
        rol_institucion = validated_data.pop('rol_institucion', None)
        password        = validated_data.pop('password')
        user            = Usuario(**validated_data, is_active=False)
        user.set_password(password)
        user.save()
        return Cliente.objects.create(
            usuario=user,
            institucion=Institucion.objects.get(pk=id_institucion),
            rol_institucion=rol_institucion, 
            estado=estado,
        )