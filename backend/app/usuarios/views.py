from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import get_object_or_404
from django.db import transaction
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.decorators import action

from .models import Usuario, Agente, Cliente
from .serializers import (
    LoginSerializer, ElegirRolSerializer, SwitchRolSerializer,
    UsuarioSerializer, UsuarioUpdateSerializer, PasswordChangeSerializer,
    AgenteSerializer, AgenteCreateSerializer,
    ClienteSerializer, ClienteCreateSerializer,
    get_roles, get_token_para_rol,UsuarioConRolesSerializer, 
)


# ──────────────────────────────────────────
# Auth
# ──────────────────────────────────────────

class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user  = serializer.validated_data['user']
        roles = serializer.validated_data['roles']

        # Un solo rol → token inmediato
        if len(roles) == 1:
            refresh = get_token_para_rol(user, roles[0])
            return Response({
                'access':     str(refresh.access_token),
                'refresh':    str(refresh),
                'rol_activo': roles[0],
                'roles':      roles,
                'user':       UsuarioSerializer(user).data,
            })

        # Múltiples roles → que elija
        return Response({
            'seleccionar_rol': True,
            'user_id':         user.pk,
            'roles':           roles,
            'user':            UsuarioSerializer(user).data,
        }, status=status.HTTP_200_OK)


class ElegirRolView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ElegirRolSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user  = serializer.validated_data['user']
        rol   = serializer.validated_data['rol']
        roles = serializer.validated_data['roles']

        refresh = get_token_para_rol(user, rol)
        return Response({
            'access':     str(refresh.access_token),
            'refresh':    str(refresh),
            'rol_activo': rol,
            'roles':      roles,
            'user':       UsuarioSerializer(user).data,
        })


class SwitchRolView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SwitchRolSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        rol     = serializer.validated_data['rol']
        roles   = get_roles(request.user)
        refresh = get_token_para_rol(request.user, rol)

        return Response({
            'access':     str(refresh.access_token),
            'refresh':    str(refresh),
            'rol_activo': rol,
            'roles':      roles,
        })


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = UsuarioSerializer(request.user).data
        data['roles']      = get_roles(request.user)
        data['rol_activo'] = request.auth.get('rol_activo') if request.auth else None
        return Response(data)

    def patch(self, request):
        serializer = UsuarioUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['password_nuevo'])
        request.user.save()
        return Response({'detail': 'Contraseña actualizada correctamente.'})


# ──────────────────────────────────────────
# Agentes
# ──────────────────────────────────────────

class AgenteListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        agentes = Agente.objects.select_related('usuario').all()
        return Response(AgenteSerializer(agentes, many=True).data)

    def post(self, request):
        serializer = AgenteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        agente = serializer.save()
        return Response(AgenteSerializer(agente).data, status=status.HTTP_201_CREATED)


class AgenteDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(Agente.objects.select_related('usuario'), pk=pk)

    def get(self, request, pk):
        return Response(AgenteSerializer(self.get_object(pk)).data)

    def patch(self, request, pk):
        agente = self.get_object(pk)
        serializer = UsuarioUpdateSerializer(
            agente.usuario, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if 'estado' in request.data:
            agente.estado = request.data['estado']
            agente.save()
        return Response(AgenteSerializer(agente).data)

    def delete(self, request, pk):
        agente = self.get_object(pk)
        agente.estado = 'eliminado'
        agente.save()
        agente.usuario.is_active = False
        agente.usuario.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ──────────────────────────────────────────
# Clientes
# ──────────────────────────────────────────

class ClienteListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        clientes = Cliente.objects.select_related('usuario', 'institucion').all()
        return Response(ClienteSerializer(clientes, many=True).data)

    def post(self, request):
        serializer = ClienteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cliente = serializer.save()
        return Response(ClienteSerializer(cliente).data, status=status.HTTP_201_CREATED)


class ClienteDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(
            Cliente.objects.select_related('usuario', 'institucion'), pk=pk
        )

    def get(self, request, pk):
        return Response(ClienteSerializer(self.get_object(pk)).data)

    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        if cliente.estado == 'activo':
            cliente.estado = 'inactivo'
            msg = f'Cliente {cliente.usuario.username} desactivado.'
        else:
            cliente.estado = 'activo'
            msg = f'Cliente {cliente.usuario.username} activado.'
        cliente.save()
        return Response({'detail': msg})

    def patch(self, request, pk):
        cliente = self.get_object(pk)
        serializer = UsuarioUpdateSerializer(
            cliente.usuario, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if 'rol_institucion' in request.data:
            cliente.rol_institucion = request.data['rol_institucion']
            cliente.save()
        return Response(ClienteSerializer(cliente).data)

    def delete(self, request, pk):
        cliente = self.get_object(pk)
        cliente.estado = 'eliminado'
        cliente.save()
        cliente.usuario.is_active = False
        cliente.usuario.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RegistroClienteView(APIView):
    permission_classes = []  # público, no requiere token

    def post(self, request):
        from instituciones.models import Institucion
        from .serializers import ClienteCreateSerializer

        # El cliente se registra con is_active=False
        # El admin lo aprueba después cambiándolo a True
        data = request.data.copy()

        # Validaciones básicas
        if not data.get('username'):
            return Response({'detail': 'El username es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
        if not data.get('email'):
            return Response({'detail': 'El email es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
        if not data.get('password'):
            return Response({'detail': 'La contraseña es obligatoria.'}, status=status.HTTP_400_BAD_REQUEST)
        if not data.get('nombres'):
            return Response({'detail': 'Los nombres son obligatorios.'}, status=status.HTTP_400_BAD_REQUEST)
        if not data.get('apellidos'):
            return Response({'detail': 'Los apellidos son obligatorios.'}, status=status.HTTP_400_BAD_REQUEST)
        if not data.get('id_institucion'):
            return Response({'detail': 'La institución es obligatoria.'}, status=status.HTTP_400_BAD_REQUEST)

        if Usuario.objects.filter(username=data.get('username')).exists():
            return Response({'detail': 'Ya existe un usuario con ese username.'}, status=status.HTTP_400_BAD_REQUEST)
        if Usuario.objects.filter(email=data.get('email')).exists():
            return Response({'detail': 'Ya existe un usuario con ese email.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            institucion = Institucion.objects.get(pk=data.get('id_institucion'), estado='activo')
        except Institucion.DoesNotExist:
            return Response({'detail': 'Institución no encontrada.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            user = Usuario(
                username      = data.get('username'),
                email         = data.get('email'),
                nombres       = data.get('nombres'),
                apellidos     = data.get('apellidos'),
                nro_celular   = data.get('nro_celular', ''),
                user_telegram = data.get('user_telegram', ''),
                ci            = data.get('ci') or None,
                is_active     = False,  # espera aprobación
            )
            user.set_password(data.get('password'))
            user.save()

            Cliente.objects.create(
                usuario        = user,
                institucion    = institucion,
                rol_institucion= data.get('rol_institucion') or None,
            )

        return Response(
            {'detail': 'Registro exitoso. Tu cuenta está pendiente de aprobación por un administrador.'},
            status=status.HTTP_201_CREATED
        )


class ClienteEliminarView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        if cliente.estado == 'eliminado':
            return Response(
                {'detail': 'El cliente ya está eliminado.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cliente.estado = 'eliminado'
        cliente.save()
        cliente.usuario.is_active = False
        cliente.usuario.save()
        return Response({'detail': f'Cliente {cliente.usuario.username} marcado como eliminado.'})

class AprobarClienteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        cliente.usuario.is_active = True
        cliente.usuario.save()
        return Response({'detail': f'Cliente {cliente.usuario.username} aprobado correctamente.'})



# ──────────────────────────────────────────
# Registro público de usuario sin rol
# ──────────────────────────────────────────
class RegistroUsuarioPublicoView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegistroUsuarioPublicoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()
        return Response(
            {
                'detail': 'Usuario registrado exitosamente. Pendiente de aprobación.',
                'id': usuario.id
            },
            status=status.HTTP_201_CREATED
        )

# ──────────────────────────────────────────
# Gestión de usuarios (admin)
# ──────────────────────────────────────────
class UsuarioListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Usuario.objects.all()
    serializer_class = UsuarioConRolesSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RegistroUsuarioPublicoSerializer  # Reutilizamos el mismo para creación
        return UsuarioConRolesSerializer

    def perform_create(self, serializer):
        # El usuario se crea inactivo por defecto
        serializer.save(is_active=False)


class UsuarioDetailView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Usuario.objects.all()
    serializer_class = UsuarioConRolesSerializer

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UsuarioUpdateSerializer
        return UsuarioConRolesSerializer


class AprobarUsuarioView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        if usuario.is_active:
            return Response(
                {'detail': 'El usuario ya está activo.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        usuario.is_active = True
        usuario.save()
        return Response({'detail': f'Usuario {usuario.username} aprobado.'})


class AsignarRolAgenteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        if hasattr(usuario, 'agente'):
            return Response(
                {'detail': 'El usuario ya tiene perfil de agente.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        agente = Agente.objects.create(usuario=usuario, estado='activo')
        return Response(
            {'detail': 'Perfil de agente creado.', 'id_agente': agente.id},
            status=status.HTTP_201_CREATED
        )


class AsignarRolClienteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        if hasattr(usuario, 'cliente'):
            return Response(
                {'detail': 'El usuario ya tiene perfil de cliente.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Se requiere institución
        id_institucion = request.data.get('id_institucion')
        rol = request.data.get('rol_institucion')
        if not id_institucion:
            return Response(
                {'detail': 'Se requiere id_institucion.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from instituciones.models import Institucion
        try:
            institucion = Institucion.objects.get(pk=id_institucion, estado='activo')
        except Institucion.DoesNotExist:
            return Response(
                {'detail': 'Institución no encontrada o inactiva.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            cliente = Cliente.objects.create(
                usuario=usuario,
                institucion=institucion,
                rol_institucion=rol
            )
        return Response(
            {'detail': 'Perfil de cliente creado.', 'id_cliente': cliente.id},
            status=status.HTTP_201_CREATED
        )


class RemoverRolAgenteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        if not hasattr(usuario, 'agente'):
            return Response(
                {'detail': 'El usuario no tiene perfil de agente.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        agente = usuario.agente
        agente.estado = 'eliminado'
        agente.save()
        # Opcional: eliminar físicamente con agente.delete()
        return Response({'detail': 'Perfil de agente desactivado.'})


class RemoverRolClienteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        if not hasattr(usuario, 'cliente'):
            return Response(
                {'detail': 'El usuario no tiene perfil de cliente.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cliente = usuario.cliente
        cliente.delete()  # Eliminación física, o podrías agregar campo estado
        return Response({'detail': 'Perfil de cliente eliminado.'})

class ClienteToggleActivoView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        if cliente.estado == 'activo':
            cliente.estado = 'inactivo'
            msg = f'Cliente {cliente.usuario.username} desactivado.'
        else:
            cliente.estado = 'activo'
            msg = f'Cliente {cliente.usuario.username} activado.'
        cliente.save()
        return Response({'detail': msg})


class ClienteEliminarView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        if cliente.estado == 'eliminado':
            return Response(
                {'detail': 'El cliente ya está eliminado.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cliente.estado = 'eliminado'
        cliente.save()
        cliente.usuario.is_active = False
        cliente.usuario.save()
        return Response({'detail': f'Cliente {cliente.usuario.username} marcado como eliminado.'})