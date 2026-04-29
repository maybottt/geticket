# tickets/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.utils import timezone

from .models import (
    CategoriaIncidencia,
    Ticket,
    Adjunto,
    HistorialTicket,
    Notificacion,
    SatisfaccionTicket,
)
from .serializers import (
    CategoriaIncidenciaSerializer,
    TicketSerializer,
    AdjuntoSerializer,
    HistorialTicketSerializer,
    NotificacionSerializer,
    SatisfaccionTicketSerializer,
)
from usuarios.permissions import EsAdministrador, EsAgente, EsCliente, EsPropietarioOAdmin


class CategoriaIncidenciaViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CategoriaIncidencia.objects.all()
    serializer_class = CategoriaIncidenciaSerializer


class TicketViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TicketSerializer

    def get_queryset(self):
        user = self.request.user
        from usuarios.serializers import get_rol
        rol = get_rol(user)
        if rol == 'administrador':
            return Ticket.objects.all()
        elif rol == 'agente':
            # Agente ve tickets asignados a él o tickets de su área (opcional)
            # Aquí simplificamos: asignados o escalados a él.
            return Ticket.objects.filter(
                models.Q(agente_asignado__usuario=user) | models.Q(agente_escalado__usuario=user)
            )
        elif rol == 'cliente':
            # Cliente ve sus propios tickets
            from usuarios.models import Cliente
            try:
                cliente = user.perfil_cliente
            except Cliente.DoesNotExist:
                return Ticket.objects.none()
            return Ticket.objects.filter(cliente=cliente)
        return Ticket.objects.none()

    def perform_create(self, serializer):
        # Al crear un ticket desde cualquier rol, pero aseguramos que el cliente sea correcto
        user = self.request.user
        from usuarios.serializers import get_rol
        rol = get_rol(user)
        if rol == 'cliente':
            # Forzar que el ticket se asocie al cliente autenticado
            cliente = user.perfil_cliente
            serializer.save(cliente=cliente)
        else:
            # Admin o agente crean con el cliente que seleccionen
            serializer.save()

    def update(self, request, *args, **kwargs):
        # Añadir lógica para registro en historial cuando cambien ciertos campos
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Podrías comparar campos anteriores para detectar cambios:
        old_estado = instance.estado
        new_estado = serializer.validated_data.get('estado', old_estado)
        old_agente = instance.agente_asignado
        new_agente = serializer.validated_data.get('agente_asignado', old_agente)

        # Realizar la actualización
        self.perform_update(serializer)

        # Generar entradas de historial (simplificado)
        if new_estado != old_estado:
            HistorialTicket.objects.create(
                ticket=instance,
                autor=request.user,
                tipo_evento='ESTADO_CAMBIADO',
                descripcion=f'Estado cambiado de {old_estado} a {new_estado}'
            )
        if new_agente != old_agente:
            HistorialTicket.objects.create(
                ticket=instance,
                autor=request.user,
                tipo_evento='REASIGNACION',
                descripcion=f'Agente reasignado de {old_agente} a {new_agente}'
            )

        return Response(serializer.data)


class AdjuntoViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Adjunto.objects.all()
    serializer_class = AdjuntoSerializer


class HistorialTicketViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = HistorialTicket.objects.all()
    serializer_class = HistorialTicketSerializer


class NotificacionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer


class SatisfaccionTicketViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = SatisfaccionTicket.objects.all()
    serializer_class = SatisfaccionTicketSerializer