from django.contrib.auth.base_user import BaseUserManager


class UsuarioManager(BaseUserManager):

    def create_user(self, username_admin, email, nombres, apellidos, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(
            username_admin=username_admin,
            email=email,
            nombres=nombres,
            apellidos=apellidos,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username_admin, email, nombres, apellidos, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username_admin, email, nombres, apellidos, password, **extra_fields)