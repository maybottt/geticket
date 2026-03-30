from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import get_object_or_404

from usuarios.models import Agente, Cliente
from .models import Solicitud, Ticket, HistorialTicket, Notificacion
from .serializers import (
    SolicitudSerializer, SolicitudCreateSerializer,
    TicketSerializer, TicketCreateSerializer,
    TicketAsignarSerializer, TicketEscalarSerializer,
    TicketSolucionarSerializer, TicketRechazarSerializer,
    NotificacionSerializer,
)
from .utils import generar_codigo_ticket, registrar_historial


# ──────────────────────────────────────────
# Permisos helpers
# ──────────────────────────────────────────

def es_admin(user):
    return user.is_admin

def es_agente(user):
    return hasattr(user, 'agente') and user.agente.estado == 'activo'

def es_cliente(user):
    return hasattr(user, 'cliente')


# ──────────────────────────────────────────
# Solicitudes
# ──────────────────────────────────────────

class SolicitudListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if es_admin(request.user):
            qs = Solicitud.objects.all()
        elif es_cliente(request.user):
            qs = Solicitud.objects.filter(cliente=request.user.cliente)
        elif es_agente(request.user):
            qs = Solicitud.objects.filter(
                ticket__agente_asignado=request.user.agente
            )
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(SolicitudSerializer(
            qs.prefetch_related('adjuntos').select_related(
                'cliente__usuario', 'canal', 'sistema'
            ), many=True
        ).data)

    def post(self, request):
        if not (es_admin(request.user) or es_cliente(request.user)):
            return Response(
                {'detail': 'Solo clientes o administradores pueden crear solicitudes.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = TicketCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # Determinar cliente
            if es_cliente(request.user):
                cliente = request.user.cliente
            else:
                # Admin debe enviar cliente_id
                cliente_id = request.data.get('cliente_id')
                if not cliente_id:
                    return Response(
                        {'detail': 'Debes enviar cliente_id.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                cliente = get_object_or_404(Cliente, pk=cliente_id)

            solicitud = Solicitud.objects.create(
                cliente=cliente,
                canal=serializer.validated_data['canal'],
                sistema=serializer.validated_data['sistema'],
                descripcion=serializer.validated_data['descripcion'],
                received_at=serializer.validated_data.get('received_at'),
            )

            ticket = Ticket.objects.create(
                codigo_ticket=generar_codigo_ticket(),
                solicitud=solicitud,
                prioridad=serializer.validated_data.get('prioridad', 'media'),
            )

            registrar_historial(
                ticket=ticket,
                tipo_evento='TICKET_CREADO',
                descripcion=f'Ticket {ticket.codigo_ticket} creado.',
                autor=request.user,
            )

        return Response(
            TicketSerializer(ticket).data,
            status=status.HTTP_201_CREATED
        )


# ──────────────────────────────────────────
# Tickets
# ──────────────────────────────────────────

class TicketListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if es_admin(request.user):
            qs = Ticket.objects.all()
        elif es_agente(request.user):
            qs = Ticket.objects.filter(agente_asignado=request.user.agente)
        elif es_cliente(request.user):
            qs = Ticket.objects.filter(solicitud__cliente=request.user.cliente)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # Filtros opcionales
        estado    = request.query_params.get('estado')
        prioridad = request.query_params.get('prioridad')
        area_id   = request.query_params.get('area')
        if estado:
            qs = qs.filter(estado=estado)
        if prioridad:
            qs = qs.filter(prioridad=prioridad)
        if area_id:
            qs = qs.filter(area_id=area_id)

        return Response(TicketSerializer(
            qs.select_related(
                'solicitud__cliente__usuario',
                'area', 'agente_asignado__usuario',
                'agente_escalado__usuario',
            ).prefetch_related('historial'), many=True
        ).data)


class TicketDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(
            Ticket.objects.select_related(
                'solicitud__cliente__usuario',
                'area', 'agente_asignado__usuario',
                'agente_escalado__usuario',
            ).prefetch_related('historial'), pk=pk
        )

    def get(self, request, pk):
        ticket = self.get_object(pk)
        # Clientes solo ven sus propios tickets
        if es_cliente(request.user):
            if ticket.solicitud.cliente != request.user.cliente:
                return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(TicketSerializer(ticket).data)


# ──────────────────────────────────────────
# Acciones sobre tickets
# ──────────────────────────────────────────

class TicketAsignarView(APIView):
    """Admin asigna un agente al ticket."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not es_admin(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        ticket = get_object_or_404(Ticket, pk=pk)
        if ticket.estado not in ['en_proceso']:
            return Response(
                {'detail': 'Solo se pueden asignar tickets en estado en_proceso.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TicketAsignarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        agente = serializer.validated_data['agente_id']

        with transaction.atomic():
            ticket.agente_asignado = agente
            if not ticket.fecha_primera_respuesta:
                ticket.fecha_primera_respuesta = timezone.now()
            ticket.save()

            registrar_historial(
                ticket=ticket,
                tipo_evento='AGENTE_ASIGNADO',
                descripcion=f'Agente {agente.usuario.nombres} {agente.usuario.apellidos} asignado.',
                autor=request.user,
            )

            Notificacion.objects.create(
                ticket=ticket,
                destinatario=agente.usuario,
                tipo_notificacion='ASIGNADO',
                contenido=f'Se te asignó el ticket {ticket.codigo_ticket}.',
            )

        return Response(TicketSerializer(ticket).data)


class TicketDesasignarView(APIView):
    """Admin desasigna el agente de un ticket."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not es_admin(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        ticket = get_object_or_404(Ticket, pk=pk)
        with transaction.atomic():
            agente_anterior = ticket.agente_asignado
            ticket.agente_asignado = None
            ticket.save()

            registrar_historial(
                ticket=ticket,
                tipo_evento='REASIGNACION',
                descripcion=f'Agente {agente_anterior.usuario.nombres} desasignado.',
                autor=request.user,
            )

        return Response(TicketSerializer(ticket).data)


class TicketAsignarAutomaticoView(APIView):
    """
    Clasificador automático — asigna el agente con menos tickets activos
    en el área correspondiente al sistema de la solicitud.
    Reemplazar esta lógica con sklearn o n8n cuando esté listo.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not es_admin(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        ticket = get_object_or_404(
            Ticket.objects.select_related('solicitud__sistema__institucion'), pk=pk
        )

        from operaciones.models import AgenteArea
        from django.db.models import Count

        # Agentes del área asignada al ticket
        if not ticket.area:
            return Response(
                {'detail': 'El ticket no tiene área asignada.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        agente = (
            AgenteArea.objects
            .filter(area=ticket.area, agente__estado='activo')
            .annotate(tickets_activos=Count(
                'agente__tickets_asignados',
                filter=__import__('django.db.models', fromlist=['Q']).Q(
                    agente__tickets_asignados__estado='en_proceso'
                )
            ))
            .order_by('tickets_activos')
            .select_related('agente__usuario')
            .first()
        )

        if not agente:
            return Response(
                {'detail': 'No hay agentes disponibles en el área del ticket.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            ticket.agente_asignado = agente.agente
            if not ticket.fecha_primera_respuesta:
                ticket.fecha_primera_respuesta = timezone.now()
            ticket.save()

            registrar_historial(
                ticket=ticket,
                tipo_evento='AGENTE_ASIGNADO',
                descripcion=f'Asignado automáticamente a {agente.agente.usuario.nombres} {agente.agente.usuario.apellidos}.',
                autor=request.user,
            )

        return Response(TicketSerializer(ticket).data)


class TicketEscalarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not (es_admin(request.user) or es_agente(request.user)):
            return Response(status=status.HTTP_403_FORBIDDEN)

        ticket = get_object_or_404(Ticket, pk=pk)
        if ticket.estado != 'en_proceso':
            return Response(
                {'detail': 'Solo se pueden escalar tickets en proceso.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TicketEscalarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        agente  = serializer.validated_data['agente_id']
        motivo  = serializer.validated_data['motivo_escalamiento']

        with transaction.atomic():
            ticket.agente_escalado      = agente
            ticket.motivo_escalamiento  = motivo
            ticket.save()

            registrar_historial(
                ticket=ticket,
                tipo_evento='REASIGNACION',
                descripcion=f'Escalado a {agente.usuario.nombres} {agente.usuario.apellidos}. Motivo: {motivo}',
                autor=request.user,
            )

        return Response(TicketSerializer(ticket).data)


class TicketSolucionarView(APIView):
    """Agente marca el ticket como solucionado — queda esperando confirmación."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not (es_admin(request.user) or es_agente(request.user)):
            return Response(status=status.HTTP_403_FORBIDDEN)

        ticket = get_object_or_404(Ticket, pk=pk)
        if ticket.estado != 'en_proceso':
            return Response(
                {'detail': 'Solo se pueden solucionar tickets en proceso.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TicketSolucionarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            ticket.estado               = 'solucionado'
            ticket.comentario_solucion  = serializer.validated_data['comentario_solucion']
            ticket.fecha_solucionado    = timezone.now()
            ticket.save()

            registrar_historial(
                ticket=ticket,
                tipo_evento='ESTADO_CAMBIADO',
                descripcion=f'Marcado como solucionado. {serializer.validated_data["comentario_solucion"]}',
                autor=request.user,
            )

            # Notificar al cliente
            Notificacion.objects.create(
                ticket=ticket,
                destinatario=ticket.solicitud.cliente.usuario,
                tipo_notificacion='SOLUCIONADO',
                contenido=f'Tu ticket {ticket.codigo_ticket} fue marcado como solucionado. Por favor confirma.',
            )

        return Response(TicketSerializer(ticket).data)


class TicketConfirmarView(APIView):
    """Cliente confirma que el ticket fue resuelto → se cierra."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)

        if es_cliente(request.user):
            if ticket.solicitud.cliente != request.user.cliente:
                return Response(status=status.HTTP_403_FORBIDDEN)
        elif not es_admin(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        if ticket.estado != 'solucionado':
            return Response(
                {'detail': 'Solo se pueden confirmar tickets solucionados.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            ticket.estado       = 'cerrado'
            ticket.fecha_cierre = timezone.now()
            ticket.save()

            registrar_historial(
                ticket=ticket,
                tipo_evento='CONFIRMACION_CLIENTE',
                descripcion='Cliente confirmó la solución. Ticket cerrado.',
                autor=request.user,
            )

        return Response(TicketSerializer(ticket).data)


class TicketCerrarView(APIView):
    """Admin cierra el ticket en cualquier momento."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not es_admin(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        ticket = get_object_or_404(Ticket, pk=pk)
        if ticket.estado == 'cerrado':
            return Response(
                {'detail': 'El ticket ya está cerrado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            ticket.estado       = 'cerrado'
            ticket.fecha_cierre = timezone.now()
            ticket.save()

            registrar_historial(
                ticket=ticket,
                tipo_evento='TICKET_CERRADO',
                descripcion='Ticket cerrado por el administrador.',
                autor=request.user,
            )

        return Response(TicketSerializer(ticket).data)


class TicketRechazarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not (es_admin(request.user) or es_agente(request.user)):
            return Response(status=status.HTTP_403_FORBIDDEN)

        ticket = get_object_or_404(Ticket, pk=pk)
        if ticket.estado not in ['en_proceso']:
            return Response(
                {'detail': 'Solo se pueden rechazar tickets en proceso.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TicketRechazarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            ticket.estado = 'rechazado'
            ticket.save()

            registrar_historial(
                ticket=ticket,
                tipo_evento='ESTADO_CAMBIADO',
                descripcion=f'Ticket rechazado. Motivo: {serializer.validated_data["motivo"]}',
                autor=request.user,
            )

            Notificacion.objects.create(
                ticket=ticket,
                destinatario=ticket.solicitud.cliente.usuario,
                tipo_notificacion='RECHAZADO',
                contenido=f'Tu ticket {ticket.codigo_ticket} fue rechazado. Motivo: {serializer.validated_data["motivo"]}',
            )

        return Response(TicketSerializer(ticket).data)


# ──────────────────────────────────────────
# Notificaciones
# ──────────────────────────────────────────

class NotificacionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notificacion.objects.filter(
            destinatario=request.user
        ).order_by('-created_at')
        return Response(NotificacionSerializer(qs, many=True).data)