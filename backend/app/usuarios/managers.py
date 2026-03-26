from django.contrib.auth.models import BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('El username es obligatorio')
        if not extra_fields.get('email'):
            raise ValueError('El email es obligatorio')
        extra_fields['email'] = self.normalize_email(extra_fields['email'])
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_active', True)
        if not extra_fields.get('is_admin'):
            raise ValueError('El superusuario debe tener is_admin=True')
        return self.create_user(username, password, **extra_fields)

