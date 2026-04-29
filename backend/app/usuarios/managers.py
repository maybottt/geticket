# usuarios/managers.py
from django.contrib.auth.hashers import make_password
from django.db import models


class UsuarioManager(models.Manager):
    def create_user(self, username, email, nombres, apellidos, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            nombres=nombres,
            apellidos=apellidos,
            **extra_fields
        )
        if password:
            user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, nombres, apellidos, password=None, **extra_fields):
        user = self.create_user(username, email, nombres, apellidos, password, **extra_fields)
        from .models import Administrador
        Administrador.objects.get_or_create(usuario=user, defaults={'estado': 'activo'})
        return user