# operaciones/serializers.py
from rest_framework import serializers
from .models import CanalEntrada, Horario, AgenteArea, AgenteHorario


class CanalEntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CanalEntrada
        fields = '__all__'
        read_only_fields = ['created_at']


class HorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horario
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AgenteAreaSerializer(serializers.ModelSerializer):
    agente_nombre = serializers.StringRelatedField(source='agente', read_only=True)
    area_nombre   = serializers.StringRelatedField(source='area', read_only=True)

    class Meta:
        model = AgenteArea
        fields = '__all__'
        read_only_fields = ['asignado_en']


class AgenteHorarioSerializer(serializers.ModelSerializer):
    agente_username = serializers.StringRelatedField(source='agente', read_only=True)
    horario_nombre  = serializers.StringRelatedField(source='horario', read_only=True)

    class Meta:
        model = AgenteHorario
        fields = '__all__'

    def validate(self, data):
        desde = data.get('vigente_desde')
        hasta = data.get('vigente_hasta')
        if desde and hasta and desde > hasta:
            raise serializers.ValidationError(
                'vigente_desde no puede ser posterior a vigente_hasta.'
            )
        return data