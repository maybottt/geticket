#from django.db import models

# Create your models here.

from django.db import models
from django.conf import settings


class Solicitud(models.Model):

    cliente    = models.ForeignKey(
        'usuarios.Cliente', on_delete=models.PROTECT,
        db_column='id_cliente', related_name='solicitudes'
    )
    canal      = models.ForeignKey(
        'operaciones.CanalEntrada', on_delete=models.PROTECT,
        db_column='id_canal', related_name='solicitudes'
    )
    sistema    = models.ForeignKey(
        'instituciones.Sistema', on_delete=models.PROTECT,
        db_column='id_sistema', related_name='solicitudes'
    )
    descripcion = models.TextField()
    received_at = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'solicitud'
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'

    def __str__(self):
        return f'Solicitud #{self.pk} — {self.cliente}'


class Adjunto(models.Model):

    solicitud      = models.ForeignKey(
        Solicitud, on_delete=models.CASCADE,
        db_column='id_solicitud', related_name='adjuntos'
    )
    subido_por     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='subido_por', related_name='adjuntos'
    )
    nombre_archivo = models.CharField(max_length=255)
    url_archivo    = models.CharField(max_length=500)
    tamanio_bytes  = models.IntegerField(null=True, blank=True)
    uploaded_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'adjunto'
        verbose_name = 'Adjunto'
        verbose_name_plural = 'Adjuntos'

    def __str__(self):
        return self.nombre_archivo


class Ticket(models.Model):

    ESTADO_CHOICES = [
        ('en_proceso',  'En proceso'),
        ('solucionado', 'Solucionado'),
        ('cerrado',     'Cerrado'),
        ('rechazado',   'Rechazado'),
    ]
    PRIORIDAD_CHOICES = [
        ('bajo',  'Bajo'),
        ('medio', 'Medio'),
        ('alto',  'Alto'),
    ]

    codigo_ticket           = models.CharField(max_length=20, unique=True)
    solicitud               = models.OneToOneField(
        Solicitud, on_delete=models.PROTECT,
        db_column='id_solicitud', related_name='ticket'
    )
    area                    = models.ForeignKey(
        'operaciones.Area', on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='id_area', related_name='tickets'
    )
    agente_asignado         = models.ForeignKey(
        'usuarios.Agente', on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='id_agente_asignado', related_name='tickets_asignados'
    )
    agente_escalado         = models.ForeignKey(
        'usuarios.Agente', on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='id_agente_escalado', related_name='tickets_escalados'
    )
    estado                  = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='en_proceso')
    prioridad               = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='media')
    motivo_escalamiento     = models.CharField(max_length=200, null=True, blank=True)
    fecha_primera_respuesta = models.DateTimeField(null=True, blank=True)
    fecha_solucionado       = models.DateTimeField(null=True, blank=True)
    fecha_cierre            = models.DateTimeField(null=True, blank=True)
    chatbot_enviado         = models.BooleanField(default=False)
    chatbot_resolvio        = models.BooleanField(default=False)
    horas_limite_confirmacion = models.IntegerField(default=72)
    comentario_solucion     = models.CharField(max_length=500, default='')
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_at              = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ticket'
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'

    def __str__(self):
        return self.codigo_ticket


class HistorialTicket(models.Model):

    TIPO_EVENTO_CHOICES = [
        ('TICKET_CREADO',        'Ticket creado'),
        ('AGENTE_ASIGNADO',      'Agente asignado'),
        ('ESTADO_CAMBIADO',      'Estado cambiado'),
        ('COMENTARIO_AGREGADO',  'Comentario agregado'),
        ('CONFIRMACION_CLIENTE', 'Confirmación cliente'),
        ('TICKET_CERRADO',       'Ticket cerrado'),
        ('REASIGNACION',         'Reasignación'),
        ('TICKET_ELIMINADO',     'Ticket eliminado'),
        ('CAMBIO_PRIORIDAD',     'Cambio de prioridad'),
    ]

    ticket      = models.ForeignKey(
        Ticket, on_delete=models.CASCADE,
        db_column='id_ticket', related_name='historial'
    )
    autor       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='id_autor', related_name='historial_tickets'
    )
    tipo_evento = models.CharField(max_length=50, choices=TIPO_EVENTO_CHOICES)
    descripcion = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'historial_ticket'
        verbose_name = 'Historial de ticket'
        verbose_name_plural = 'Historial de tickets'

    def __str__(self):
        return f'{self.ticket} — {self.tipo_evento}'


class Notificacion(models.Model):

    TIPO_CHOICES = [
        ('ASIGNADO',   'Asignado'),
        ('SOLUCIONADO','Solucionado'),
        ('RECHAZADO',  'Rechazado'),
    ]
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('enviado',   'Enviado'),
        ('fallido',   'Fallido'),
    ]

    ticket            = models.ForeignKey(
        Ticket, on_delete=models.CASCADE,
        db_column='id_ticket', related_name='notificaciones'
    )
    destinatario      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        db_column='id_destinatario', related_name='notificaciones'
    )
    tipo_notificacion = models.CharField(max_length=50, choices=TIPO_CHOICES)
    contenido         = models.TextField()
    estado            = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    sent_at           = models.DateTimeField(null=True, blank=True)
    error_log         = models.TextField(null=True, blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notificacion'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f'{self.ticket} → {self.destinatario}'
