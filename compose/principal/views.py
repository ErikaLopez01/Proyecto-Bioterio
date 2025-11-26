"""
Vista del dashboard (página principal).
- Muestra KPIs básicos de Insumos y Animales
- Lista últimos movimientos (breve)
- Provee accesos a administrar Animales / Insumos
"""

from django.views.generic import TemplateView
from django.db.models import F

from animales.models import GrupoAnimal, MovimientoGrupo

class DashboardView(TemplateView):
    template_name = "principal/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        grupos = GrupoAnimal.objects.select_related("especie", "cepa", "jaula")

        ctx["anim_bajo_machos"] = grupos.filter(
            cantidad_machos__lt=F("stock_minimo_machos")
        ).count()
        ctx["anim_bajo_hembras"] = grupos.filter(
            cantidad_hembras__lt=F("stock_minimo_hembras")
        ).count()

        ctx["ult_mov_animales"] = (
            MovimientoGrupo.objects
            .select_related("grupo", "grupo__especie", "grupo__jaula")
            .order_by("-fecha")[:5]
        )

        # Insumos: hacemos try/except por si tu módulo no tiene estos campos/tablas
        try:
            from insumos.models import Insumo, Movimiento
            ctx["ins_bajo_min"] = Insumo.objects.filter(
                stock_actual__lt=F("stock_minimo")
            ).count()
            ctx["ult_mov_insumos"] = (
                Movimiento.objects.select_related("insumo").order_by("-fecha")[:5]
            )
        except Exception:
            ctx["ins_bajo_min"] = 0
            ctx["ult_mov_insumos"] = []

        return ctx

