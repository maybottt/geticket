from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Agente, Cliente, Administrador


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display  = ('username', 'email', 'nombres', 'apellidos', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'nombres', 'apellidos', 'ci')
    ordering      = ('-created_at',)
    list_filter   = ('is_active', 'is_superuser') 
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Datos personales', {'fields': ('nombres', 'apellidos', 'ci', 'nro_celular', 'nro_celular_dos', 'user_telegram')}),
        ('Permisos', {'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'nombres', 'apellidos', 'password1', 'password2'),
        }),
    )


@admin.register(Agente)
class AgenteAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'estado', 'created_at')
    list_filter   = ('estado',)
    search_fields = ('usuario__username', 'usuario__email')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'institucion', 'rol_institucion', 'estado', 'created_at')
    list_filter   = ('estado', 'institucion')
    search_fields = ('usuario__username', 'usuario__email')


@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'estado', 'created_at')
    list_filter   = ('estado',)
    search_fields = ('usuario__username', 'usuario__email')