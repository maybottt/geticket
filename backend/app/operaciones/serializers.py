from rest_framework import serializers
from .models import Area, Horario, CanalEntrada, AgenteArea, AgenteHorario


class AreaSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Area
        fields = ['id', 'nombre', 'estado', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class HorarioSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Horario
        fields = [
            'id', 'nombre', 'hora_inicio', 'hora_fin',
            'lunes', 'martes', 'miercoles', 'jueves',
            'viernes', 'sabado', 'domingo',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        hora_inicio = attrs.get('hora_inicio')
        hora_fin    = attrs.get('hora_fin')
        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise serializers.ValidationError(
                'La hora de inicio debe ser menor a la hora de fin.'
            )
        return attrs


class CanalEntradaSerializer(serializers.ModelSerializer):

    class Meta:
        model  = CanalEntrada
        fields = ['id', 'nombre', 'descripcion', 'estado', 'created_at']
        read_only_fields = ['id', 'created_at']


# ──────────────────────────────────────────
# Agente ↔ Área / Horario
# ──────────────────────────────────────────

class AgenteAreaSerializer(serializers.ModelSerializer):
    agente_nombre = serializers.SerializerMethodField()
    area_nombre   = serializers.CharField(source='area.nombre', read_only=True)

    class Meta:
        model  = AgenteArea
        fields = ['id', 'agente', 'area', 'agente_nombre', 'area_nombre', 'asignado_en']
        read_only_fields = ['id', 'asignado_en']

    def get_agente_nombre(self, obj):
        u = obj.agente.usuario
        return f'{u.nombres} {u.apellidos}'

    def validate(self, attrs):
        if AgenteArea.objects.filter(
            agente=attrs['agente'], area=attrs['area']
        ).exists():
            raise serializers.ValidationError(
                'El agente ya está asignado a esta área.'
            )
        return attrs


class AgenteHorarioSerializer(serializers.ModelSerializer):
    agente_nombre  = serializers.SerializerMethodField()
    horario_nombre = serializers.CharField(source='horario.nombre', read_only=True)

    class Meta:
        model  = AgenteHorario
        fields = [
            'id', 'agente', 'horario', 'agente_nombre', 'horario_nombre',
            'vigente_desde', 'vigente_hasta',
        ]
        read_only_fields = ['id']

    def get_agente_nombre(self, obj):
        u = obj.agente.usuario
        return f'{u.nombres} {u.apellidos}'

    def validate(self, attrs):
        vigente_desde = attrs.get('vigente_desde')
        vigente_hasta = attrs.get('vigente_hasta')
        if vigente_desde and vigente_hasta and vigente_desde > vigente_hasta:
            raise serializers.ValidationError(
                'La fecha de inicio debe ser menor a la fecha de fin.'
            )
        return attrs