from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import get_object_or_404, ListCreateAPIView, RetrieveUpdateAPIView
from django.db import transaction

from .models import Usuario, Agente, Cliente, Administrador
from .serializers import (
    LoginSerializer,
    UsuarioSerializer, UsuarioUpdateSerializer, PasswordChangeSerializer,
    AgenteSerializer, AgenteCreateSerializer,
    ClienteSerializer, ClienteCreateSerializer,
    AdministradorSerializer, AdministradorCreateSerializer,
    RegistroUsuarioBaseSerializer, get_rol, get_token_para_usuario,
    UsuarioConRolSerializer,
)
from instituciones.models import Institucion


# ──────────────────────────────────────────
# Auth
# ──────────────────────────────────────────

class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        rol  = serializer.validated_data['rol']

        refresh = get_token_para_usuario(user)
        return Response({
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'rol':     rol,
            'user':    UsuarioSerializer(user).data,
        })


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = UsuarioSerializer(request.user).data
        data['rol'] = request.auth.get('rol') if request.auth else None
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


class AgenteAprobarView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        agente = get_object_or_404(Agente, pk=pk)

        if agente.usuario.is_active and agente.estado == 'activo':
            return Response(
                {'detail': 'El agente ya está activo.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        agente.usuario.is_active = True
        agente.usuario.save()
        agente.estado = 'activo'
        agente.save()

        return Response({'detail': f'Agente {agente.usuario.email} aprobado correctamente.'})


class AgenteToggleActivoView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        agente = get_object_or_404(Agente, pk=pk)
        if agente.estado == 'activo':
            agente.estado = 'inactivo'
            msg = f'Agente {agente.usuario.email} desactivado.'
        else:
            agente.estado = 'activo'
            msg = f'Agente {agente.usuario.email} activado.'
        agente.save()
        return Response({'detail': msg})


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
        cliente.estado = 'eliminado'
        cliente.save()
        cliente.usuario.is_active = False
        cliente.usuario.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AprobarClienteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        cliente.usuario.is_active = True
        cliente.usuario.save()
        cliente.estado = 'activo'
        cliente.save()
        return Response({'detail': f'Cliente {cliente.usuario.email} aprobado correctamente.'})


class ClienteToggleActivoView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        if cliente.estado == 'activo':
            cliente.estado = 'inactivo'
            msg = f'Cliente {cliente.usuario.email} desactivado.'
        else:
            cliente.estado = 'activo'
            msg = f'Cliente {cliente.usuario.email} activado.'
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
        return Response({'detail': f'Cliente {cliente.usuario.email} marcado como eliminado.'})


# ──────────────────────────────────────────
# Administradores
# ──────────────────────────────────────────

class AdministradorListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        admins = Administrador.objects.select_related('usuario').all()
        return Response(AdministradorSerializer(admins, many=True).data)

    def post(self, request):
        serializer = AdministradorCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin = serializer.save()
        return Response(AdministradorSerializer(admin).data, status=status.HTTP_201_CREATED)


class AdministradorDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(Administrador.objects.select_related('usuario'), pk=pk)

    def get(self, request, pk):
        return Response(AdministradorSerializer(self.get_object(pk)).data)

    def patch(self, request, pk):
        admin = self.get_object(pk)
        serializer = UsuarioUpdateSerializer(
            admin.usuario, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if 'estado' in request.data:
            admin.estado = request.data['estado']
            admin.save()
        return Response(AdministradorSerializer(admin).data)

    def delete(self, request, pk):
        admin = self.get_object(pk)
        admin.estado = 'eliminado'
        admin.save()
        admin.usuario.is_active = False
        admin.usuario.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ──────────────────────────────────────────
# Registro público
# ──────────────────────────────────────────

class RegistroClienteView(APIView):
    permission_classes = []

    def post(self, request):
        data = request.data.copy()
        serializer = ClienteCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            cliente = serializer.save()

        return Response(
            {'detail': 'Registro exitoso. Tu cuenta está pendiente de aprobación por un administrador.'},
            status=status.HTTP_201_CREATED
        )


class RegistroAgenteView(APIView):
    permission_classes = []

    def post(self, request):
        data = request.data.copy()
        data['estado'] = 'inactivo'

        serializer = AgenteCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            serializer.save()

        return Response(
            {'detail': 'Registro de agente exitoso. Tu cuenta está pendiente de aprobación por el administrador.'},
            status=status.HTTP_201_CREATED
        )


# ──────────────────────────────────────────
# Gestión de usuarios (admin)
# ──────────────────────────────────────────

class UsuarioListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Usuario.objects.all()
    serializer_class = UsuarioConRolSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RegistroUsuarioBaseSerializer
        return UsuarioConRolSerializer


class UsuarioDetailView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Usuario.objects.all()
    serializer_class = UsuarioConRolSerializer

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UsuarioUpdateSerializer
        return UsuarioConRolSerializer


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
        return Response({'detail': f'Usuario {usuario.email} aprobado.'})