# operaciones/views.py
from rest_framework import viewsets, permissions
from .models import CanalEntrada, Horario, AgenteArea, AgenteHorario
from .serializers import (
    CanalEntradaSerializer,
    HorarioSerializer,
    AgenteAreaSerializer,
    AgenteHorarioSerializer,
)


class CanalEntradaViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CanalEntrada.objects.all()
    serializer_class = CanalEntradaSerializer


class HorarioViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Horario.objects.all()
    serializer_class = HorarioSerializer


class AgenteAreaViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = AgenteArea.objects.all()
    serializer_class = AgenteAreaSerializer


class AgenteHorarioViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = AgenteHorario.objects.all()
    serializer_class = AgenteHorarioSerializer