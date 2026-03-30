from django.db import transaction


def generar_codigo_ticket():
    """Genera el código GT-XXXX con el siguiente número disponible."""
    from .models import Ticket
    with transaction.atomic():
        ultimo = (
            Ticket.objects.select_for_update()
            .order_by('-id')
            .first()
        )
        siguiente = (ultimo.id + 1) if ultimo else 1
        return f'GT-{siguiente:04d}'


def registrar_historial(ticket, tipo_evento, descripcion, autor=None):
    """Registra un evento en el historial del ticket."""
    from .models import HistorialTicket
    HistorialTicket.objects.create(
        ticket=ticket,
        tipo_evento=tipo_evento,
        descripcion=descripcion,
        autor=autor,
    )