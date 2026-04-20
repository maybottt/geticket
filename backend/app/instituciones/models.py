# Create your models here.

from django.db import models


class Institucion(models.Model):

    ESTADO_CHOICES = [
        ('activo',    'Activo'),
        ('inactivo',  'Inactivo'),
        ('eliminado', 'Eliminado'),
    ]

    nombre      = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=50, null=True, blank=True)
    direccion   = models.TextField(null=True, blank=True)
    telefono    = models.CharField(max_length=20, null=True, blank=True)
    email       = models.EmailField(max_length=255, null=True, blank=True)
    estado      = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'institucion'
        verbose_name = 'Institución'
        verbose_name_plural = 'Instituciones'

    def __str__(self):
        return self.nombre


class Sistema(models.Model):

    ESTADO_CHOICES = [
        ('activo',    'Activo'),
        ('inactivo',  'Inactivo'),
        ('eliminado', 'Eliminado'),
    ]

    instituciones = models.ManyToManyField(
        Institucion,
        through='InstitucionSistema',
        related_name='sistemas'
    )
    nombre      = models.CharField(max_length=255)
    version     = models.CharField(max_length=50, null=True, blank=True)
    estado      = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sistema'
        verbose_name = 'Sistema'
        verbose_name_plural = 'Sistemas'

    def __str__(self):
        return f'{self.nombre} v{self.version}'

class InstitucionSistema(models.Model):
 
    institucion = models.ForeignKey(
        Institucion, on_delete=models.PROTECT,
        db_column='id_institucion', related_name='institucion_sistemas'
    )
    sistema     = models.ForeignKey(
        Sistema, on_delete=models.PROTECT,
        db_column='id_sistema', related_name='institucion_sistemas'
    )
 
    class Meta:
        db_table = 'institucion_sistema'
        verbose_name = 'Institución-Sistema'
        verbose_name_plural = 'Instituciones-Sistemas'
        constraints = [
            models.UniqueConstraint(fields=['institucion', 'sistema'], name='uq_inst_sistema')
        ]
 
    def __str__(self):
        return f'{self.institucion} ↔ {self.sistema}'