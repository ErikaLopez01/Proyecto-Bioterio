"""
Crea/actualiza los grupos de roles después de aplicar migraciones.
- Administrador: todos los permisos de insumos y animales.
- Investigador: ver todo + agregar/cambiar "movimientos".
"""
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.db.models import Q

APPS_OBJETIVO = {"insumos", "animales"}

@receiver(post_migrate)
def crear_roles_basicos(sender, **kwargs):
    # Trae permisos de las apps objetivo
    perms = Permission.objects.filter(content_type__app_label__in=APPS_OBJETIVO)

    # Administrador: todos los permisos de esas apps
    admin, _ = Group.objects.get_or_create(name="Administrador")
    admin.permissions.set(perms)

    
    # Investigador: ver todo + add_/change_ de “movimiento”
    investigador, _ = Group.objects.get_or_create(name="Investigador")
    investigador_perms = perms.filter(
        Q(codename__startswith="view_")
        | Q(codename__startswith="add_", codename__contains="movimiento")
        | Q(codename__startswith="change_", codename__contains="movimiento")
    )
    investigador.permissions.set(investigador_perms)
