from rest_framework import serializers
from .models import Institucion, Sistema


class SistemaSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Sistema
        fields = [
            'id', 'nombre', 'version', 'estado', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InstitucionSerializer(serializers.ModelSerializer):
    sistemas = SistemaSerializer(many=True, read_only=True)

    class Meta:
        model  = Institucion
        fields = [
            'id', 'nombre', 'descripcion', 'direccion',
            'telefono', 'email', 'estado', 'created_at', 'updated_at',
            'sistemas',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InstitucionWriteSerializer(serializers.ModelSerializer):
    """Para crear y actualizar — sin sistemas anidados."""

    class Meta:
        model  = Institucion
        fields = [
            'nombre', 'descripcion', 'direccion',
            'telefono', 'email', 'estado',
        ]


class SistemaWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Sistema
        fields = ['nombre', 'version', 'estado', 'institucion']

    def validate_institucion(self, value):
        if value.estado == 'eliminado':
            raise serializers.ValidationError(
                'No se puede asociar un sistema a una institución eliminada.'
            )
        return value