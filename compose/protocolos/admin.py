from django.contrib import admin
from .models import Protocolo, ProtocoloAnimal, Procedimiento, Analgesico

class ProtocoloAnimalInline(admin.TabularInline):
    model = ProtocoloAnimal
    extra = 0

class ProcedimientoInline(admin.TabularInline):
    model = Procedimiento
    extra = 0

class AnalgesicoInline(admin.TabularInline):
    model = Analgesico
    extra = 0

@admin.register(Protocolo)
class ProtocoloAdmin(admin.ModelAdmin):
    list_display = ("id", "inv_nombre", "estado", "creado_en")
    list_filter = ("estado", "riesgo_biologico")
    search_fields = ("inv_nombre", "instituciones", "justificacion")
    inlines = [ProtocoloAnimalInline, ProcedimientoInline, AnalgesicoInline]
