# tickets/serializers.py
from rest_framework import serializers
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import (
    CategoriaIncidencia,
    Ticket,
    Adjunto,
    HistorialTicket,
    Notificacion,
    SatisfaccionTicket,
)
from usuarios.models import Agente, Cliente, Usuario
from operaciones.models import CanalEntrada
from instituciones.models import Area, Sistema


# ---------------------------------------------------------------------------
# Categoría de incidencia
# ---------------------------------------------------------------------------
class CategoriaIncidenciaSerializer(serializers.ModelSerializer):
    area_nombre = serializers.StringRelatedField(source='area', read_only=True)

    class Meta:
        model = CategoriaIncidencia
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# ---------------------------------------------------------------------------
# Ticket
# ---------------------------------------------------------------------------
class TicketSerializer(serializers.ModelSerializer):
    # Relaciones de escritura mediante IDs
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    canal   = serializers.PrimaryKeyRelatedField(queryset=CanalEntrada.objects.all())
    sistema = serializers.PrimaryKeyRelatedField(queryset=Sistema.objects.all())
    categoria = serializers.PrimaryKeyRelatedField(queryset=CategoriaIncidencia.objects.all(), allow_null=True, required=False)
    area = serializers.PrimaryKeyRelatedField(queryset=Area.objects.all(), allow_null=True, required=False)
    agente_asignado = serializers.PrimaryKeyRelatedField(queryset=Agente.objects.all(), allow_null=True, required=False)
    agente_escalado = serializers.PrimaryKeyRelatedField(queryset=Agente.objects.all(), allow_null=True, required=False)

    # Campos de solo lectura para visualización
    cliente_nombre = serializers.StringRelatedField(source='cliente', read_only=True)
    canal_nombre   = serializers.StringRelatedField(source='canal', read_only=True)
    sistema_nombre = serializers.StringRelatedField(source='sistema', read_only=True)
    categoria_nombre = serializers.StringRelatedField(source='categoria', read_only=True)
    area_nombre = serializers.StringRelatedField(source='area', read_only=True)
    agente_asignado_nombre = serializers.StringRelatedField(source='agente_asignado', read_only=True)
    agente_escalado_nombre = serializers.StringRelatedField(source='agente_escalado', read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = [
            'codigo_ticket',           # normalmente se genera automáticamente
            'fecha_asignacion',        # se asigna en el servidor
            'created_at',
            'updated_at',
        ]

    def validate(self, data):
        # Validación de escalamiento (cláusula CHECK)
        if data.get('agente_escalado') and not data.get('motivo_escalamiento'):
            raise serializers.ValidationError(
                'Debe indicar el motivo de escalamiento cuando se asigna un agente escalado.'
            )
        return data

    def create(self, validated_data):
        # Si al crear ya viene un agente asignado, establecemos fecha_asignacion
        if validated_data.get('agente_asignado') and not validated_data.get('fecha_asignacion'):
            validated_data['fecha_asignacion'] = timezone.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Si el agente pasa de NULL a un valor concreto y no hay fecha_asignacion, la establecemos
        if instance.agente_asignado is None and validated_data.get('agente_asignado') is not None:
            validated_data['fecha_asignacion'] = timezone.now()
        return super().update(instance, validated_data)


# ---------------------------------------------------------------------------
# Adjunto
# ---------------------------------------------------------------------------
class AdjuntoSerializer(serializers.ModelSerializer):
    subido_por_nombre = serializers.StringRelatedField(source='subido_por', read_only=True)

    class Meta:
        model = Adjunto
        fields = '__all__'
        read_only_fields = ['uploaded_at']

    def validate_tamanio_bytes(self, value):
        if value is not None and value > Adjunto.TAMANIO_MAXIMO_BYTES:
            raise serializers.ValidationError(
                f'El archivo no puede superar {Adjunto.TAMANIO_MAXIMO_BYTES} bytes (10 MB).'
            )
        return value


# ---------------------------------------------------------------------------
# HistorialTicket
# ---------------------------------------------------------------------------
class HistorialTicketSerializer(serializers.ModelSerializer):
    autor_nombre = serializers.StringRelatedField(source='autor', read_only=True)

    class Meta:
        model = HistorialTicket
        fields = '__all__'
        read_only_fields = ['created_at']


# ---------------------------------------------------------------------------
# Notificación
# ---------------------------------------------------------------------------
class NotificacionSerializer(serializers.ModelSerializer):
    destinatario_nombre = serializers.StringRelatedField(source='destinatario', read_only=True)

    class Meta:
        model = Notificacion
        fields = '__all__'
        read_only_fields = ['created_at']


# ---------------------------------------------------------------------------
# SatisfacciónTicket
# ---------------------------------------------------------------------------
class SatisfaccionTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SatisfaccionTicket
        fields = '__all__'
        read_only_fields = ['enviado_en']

    def validate_puntuacion(self, value):
        if value is not None and not (1 <= value <= 5):
            raise serializers.ValidationError('La puntuación debe estar entre 1 y 5.')
        return value

    def validate(self, data):
        respondido = data.get('respondido_en')
        enviado = self.instance.enviado_en if self.instance else data.get('enviado_en')
        if respondido and enviado and respondido < enviado:
            raise serializers.ValidationError('respondido_en no puede ser anterior a enviado_en.')
        return data