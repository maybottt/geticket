from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import get_object_or_404

from .models import Usuario, Agente, Cliente
from .serializers import (
    LoginSerializer, ElegirRolSerializer, SwitchRolSerializer,
    UsuarioSerializer, UsuarioUpdateSerializer, PasswordChangeSerializer,
    AgenteSerializer, AgenteCreateSerializer,
    ClienteSerializer, ClienteCreateSerializer,
    get_roles, get_token_para_rol,
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

class AprobarClienteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        cliente.usuario.is_active = True
        cliente.usuario.save()
        return Response({'detail': f'Cliente {cliente.usuario.username} aprobado correctamente.'})