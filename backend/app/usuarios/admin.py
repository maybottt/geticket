from django import forms
from django.contrib import admin
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from .models import Usuario, Agente, Cliente, Administrador


# ---------------------------------------------------------------------------
# Formularios personalizados para Usuario
# ---------------------------------------------------------------------------

class UsuarioCreationForm(forms.ModelForm):
    """Formulario para crear nuevo usuario en el admin, con confirmación de contraseña."""
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'nombres', 'apellidos', 'nro_celular',
                  'nro_celular_dos', 'user_telegram', 'ci', 'estado')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Las contraseñas no coinciden.')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UsuarioChangeForm(forms.ModelForm):
    """Permite cambiar la contraseña en el admin mediante un campo opcional."""
    new_password = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput,
        required=False,
        help_text='Solo completar si desea cambiar la contraseña.'
    )

    class Meta:
        model = Usuario
        fields = '__all__'

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.password = make_password(new_password)
        if commit:
            user.save()
        return user


# ---------------------------------------------------------------------------
# ModelAdmin para Usuario
# ---------------------------------------------------------------------------

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    form = UsuarioChangeForm
    add_form = UsuarioCreationForm

    list_display = ('username', 'email', 'nombres', 'apellidos', 'estado', 'created_at')
    search_fields = ('username', 'email', 'nombres', 'apellidos', 'ci')
    ordering = ('-created_at',)
    list_filter = ('estado',)

    fieldsets = (
        (None, {'fields': ('username', 'email')}),
        ('Datos personales', {'fields': ('nombres', 'apellidos', 'ci',
                                         'nro_celular', 'nro_celular_dos',
                                         'user_telegram')}),
        ('Estado', {'fields': ('estado',)}),
        ('Contraseña', {'fields': ('new_password',)}),
        ('Fechas', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login')

    def get_form(self, request, obj=None, **kwargs):
        """Usa el formulario de creación para añadir, y el de cambio para editar."""
        if obj is None:
            return UsuarioCreationForm
        return super().get_form(request, obj, **kwargs)


# ---------------------------------------------------------------------------
# Otros modelos
# ---------------------------------------------------------------------------

@admin.register(Agente)
class AgenteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'estado', 'created_at')
    list_filter = ('estado',)
    search_fields = ('usuario__username', 'usuario__email')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'institucion', 'rol_institucion', 'estado', 'created_at')
    list_filter = ('estado', 'institucion')
    search_fields = ('usuario__username', 'usuario__email')


@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'estado', 'created_at')
    list_filter = ('estado',)
    search_fields = ('usuario__username', 'usuario__email')