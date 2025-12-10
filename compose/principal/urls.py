from django.urls import path
from .views import DashboardView, ReporteMovimientosAnimalesView

app_name = "principal"

urlpatterns = [
    # ruta raíz de la app principal
    path("", DashboardView.as_view(), name="dashboard"),
    path("reportes/movimientos-animales/", ReporteMovimientosAnimalesView.as_view(), name="reporte_mov_animales"),
]
