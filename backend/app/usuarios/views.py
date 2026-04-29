# usuarios/views.py
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate

from .models import Usuario, Agente, Cliente, Administrador
from .serializers import (
    LoginSerializer,
    UsuarioSerializer,
    UsuarioUpdateSerializer,
    UsuarioConRolSerializer,
    PasswordChangeSerializer,
    AgenteSerializer,
    AgenteCreateSerializer,
    ClienteSerializer,
    ClienteCreateSerializer,
    AdministradorSerializer,
    AdministradorCreateSerializer,
    get_token_para_usuario,
)
from .permissions import EsAdministrador, EsPropietarioOAdmin


# ---------------------------------------------------------------------------
# Autenticación: Login
# ---------------------------------------------------------------------------
class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = get_token_para_usuario(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'rol': serializer.validated_data['rol'],
        })


# ---------------------------------------------------------------------------
# Cambio de contraseña (usuario autenticado)
# ---------------------------------------------------------------------------
class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data['password_nuevo']
        request.user.set_password(new_password)
        request.user.save()
        return Response({'detail': 'Contraseña actualizada.'})


# ---------------------------------------------------------------------------
# Registro público de Cliente (sin autenticación)
# ---------------------------------------------------------------------------
class RegistroClienteView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = ClienteCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cliente = serializer.save()
        # El usuario asociado queda inactivo; devolvemos datos básicos
        return Response(
            ClienteSerializer(cliente).data,
            status=status.HTTP_201_CREATED
        )

# ---------------------------------------------------------------------------
# Administración de Usuarios (admin)
# ---------------------------------------------------------------------------
class UsuarioViewSet(viewsets.ModelViewSet):
    """
    Admin puede listar/crear/editar/eliminar usuarios.
    """
    permission_classes = [permissions.IsAuthenticated, EsAdministrador]
    queryset = Usuario.objects.all()
    serializer_class = UsuarioConRolSerializer  # incluye rol

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UsuarioUpdateSerializer
        return UsuarioConRolSerializer


# ---------------------------------------------------------------------------
# Perfil del usuario autenticado (ver/editar)
# ---------------------------------------------------------------------------
class MiPerfilView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UsuarioUpdateSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        # Para editar, debemos usar partial update si solo envía algunos campos
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# Vistas de perfil Agente (admin)
# ---------------------------------------------------------------------------
class AgenteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, EsAdministrador]
    queryset = Agente.objects.all()
    serializer_class = AgenteSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return AgenteCreateSerializer
        return AgenteSerializer


# ---------------------------------------------------------------------------
# Vistas de perfil Cliente (admin)
# ---------------------------------------------------------------------------
class ClienteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, EsAdministrador]
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return ClienteCreateSerializer
        return ClienteSerializer


# ---------------------------------------------------------------------------
# Vistas de perfil Administrador (admin)
# ---------------------------------------------------------------------------
class AdministradorViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, EsAdministrador]
    queryset = Administrador.objects.all()
    serializer_class = AdministradorSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return AdministradorCreateSerializer
        return AdministradorSerializer