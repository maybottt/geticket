from rest_framework import serializers
from .models import Institucion, Sistema, InstitucionSistema


class SistemaSerializer(serializers.ModelSerializer):
    instituciones = serializers.SerializerMethodField()

    class Meta:
        model  = Sistema
        fields = [
            'id', 'nombre', 'version', 'estado', 'created_at', 'updated_at',
            'instituciones',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_instituciones(self, obj):
        # Devuelve una lista simple con id y nombre de las instituciones asociadas
        return list(obj.instituciones.filter(estado='activo').values('id', 'nombre'))


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
    instituciones_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model  = Sistema
        fields = ['nombre', 'version', 'estado', 'instituciones_ids']

    def validate_instituciones_ids(self, value):
        # Verificar que todos los IDs correspondan a instituciones activas
        instituciones = Institucion.objects.filter(id__in=value, estado='activo')
        if len(instituciones) != len(value):
            raise serializers.ValidationError(
                'Uno o más IDs de institución no son válidos o están inactivos.'
            )
        return value

    def create(self, validated_data):
        instituciones_ids = validated_data.pop('instituciones_ids', [])
        sistema = Sistema.objects.create(**validated_data)
        if instituciones_ids:
            sistema.instituciones.set(instituciones_ids)
        return sistema

    def update(self, instance, validated_data):
        instituciones_ids = validated_data.pop('instituciones_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if instituciones_ids is not None:
            instance.instituciones.set(instituciones_ids)
        return instance