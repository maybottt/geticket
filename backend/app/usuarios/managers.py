from django.contrib.auth.base_user import BaseUserManager



class UsuarioManager(BaseUserManager):
 
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
        user.set_password(password)
        user.save(using=self._db)
        return user
 
    def create_superuser(self, username, email, nombres, apellidos, password=None, **extra_fields):
        """
        Crea un usuario con perfil Administrador.
        Usado principalmente por el comando createsuperuser de Django.
        """
        extra_fields.setdefault('is_superuser', True)
        user = self.create_user(username, email, nombres, apellidos, password, **extra_fields)
 
        # Crear automáticamente el perfil administrador
        from .models import Administrador
        Administrador.objects.get_or_create(usuario=user, defaults={'estado': 'activo'})
 
        return user