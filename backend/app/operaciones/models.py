#from django.db import models

# Create your models here.

from django.db import models


class Area(models.Model):

    ESTADO_CHOICES = [
        ('activo',    'Activo'),
        ('inactivo',  'Inactivo'),
        ('eliminado', 'Eliminado'),
    ]

    nombre     = models.CharField(max_length=100)
    estado     = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'area'
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'

    def __str__(self):
        return self.nombre


class Horario(models.Model):

    TURNO_CHOICES = [
        ('Mañana',        'Mañana'),
        ('Tarde',         'Tarde'),
        ('Completo',      'Completo'),
        ('Fin de semana', 'Fin de semana'),
        ('Personalizado', 'Personalizado'),
    ]

    nombre     = models.CharField(max_length=50, choices=TURNO_CHOICES)
    hora_inicio = models.TimeField()
    hora_fin    = models.TimeField()
    lunes      = models.BooleanField(default=False)
    martes     = models.BooleanField(default=False)
    miercoles  = models.BooleanField(default=False)
    jueves     = models.BooleanField(default=False)
    viernes    = models.BooleanField(default=False)
    sabado     = models.BooleanField(default=False)
    domingo    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'horario'
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'

    def __str__(self):
        return self.nombre


class CanalEntrada(models.Model):

    NOMBRE_CHOICES = [
        ('correo',          'Correo'),
        ('whatsapp',        'WhatsApp'),
        ('telegram',        'Telegram'),
        ('formulario_web',  'Formulario web'),
        ('chatbot_movil',   'Chatbot móvil'),
    ]
    ESTADO_CHOICES = [
        ('activo',    'Activo'),
        ('inactivo',  'Inactivo'),
        ('eliminado', 'Eliminado'),
    ]

    nombre      = models.CharField(max_length=50, choices=NOMBRE_CHOICES)
    descripcion = models.TextField(null=True, blank=True)
    estado      = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'canal_entrada'
        verbose_name = 'Canal de entrada'
        verbose_name_plural = 'Canales de entrada'

    def __str__(self):
        return self.nombre


class AgenteArea(models.Model):

    agente      = models.ForeignKey(
        'usuarios.Agente', on_delete=models.PROTECT,
        db_column='id_agente', related_name='agente_areas'
    )
    area        = models.ForeignKey(
        Area, on_delete=models.PROTECT,
        db_column='id_area', related_name='agente_areas'
    )
    asignado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'agente_area'
        verbose_name = 'Agente-Área'
        verbose_name_plural = 'Agentes-Áreas'
        constraints = [
            models.UniqueConstraint(fields=['agente', 'area'], name='uq_agente_area')
        ]

    def __str__(self):
        return f'{self.agente} → {self.area}'


class AgenteHorario(models.Model):

    agente         = models.ForeignKey(
        'usuarios.Agente', on_delete=models.PROTECT,
        db_column='id_agente', related_name='agente_horarios'
    )
    horario        = models.ForeignKey(
        Horario, on_delete=models.PROTECT,
        db_column='id_turno', related_name='agente_horarios'
    )
    vigente_desde  = models.DateField()
    vigente_hasta  = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'agente_horario'
        verbose_name = 'Agente-Horario'
        verbose_name_plural = 'Agentes-Horarios'

    def __str__(self):
        return f'{self.agente} — {self.horario}'
