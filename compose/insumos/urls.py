from django.urls import path
from . import views

app_name = "insumos"

urlpatterns = [
    path("", views.InsumoListView.as_view(), name="list"),
    path("nuevo/", views.InsumoCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", views.InsumoUpdateView.as_view(), name="update"),
    path("<int:pk>/eliminar/", views.InsumoDeleteView.as_view(), name="delete"),
    path("<int:insumo_id>/movimientos/nuevo/", views.MovimientoCreateView.as_view(), name="nuevo_mov"),
    path("categoria/nueva/", views.CategoriaCreateView.as_view(), name="categoria_create"),
]
