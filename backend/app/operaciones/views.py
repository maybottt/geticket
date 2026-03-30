from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import get_object_or_404

from .models import Area, Horario, CanalEntrada, AgenteArea, AgenteHorario
from .serializers import (
    AreaSerializer, HorarioSerializer, CanalEntradaSerializer,
    AgenteAreaSerializer, AgenteHorarioSerializer,
)


# ──────────────────────────────────────────
# Área
# ──────────────────────────────────────────

class AreaListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        qs = Area.objects.exclude(estado='eliminado')
        return Response(AreaSerializer(qs, many=True).data)

    def post(self, request):
        serializer = AreaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AreaDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(Area, pk=pk)

    def get(self, request, pk):
        return Response(AreaSerializer(self.get_object(pk)).data)

    def patch(self, request, pk):
        serializer = AreaSerializer(
            self.get_object(pk), data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        area        = self.get_object(pk)
        area.estado = 'eliminado'
        area.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ──────────────────────────────────────────
# Horario
# ──────────────────────────────────────────

class HorarioListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response(HorarioSerializer(Horario.objects.all(), many=True).data)

    def post(self, request):
        serializer = HorarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class HorarioDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(Horario, pk=pk)

    def get(self, request, pk):
        return Response(HorarioSerializer(self.get_object(pk)).data)

    def patch(self, request, pk):
        serializer = HorarioSerializer(
            self.get_object(pk), data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        self.get_object(pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ──────────────────────────────────────────
# Canal de entrada
# ──────────────────────────────────────────

class CanalEntradaListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        qs = CanalEntrada.objects.exclude(estado='eliminado')
        return Response(CanalEntradaSerializer(qs, many=True).data)

    def post(self, request):
        serializer = CanalEntradaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CanalEntradaDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(CanalEntrada, pk=pk)

    def get(self, request, pk):
        return Response(CanalEntradaSerializer(self.get_object(pk)).data)

    def patch(self, request, pk):
        serializer = CanalEntradaSerializer(
            self.get_object(pk), data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        canal        = self.get_object(pk)
        canal.estado = 'eliminado'
        canal.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ──────────────────────────────────────────
# Agente ↔ Área
# ──────────────────────────────────────────

class AgenteAreaListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        qs = AgenteArea.objects.select_related(
            'agente__usuario', 'area'
        )
        # Filtro opcional: /api/agente-areas/?agente=1
        agente_id = request.query_params.get('agente')
        if agente_id:
            qs = qs.filter(agente_id=agente_id)
        return Response(AgenteAreaSerializer(qs, many=True).data)

    def post(self, request):
        serializer = AgenteAreaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AgenteAreaDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(
            AgenteArea.objects.select_related('agente__usuario', 'area'), pk=pk
        )

    def get(self, request, pk):
        return Response(AgenteAreaSerializer(self.get_object(pk)).data)

    def delete(self, request, pk):
        self.get_object(pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ──────────────────────────────────────────
# Agente ↔ Horario
# ──────────────────────────────────────────

class AgenteHorarioListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        qs = AgenteHorario.objects.select_related(
            'agente__usuario', 'horario'
        )
        agente_id = request.query_params.get('agente')
        if agente_id:
            qs = qs.filter(agente_id=agente_id)
        return Response(AgenteHorarioSerializer(qs, many=True).data)

    def post(self, request):
        serializer = AgenteHorarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AgenteHorarioDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(
            AgenteHorario.objects.select_related('agente__usuario', 'horario'), pk=pk
        )

    def get(self, request, pk):
        return Response(AgenteHorarioSerializer(self.get_object(pk)).data)

    def patch(self, request, pk):
        serializer = AgenteHorarioSerializer(
            self.get_object(pk), data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        self.get_object(pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)