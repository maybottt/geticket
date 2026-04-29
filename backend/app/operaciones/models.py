# operaciones/models.py
from django.db import models
from django.core.exceptions import ValidationError

from instituciones.models import Area
from usuarios.models import Agente


class CanalEntrada(models.Model):
    class NombreCanal(models.TextChoices):
        CORREO          = 'correo',           'Correo'
        WHATSAPP        = 'whatsapp',         'WhatsApp'
        TELEGRAM        = 'telegram',         'Telegram'
        FORMULARIO_WEB  = 'formulario_web',   'Formulario web'
        CHATBOT_MOVIL   = 'chatbot_movil',    'Chatbot móvil'
        LLAMADA         = 'llamada',          'Llamada'

    class Estado(models.TextChoices):
        ACTIVO    = 'activo',    'Activo'
        INACTIVO  = 'inactivo',  'Inactivo'
        ELIMINADO = 'eliminado', 'Eliminado'

    nombre      = models.CharField(max_length=50, choices=NombreCanal.choices)
    descripcion = models.TextField(null=True, blank=True)
    estado      = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.ACTIVO
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'canal_entrada'
        verbose_name = 'Canal de entrada'
        verbose_name_plural = 'Canales de entrada'

    def __str__(self):
        return self.get_nombre_display()


class Horario(models.Model):
    class NombreTurno(models.TextChoices):
        MANANA        = 'Mañana',        'Mañana'
        TARDE         = 'Tarde',         'Tarde'
        COMPLETO      = 'Completo',      'Completo'
        FIN_SEMANA    = 'Fin de semana', 'Fin de semana'
        PERSONALIZADO = 'Personalizado', 'Personalizado'

    nombre      = models.CharField(max_length=50, choices=NombreTurno.choices)
    hora_inicio = models.TimeField()
    hora_fin    = models.TimeField()
    lunes       = models.BooleanField(default=False)
    martes      = models.BooleanField(default=False)
    miercoles   = models.BooleanField(default=False)
    jueves      = models.BooleanField(default=False)
    viernes     = models.BooleanField(default=False)
    sabado      = models.BooleanField(default=False)
    domingo     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'horario'
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'

    def __str__(self):
        return f'{self.nombre} ({self.hora_inicio}–{self.hora_fin})'


class AgenteArea(models.Model):
    agente = models.ForeignKey(
        Agente,
        on_delete=models.PROTECT,
        related_name='agente_areas',
        db_column='id_agente',
    )
    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        related_name='agente_areas',
        db_column='id_area',
    )
    asignado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'agente_area'
        verbose_name = 'Agente-Área'
        verbose_name_plural = 'Agentes-Áreas'
        constraints = [
            models.UniqueConstraint(
                fields=['agente', 'area'],
                name='uq_agente_area',
            )
        ]
        indexes = [
            models.Index(fields=['agente'], name='idx_agente_area_id_agente'),
        ]

    def __str__(self):
        return f'{self.agente} → {self.area}'


class AgenteHorario(models.Model):
    agente = models.ForeignKey(
        Agente,
        on_delete=models.PROTECT,
        related_name='agente_horarios',
        db_column='id_agente',
    )
    horario = models.ForeignKey(
        Horario,
        on_delete=models.PROTECT,
        related_name='agente_horarios',
        db_column='id_turno',
    )
    vigente_desde = models.DateField()
    vigente_hasta = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'agente_horario'
        verbose_name = 'Agente-Horario'
        verbose_name_plural = 'Agentes-Horarios'
        indexes = [
            models.Index(fields=['agente'], name='idx_agente_horario_id_agente'),
        ]

    def __str__(self):
        return f'{self.agente} — {self.horario} (desde {self.vigente_desde})'

    def clean(self):
        if (
            self.vigente_hasta is not None
            and self.vigente_desde > self.vigente_hasta
        ):
            raise ValidationError(
                'vigente_desde no puede ser posterior a vigente_hasta.'
            )