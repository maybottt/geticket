# tickets/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from instituciones.models import Area, Sistema
from usuarios.models import Agente, Cliente, Usuario
from operaciones.models import CanalEntrada


# ---------------------------------------------------------------------------
# Modelos de configuración de tickets
# ---------------------------------------------------------------------------

class CategoriaIncidencia(models.Model):
    class Estado(models.TextChoices):
        ACTIVO    = 'activo',    'Activo'
        INACTIVO  = 'inactivo',  'Inactivo'
        ELIMINADO = 'eliminado', 'Eliminado'

    nombre      = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    area        = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='categorias',
        db_column='id_area',
    )
    estado      = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.ACTIVO
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categoria_incidencia'
        verbose_name = 'Categoría de incidencia'
        verbose_name_plural = 'Categorías de incidencia'
        indexes = [
            models.Index(fields=['area'], name='idx_categoria_id_area'),
        ]

    def __str__(self):
        return self.nombre


# ---------------------------------------------------------------------------
# Modelo principal: Ticket
# ---------------------------------------------------------------------------

class Ticket(models.Model):
    class Estado(models.TextChoices):
        EN_PROCESO  = 'en_proceso',  'En proceso'
        SOLUCIONADO = 'solucionado', 'Solucionado'
        CERRADO     = 'cerrado',     'Cerrado'
        RECHAZADO   = 'rechazado',   'Rechazado'
        ESCALADO    = 'escalado',    'Escalado'

    class Prioridad(models.TextChoices):
        BAJO  = 'bajo',  'Bajo'
        MEDIO = 'medio', 'Medio'
        ALTO  = 'alto',  'Alto'

    codigo_ticket = models.CharField(max_length=20, unique=True)

    cliente   = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='tickets',
        db_column='id_cliente',
    )
    canal     = models.ForeignKey(
        CanalEntrada,
        on_delete=models.PROTECT,
        related_name='tickets',
        db_column='id_canal',
    )
    sistema   = models.ForeignKey(
        Sistema,
        on_delete=models.PROTECT,
        related_name='tickets',
        db_column='id_sistema',
    )
    categoria = models.ForeignKey(
        CategoriaIncidencia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        db_column='id_categoria',
    )
    area      = models.ForeignKey(
        Area,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        db_column='id_area',
    )

    agente_asignado = models.ForeignKey(
        Agente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_asignados',
        db_column='id_agente_asignado',
    )
    agente_escalado = models.ForeignKey(
        Agente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_escalados',
        db_column='id_agente_escalado',
    )

    descripcion          = models.TextField()
    comentario_solucion  = models.TextField(default='', blank=True)
    motivo_escalamiento  = models.CharField(max_length=200, null=True, blank=True)

    estado    = models.CharField(
        max_length=15, choices=Estado.choices, default=Estado.EN_PROCESO
    )
    prioridad = models.CharField(
        max_length=20, choices=Prioridad.choices, default=Prioridad.MEDIO
    )

    received_at              = models.DateTimeField(null=True, blank=True)
    fecha_asignacion         = models.DateTimeField(null=True, blank=True)
    fecha_primera_respuesta  = models.DateTimeField(null=True, blank=True)
    fecha_solucionado        = models.DateTimeField(null=True, blank=True)
    fecha_cierre             = models.DateTimeField(null=True, blank=True)

    chatbot_enviado   = models.BooleanField(default=False)
    chatbot_resolvio  = models.BooleanField(default=False)

    horas_limite_confirmacion = models.IntegerField(default=72)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ticket'
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        indexes = [
            models.Index(fields=['cliente'],         name='idx_ticket_id_cliente'),
            models.Index(fields=['canal'],           name='idx_ticket_id_canal'),
            models.Index(fields=['sistema'],         name='idx_ticket_id_sistema'),
            models.Index(fields=['categoria'],       name='idx_ticket_id_categoria'),
            models.Index(fields=['area'],            name='idx_ticket_id_area'),
            models.Index(fields=['agente_asignado'], name='idx_ticket_id_agente_asignado'),
            models.Index(fields=['estado'],          name='idx_ticket_estado'),
            models.Index(fields=['prioridad'],       name='idx_ticket_prioridad'),
            models.Index(fields=['created_at'],      name='idx_ticket_created_at'),
        ]

    def __str__(self):
        return f'[{self.codigo_ticket}] {self.get_estado_display()}'

    def clean(self):
        if self.agente_escalado_id is not None and not self.motivo_escalamiento:
            raise ValidationError(
                'Se debe indicar el motivo de escalamiento cuando se asigna '
                'un agente escalado.'
            )

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.agente_asignado_id is not None and self.fecha_asignacion is None:
                self.fecha_asignacion = timezone.now()
        else:
            try:
                original = Ticket.objects.get(pk=self.pk)
                if (
                    original.agente_asignado_id is None
                    and self.agente_asignado_id is not None
                    and self.fecha_asignacion is None
                ):
                    self.fecha_asignacion = timezone.now()
            except Ticket.DoesNotExist:
                pass

        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Modelos auxiliares del ticket
# ---------------------------------------------------------------------------

class Adjunto(models.Model):
    TAMANIO_MAXIMO_BYTES = 10_485_760  # 10 MB

    ticket         = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='adjuntos',
        db_column='id_ticket',
    )
    subido_por     = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='adjuntos_subidos',
        db_column='subido_por',
    )
    nombre_archivo = models.CharField(max_length=255)
    url_archivo    = models.CharField(max_length=500)
    tamanio_bytes  = models.IntegerField(null=True, blank=True)
    uploaded_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'adjunto'
        verbose_name = 'Adjunto'
        verbose_name_plural = 'Adjuntos'
        indexes = [
            models.Index(fields=['ticket'], name='idx_adjunto_id_ticket'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(tamanio_bytes__isnull=True)
                    | models.Q(tamanio_bytes__lte=10_485_760)
                ),
                name='chk_adjunto_tamanio',
            )
        ]

    def __str__(self):
        return self.nombre_archivo

    def clean(self):
        if (
            self.tamanio_bytes is not None
            and self.tamanio_bytes > self.TAMANIO_MAXIMO_BYTES
        ):
            raise ValidationError(
                f'El archivo no puede superar {self.TAMANIO_MAXIMO_BYTES} bytes (10 MB).'
            )


class HistorialTicket(models.Model):
    class TipoEvento(models.TextChoices):
        TICKET_CREADO         = 'TICKET_CREADO',         'Ticket creado'
        AGENTE_ASIGNADO       = 'AGENTE_ASIGNADO',       'Agente asignado'
        ESTADO_CAMBIADO       = 'ESTADO_CAMBIADO',       'Estado cambiado'
        COMENTARIO_AGREGADO   = 'COMENTARIO_AGREGADO',   'Comentario agregado'
        CONFIRMACION_CLIENTE  = 'CONFIRMACION_CLIENTE',  'Confirmación del cliente'
        TICKET_CERRADO        = 'TICKET_CERRADO',        'Ticket cerrado'
        REASIGNACION          = 'REASIGNACION',          'Reasignación'
        TICKET_ELIMINADO      = 'TICKET_ELIMINADO',      'Ticket eliminado'
        CAMBIO_PRIORIDAD      = 'CAMBIO_PRIORIDAD',      'Cambio de prioridad'

    ticket      = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='historial',
        db_column='id_ticket',
    )
    autor       = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos_generados',
        db_column='id_autor',
    )
    tipo_evento = models.CharField(max_length=50, choices=TipoEvento.choices)
    descripcion = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'historial_ticket'
        verbose_name = 'Historial de ticket'
        verbose_name_plural = 'Historial de tickets'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['ticket'],      name='idx_historial_id_ticket'),
            models.Index(fields=['tipo_evento'], name='idx_historial_tipo_evento'),
        ]

    def __str__(self):
        return f'{self.ticket.codigo_ticket} — {self.get_tipo_evento_display()}'


class Notificacion(models.Model):
    class TipoNotificacion(models.TextChoices):
        ASIGNADO    = 'ASIGNADO',    'Asignado'
        SOLUCIONADO = 'SOLUCIONADO', 'Solucionado'
        RECHAZADO   = 'RECHAZADO',   'Rechazado'

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        ENVIADO   = 'enviado',   'Enviado'
        FALLIDO   = 'fallido',   'Fallido'

    ticket            = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        db_column='id_ticket',
    )
    destinatario      = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        db_column='id_destinatario',
    )
    tipo_notificacion = models.CharField(
        max_length=50, choices=TipoNotificacion.choices
    )
    contenido   = models.TextField()
    estado      = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )
    sent_at     = models.DateTimeField(null=True, blank=True)
    error_log   = models.TextField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notificacion'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        indexes = [
            models.Index(fields=['ticket'],       name='idx_notificacion_id_ticket'),
            models.Index(fields=['destinatario'], name='idx_notif_destinatario'),
            models.Index(fields=['estado'],       name='idx_notificacion_estado'),
        ]

    def __str__(self):
        return f'Notif. {self.get_tipo_notificacion_display()} → {self.destinatario.username}'


class SatisfaccionTicket(models.Model):
    ticket        = models.OneToOneField(
        Ticket,
        on_delete=models.CASCADE,
        related_name='satisfaccion',
        db_column='id_ticket',
    )
    puntuacion    = models.SmallIntegerField(null=True, blank=True)
    comentario    = models.TextField(null=True, blank=True)
    enviado_en    = models.DateTimeField(auto_now_add=True)
    respondido_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'satisfaccion_ticket'
        verbose_name = 'Satisfacción de ticket'
        verbose_name_plural = 'Satisfacciones de tickets'
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(puntuacion__isnull=True)
                    | models.Q(puntuacion__gte=1, puntuacion__lte=5)
                ),
                name='chk_satisfaccion_puntuacion',
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(respondido_en__isnull=True)
                    | models.Q(respondido_en__gte=models.F('enviado_en'))
                ),
                name='chk_satisfaccion_fechas',
            ),
        ]
        indexes = [
            models.Index(fields=['ticket'], name='idx_satisfaccion_id_ticket'),
            models.Index(
                fields=['respondido_en'],
                name='idx_satisfaccion_respondido',
                condition=models.Q(respondido_en__isnull=False),
            ),
            models.Index(
                fields=['puntuacion'],
                name='idx_satisfaccion_puntuacion',
                condition=models.Q(puntuacion__isnull=False),
            ),
        ]

    def __str__(self):
        return f'CSAT ticket {self.ticket.codigo_ticket} — {self.puntuacion or "sin respuesta"}'

    def clean(self):
        if self.puntuacion is not None and not (1 <= self.puntuacion <= 5):
            raise ValidationError('La puntuación debe estar entre 1 y 5.')
        if (
            self.respondido_en is not None
            and self.enviado_en is not None
            and self.respondido_en < self.enviado_en
        ):
            raise ValidationError('respondido_en no puede ser anterior a enviado_en.')