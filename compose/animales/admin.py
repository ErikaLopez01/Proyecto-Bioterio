# animales/admin.py
from django.contrib import admin
from .models import Especie, Cepa, Jaula, GrupoAnimal, MovimientoGrupo


@admin.register(Especie)
class EspecieAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(Cepa)
class CepaAdmin(admin.ModelAdmin):
    list_display = ("id", "especie", "nombre", "descripcion")
    list_filter = ("especie",)
    search_fields = ("nombre", "especie__nombre")


@admin.register(Jaula)
class JaulaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "ubicacion", "capacidad")
    search_fields = ("nombre", "ubicacion")


@admin.register(GrupoAnimal)
class GrupoAnimalAdmin(admin.ModelAdmin):
    list_display = (
        "id", "especie", "cepa", "jaula",
        "cantidad_machos", "cantidad_hembras",
        "stock_minimo_machos", "stock_minimo_hembras",
        "activo", "creado_en",
    )
    list_filter = ("activo", "especie", "cepa", "jaula")
    search_fields = ("especie__nombre", "cepa__nombre", "jaula__nombre")
    readonly_fields = ("creado_en", "actualizado_en")


@admin.register(MovimientoGrupo)
class MovimientoAdmin(admin.ModelAdmin):
    # Reemplazamos 'tipo' y 'grupo_destino' por los nuevos campos
    list_display = (
        "id",
        "categoria",          # antes: 'tipo'
        "motivo",
        "grupo",
        "cantidad_machos",
        "cantidad_hembras",
        "protocolo",          # visible solo si motivo = PRO
        "jaula_destino",      # visible solo si categoría = TRA
        "fecha",
        "usuario",
    )
    list_filter = (
        "categoria",          # antes: 'tipo'
        "motivo",
        "grupo__especie",
        "grupo__cepa",
        "grupo__jaula",
        "usuario",
        "fecha",
    )
    search_fields = (
        "grupo__especie__nombre",
        "grupo__cepa__nombre",
        "grupo__jaula__nombre",
        "protocolo__inv_nombre",
        "usuario__username",
    )
    readonly_fields = ("fecha",)
    autocomplete_fields = ("grupo", "protocolo", "jaula_destino")
    date_hierarchy = "fecha"
    ordering = ("-fecha",)
