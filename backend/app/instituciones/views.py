# instituciones/views.py
from rest_framework import viewsets, permissions
from .models import Institucion, Sistema, InstitucionSistema, Area
from .serializers import (
    InstitucionSerializer,
    SistemaSerializer,
    InstitucionSistemaSerializer,
    AreaSerializer,
)


class InstitucionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Institucion.objects.all()
    serializer_class = InstitucionSerializer


class SistemaViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Sistema.objects.all()
    serializer_class = SistemaSerializer


class InstitucionSistemaViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = InstitucionSistema.objects.all()
    serializer_class = InstitucionSistemaSerializer


class AreaViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Area.objects.all()
    serializer_class = AreaSerializer