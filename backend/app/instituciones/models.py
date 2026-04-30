# instituciones/models.py
from django.db import models


class Institucion(models.Model):
    class TipoInstitucion(models.TextChoices):
        HOSPITAL    = 'hospital',    'Hospital'
        COLEGIO     = 'colegio',     'Colegio'
        LABORATORIO = 'laboratorio', 'Laboratorio'
        OTRO        = 'otro',        'Otro'

    class Estado(models.TextChoices):
        ACTIVO    = 'activo',    'Activo'
        INACTIVO  = 'inactivo',  'Inactivo'
        ELIMINADO = 'eliminado', 'Eliminado'

    nombre           = models.CharField(max_length=255)
    tipo_institucion = models.CharField(
        max_length=50, choices=TipoInstitucion.choices, null=True, blank=True
    )
    descripcion = models.TextField(null=True, blank=True)
    direccion   = models.TextField(null=True, blank=True)
    telefono    = models.CharField(max_length=20, null=True, blank=True)
    email       = models.EmailField(max_length=255, null=True, blank=True)
    estado      = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.ACTIVO
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'institucion'
        verbose_name = 'Institución'
        verbose_name_plural = 'Instituciones'

    def __str__(self):
        return self.nombre


class Sistema(models.Model):
    class Estado(models.TextChoices):
        ACTIVO    = 'activo',    'Activo'
        INACTIVO  = 'inactivo',  'Inactivo'
        ELIMINADO = 'eliminado', 'Eliminado'

    nombre  = models.CharField(max_length=255)
    version = models.CharField(max_length=50, null=True, blank=True)
    estado  = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.ACTIVO,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sistema'
        verbose_name = 'Sistema'
        verbose_name_plural = 'Sistemas'

    def __str__(self):
        return f'{self.nombre} ({self.version or "s/v"})'

class InstitucionSistema(models.Model):
    institucion = models.ForeignKey(
        Institucion,
        on_delete=models.CASCADE,
        related_name='institucion_sistemas',
        db_column='id_institucion',
    )
    sistema = models.ForeignKey(
        Sistema,
        on_delete=models.CASCADE,
        related_name='institucion_sistemas',
        db_column='id_sistema',
    )

    class Meta:
        db_table = 'institucion_sistema'
        verbose_name = 'Institución-Sistema'
        verbose_name_plural = 'Instituciones-Sistemas'
        constraints = [
            models.UniqueConstraint(
                fields=['institucion', 'sistema'],
                name='uq_inst_sistema',
            )
        ]

    def __str__(self):
        return f'{self.institucion} — {self.sistema}'


class Area(models.Model):
    class Estado(models.TextChoices):
        ACTIVO    = 'activo',    'Activo'
        INACTIVO  = 'inactivo',  'Inactivo'
        ELIMINADO = 'eliminado', 'Eliminado'

    nombre = models.CharField(max_length=100)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.ACTIVO
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'area'
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'

    def __str__(self):
        return self.nombre