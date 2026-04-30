# instituciones/serializers.py
from rest_framework import serializers
from .models import Institucion, Sistema, InstitucionSistema, Area


class InstitucionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institucion
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class SistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sistema
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class InstitucionSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitucionSistema
        fields = '__all__'


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']