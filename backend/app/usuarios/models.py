
# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UsuarioManager


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Cuenta de acceso única. Un usuario = un rol = una institución.
    Si una persona pertenece a dos instituciones, crea dos cuentas distintas.
    """
    username        = models.CharField(max_length=50, unique=True)
    email           = models.EmailField(max_length=255, unique=True)
    nro_celular     = models.CharField(max_length=20, null=True, blank=True)
    nro_celular_dos = models.CharField(max_length=20, null=True, blank=True)
    user_telegram   = models.CharField(max_length=50, null=True, blank=True)
    ci              = models.CharField(max_length=20, null=True, blank=True)
    nombres         = models.CharField(max_length=100)
    apellidos       = models.CharField(max_length=100)
    is_active       = models.BooleanField(default=True)
    last_login      = models.DateTimeField(auto_now=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
 
    objects = UsuarioManager()
 
    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = ['email', 'nombres', 'apellidos']
 
    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
 
    def __str__(self):
        return f'{self.nombres} {self.apellidos} <{self.email}>'
 
    @property
    def is_staff(self):
        """Requerido por Django admin. Solo los administradores tienen acceso."""
        return hasattr(self, 'administrador') and self.administrador.estado == 'activo'
 
    @property
    def rol(self):
        """Devuelve el rol de esta cuenta, o None si aún no tiene perfil asignado."""
        if hasattr(self, 'administrador'):
            return 'administrador'
        if hasattr(self, 'agente'):
            return 'agente'
        if hasattr(self, 'cliente'):
            return 'cliente'
        return None
 
 
class Agente(models.Model):
 
    ESTADO_CHOICES = [
        ('activo',    'Activo'),
        ('inactivo',  'Inactivo'),
        ('eliminado', 'Eliminado'),
    ]
 
    usuario    = models.OneToOneField(
        Usuario, on_delete=models.PROTECT,
        db_column='id_usuario', related_name='agente'
    )
    estado     = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table = 'agente'
        verbose_name = 'Agente'
        verbose_name_plural = 'Agentes'
 
    def __str__(self):
        return str(self.usuario)
 
 
class Cliente(models.Model):
 
    ESTADO_CHOICES = [
        ('activo',    'Activo'),
        ('inactivo',  'Inactivo'),
        ('eliminado', 'Eliminado'),
    ]
 
    usuario         = models.OneToOneField(
        Usuario, on_delete=models.PROTECT,
        db_column='id_usuario', related_name='cliente'
    )
    institucion     = models.ForeignKey(
        'instituciones.Institucion', on_delete=models.PROTECT,
        db_column='id_institucion', related_name='clientes'
    )
    rol_institucion = models.CharField(max_length=50, blank=True)
    estado          = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='activo')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table = 'cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
 
    def __str__(self):
        return str(self.usuario)
 
 
class Administrador(models.Model):
 
    ESTADO_CHOICES = [
        ('activo',    'Activo'),
        ('inactivo',  'Inactivo'),
        ('eliminado', 'Eliminado'),
    ]
 
    usuario    = models.OneToOneField(
        Usuario, on_delete=models.PROTECT,
        db_column='id_usuario', related_name='administrador'
    )
    estado     = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table = 'administrador'
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'
 
    def __str__(self):
        return str(self.usuario)