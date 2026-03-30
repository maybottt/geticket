from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import get_object_or_404

from .models import Institucion, Sistema
from .serializers import (
    InstitucionSerializer, InstitucionWriteSerializer,
    SistemaSerializer, SistemaWriteSerializer,
)


# ──────────────────────────────────────────
# Instituciones
# ──────────────────────────────────────────

class InstitucionListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        qs = Institucion.objects.exclude(estado='eliminado').prefetch_related('sistemas')
        return Response(InstitucionSerializer(qs, many=True).data)

    def post(self, request):
        serializer = InstitucionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        institucion = serializer.save()
        return Response(
            InstitucionSerializer(institucion).data,
            status=status.HTTP_201_CREATED
        )


class InstitucionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(
            Institucion.objects.prefetch_related('sistemas'), pk=pk
        )

    def get(self, request, pk):
        return Response(InstitucionSerializer(self.get_object(pk)).data)

    def patch(self, request, pk):
        institucion = self.get_object(pk)
        serializer  = InstitucionWriteSerializer(
            institucion, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(InstitucionSerializer(institucion).data)

    def delete(self, request, pk):
        institucion         = self.get_object(pk)
        institucion.estado  = 'eliminado'
        institucion.save()
        # Desactiva también sus sistemas
        institucion.sistemas.filter(estado='activo').update(estado='inactivo')
        return Response(status=status.HTTP_204_NO_CONTENT)


# ──────────────────────────────────────────
# Sistemas
# ──────────────────────────────────────────

class SistemaListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        qs = Sistema.objects.exclude(estado='eliminado').select_related('institucion')
        # Filtro opcional por institución: /api/sistemas/?institucion=1
        id_institucion = request.query_params.get('institucion')
        if id_institucion:
            qs = qs.filter(institucion_id=id_institucion)
        return Response(SistemaSerializer(qs, many=True).data)

    def post(self, request):
        serializer = SistemaWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sistema = serializer.save()
        return Response(
            SistemaSerializer(sistema).data,
            status=status.HTTP_201_CREATED
        )


class SistemaDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(
            Sistema.objects.select_related('institucion'), pk=pk
        )

    def get(self, request, pk):
        return Response(SistemaSerializer(self.get_object(pk)).data)

    def patch(self, request, pk):
        sistema    = self.get_object(pk)
        serializer = SistemaWriteSerializer(
            sistema, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(SistemaSerializer(sistema).data)

    def delete(self, request, pk):
        sistema        = self.get_object(pk)
        sistema.estado = 'eliminado'
        sistema.save()
        return Response(status=status.HTTP_204_NO_CONTENT)