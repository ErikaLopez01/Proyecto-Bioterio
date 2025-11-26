from django.contrib import admin
from .models import Categoria, Insumo, MovimientoInsumo

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "creado_en")
    search_fields = ("nombre",)

@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "unidad", "stock_actual", "stock_minimo", "precio_unitario", "activo")
    list_filter = ("categoria", "unidad", "activo")
    search_fields = ("nombre",)

@admin.register(MovimientoInsumo)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ("insumo", "tipo", "cantidad", "fecha", "usuario")
    list_filter = ("tipo", "fecha")
    search_fields = ("insumo__nombre", "motivo")
