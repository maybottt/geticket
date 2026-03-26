from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """Login — devuelve access + refresh + datos del usuario."""
    serializer_class = CustomTokenObtainPairSerializer


class MeView(APIView):
    """Devuelve los datos del usuario autenticado."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id':        user.pk,
            'username':  user.username,
            'email':     user.email,
            'nombres':   user.nombres,
            'apellidos': user.apellidos,
            'is_admin':  user.is_admin,
            'rol':       self._get_rol(user),
        })

    def _get_rol(self, user):
        if user.is_admin:
            return 'administrador'
        if hasattr(user, 'agente'):
            return 'agente'
        if hasattr(user, 'cliente'):
            return 'cliente'
        return None