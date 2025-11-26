from django.urls import path
from .views import DashboardView

app_name = "principal"

urlpatterns = [
    # ruta raíz de la app principal
    path("", DashboardView.as_view(), name="dashboard"),
]
