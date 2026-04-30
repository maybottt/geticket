# usuarios/models.py
from django.db import models
from django.contrib.auth.hashers import make_password, check_password as django_check_password
from django.core.exceptions import ValidationError
from django.contrib.auth.models import BaseUserManager
from django.apps import apps

from instituciones.models import Institucion

class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, nombres, apellidos, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = BaseUserManager.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            nombres=nombres,
            apellidos=apellidos,
            **extra_fields
        )
        if password:
            user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, nombres, apellidos, password=None, **extra_fields):
        user = self.create_user(username, email, nombres, apellidos, password, **extra_fields)
        # Evita import circular usando apps.get_model
        Administrador = apps.get_model('usuarios', 'Administrador')
        Administrador.objects.get_or_create(usuario=user, defaults={'estado': 'activo'})
        return user

class Usuario(models.Model):
    class Estado(models.TextChoices):
        ACTIVO    = 'activo',    'Activo'
        INACTIVO  = 'inactivo',  'Inactivo'
        ELIMINADO = 'eliminado', 'Eliminado'

    username        = models.CharField(max_length=50, unique=True)
    email           = models.EmailField(max_length=255)
    password        = models.CharField(max_length=255)   # almacenado con hash
    nro_celular     = models.CharField(max_length=20, null=True, blank=True)
    nro_celular_dos = models.CharField(max_length=20, null=True, blank=True)
    user_telegram   = models.CharField(max_length=50, null=True, blank=True)
    ci              = models.CharField(max_length=20, null=True, blank=True)
    nombres         = models.CharField(max_length=100)
    apellidos       = models.CharField(max_length=100)
    estado          = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.ACTIVO,
    )
    last_login  = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'nombres', 'apellidos', 'nro_celular']
   
    objects = UsuarioManager()

    # Propiedades y métodos necesarios para Django y SimpleJWT
    @property
    def is_active(self):
        return self.estado == 'activo'

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def check_password(self, raw_password):
        return django_check_password(raw_password, self.password)

    def get_username(self):
        return self.username

    def natural_key(self):
        return (self.username,)

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.username} ({self.nombres} {self.apellidos})'

    def set_password(self, raw_password: str) -> None:
        """Hashea y guarda la contraseña."""
        self.password = make_password(raw_password)


class Cliente(models.Model):
    class Estado(models.TextChoices):
        ACTIVO    = 'activo',    'Activo'
        INACTIVO  = 'inactivo',  'Inactivo'
        ELIMINADO = 'eliminado', 'Eliminado'

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.PROTECT,
        related_name='perfil_cliente',
        db_column='id_usuario',
    )
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.PROTECT,
        related_name='clientes',
        db_column='id_institucion',
    )
    rol_institucion = models.CharField(max_length=50)
    estado          = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.ACTIVO,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        indexes = [
            models.Index(fields=['institucion'], name='idx_cliente_id_institucion'),
        ]

    def __str__(self):
        return f'Cliente: {self.usuario.username}'


class Agente(models.Model):
    class Estado(models.TextChoices):
        ACTIVO    = 'activo',    'Activo'
        INACTIVO  = 'inactivo',  'Inactivo'
        ELIMINADO = 'eliminado', 'Eliminado'

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.PROTECT,
        related_name='perfil_agente',
        db_column='id_usuario',
    )
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.ACTIVO,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'agente'
        verbose_name = 'Agente'
        verbose_name_plural = 'Agentes'

    def __str__(self):
        return f'Agente: {self.usuario.username}'


class Administrador(models.Model):
    class Estado(models.TextChoices):
        ACTIVO    = 'activo',    'Activo'
        INACTIVO  = 'inactivo',  'Inactivo'
        ELIMINADO = 'eliminado', 'Eliminado'

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.PROTECT,
        related_name='perfil_admin',
        db_column='id_usuario',
    )
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.ACTIVO,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'administrador'
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'

    def __str__(self):
        return f'Admin: {self.usuario.username}'