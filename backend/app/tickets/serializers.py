from rest_framework import serializers
from .models import Solicitud, Adjunto, Ticket, HistorialTicket, Notificacion


class AdjuntoSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Adjunto
        fields = [
            'id', 'nombre_archivo', 'url_archivo',
            'tamanio_bytes', 'uploaded_at', 'subido_por',
        ]
        read_only_fields = ['id', 'uploaded_at']


class SolicitudSerializer(serializers.ModelSerializer):
    adjuntos = AdjuntoSerializer(many=True, read_only=True)

    class Meta:
        model  = Solicitud
        fields = [
            'id', 'cliente', 'canal', 'sistema',
            'descripcion', 'received_at', 'created_at',
            'adjuntos',
        ]
        read_only_fields = ['id', 'created_at']


class SolicitudCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Solicitud
        fields = ['cliente', 'canal', 'sistema', 'descripcion', 'received_at']

    def validate_cliente(self, value):
        if not value.usuario.is_active:
            raise serializers.ValidationError('El cliente no está activo.')
        return value

    def validate_sistema(self, value):
        if value.estado != 'activo':
            raise serializers.ValidationError('El sistema no está activo.')
        return value


class HistorialTicketSerializer(serializers.ModelSerializer):
    autor_nombre = serializers.SerializerMethodField()

    class Meta:
        model  = HistorialTicket
        fields = ['id', 'tipo_evento', 'descripcion', 'autor', 'autor_nombre', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_autor_nombre(self, obj):
        if obj.autor:
            return f'{obj.autor.nombres} {obj.autor.apellidos}'
        return 'Sistema'


class TicketSerializer(serializers.ModelSerializer):
    historial  = HistorialTicketSerializer(many=True, read_only=True)
    solicitud  = SolicitudSerializer(read_only=True)
    area_nombre            = serializers.CharField(source='area.nombre', read_only=True)
    agente_asignado_nombre = serializers.SerializerMethodField()
    agente_escalado_nombre = serializers.SerializerMethodField()

    class Meta:
        model  = Ticket
        fields = [
            'id', 'codigo_ticket', 'solicitud',
            'area', 'area_nombre',
            'agente_asignado', 'agente_asignado_nombre',
            'agente_escalado', 'agente_escalado_nombre',
            'estado', 'prioridad',
            'motivo_escalamiento',
            'fecha_primera_respuesta', 'fecha_solucionado', 'fecha_cierre',
            'chatbot_enviado', 'chatbot_resolvio',
            'horas_limite_confirmacion', 'comentario_solucion',
            'created_at', 'updated_at',
            'historial',
        ]
        read_only_fields = [
            'id', 'codigo_ticket', 'created_at', 'updated_at',
            'fecha_primera_respuesta', 'fecha_solucionado', 'fecha_cierre',
        ]

    def get_agente_asignado_nombre(self, obj):
        if obj.agente_asignado:
            u = obj.agente_asignado.usuario
            return f'{u.nombres} {u.apellidos}'
        return None

    def get_agente_escalado_nombre(self, obj):
        if obj.agente_escalado:
            u = obj.agente_escalado.usuario
            return f'{u.nombres} {u.apellidos}'
        return None


class TicketCreateSerializer(serializers.Serializer):
    """Crea solicitud + ticket en una sola operación."""
    canal       = serializers.IntegerField()
    sistema     = serializers.IntegerField()
    descripcion = serializers.CharField()
    prioridad   = serializers.ChoiceField(
        choices=['baja', 'media', 'alta'], default='media'
    )
    received_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate_canal(self, value):
        from operaciones.models import CanalEntrada
        try:
            canal = CanalEntrada.objects.get(pk=value, estado='activo')
        except CanalEntrada.DoesNotExist:
            raise serializers.ValidationError('Canal no encontrado o inactivo.')
        return canal

    def validate_sistema(self, value):
        from instituciones.models import Sistema
        try:
            sistema = Sistema.objects.get(pk=value, estado='activo')
        except Sistema.DoesNotExist:
            raise serializers.ValidationError('Sistema no encontrado o inactivo.')
        return sistema


class TicketAsignarSerializer(serializers.Serializer):
    agente_id = serializers.IntegerField()

    def validate_agente_id(self, value):
        from usuarios.models import Agente
        try:
            agente = Agente.objects.get(pk=value, estado='activo')
        except Agente.DoesNotExist:
            raise serializers.ValidationError('Agente no encontrado o inactivo.')
        return agente


class TicketEscalarSerializer(serializers.Serializer):
    agente_id           = serializers.IntegerField()
    motivo_escalamiento = serializers.CharField(max_length=200)

    def validate_agente_id(self, value):
        from usuarios.models import Agente
        try:
            agente = Agente.objects.get(pk=value, estado='activo')
        except Agente.DoesNotExist:
            raise serializers.ValidationError('Agente no encontrado o inactivo.')
        return agente


class TicketSolucionarSerializer(serializers.Serializer):
    comentario_solucion = serializers.CharField(max_length=500)


class TicketRechazarSerializer(serializers.Serializer):
    motivo = serializers.CharField(max_length=200)


class NotificacionSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Notificacion
        fields = [
            'id', 'ticket', 'destinatario', 'tipo_notificacion',
            'contenido', 'estado', 'sent_at', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']