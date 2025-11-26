from django.urls import path
from . import views
from django.http import HttpResponse


app_name = "animales"

urlpatterns = [
    path("", views.GrupoListView.as_view(), name="list"),
    path("grupos/nuevo/", views.GrupoCreateView.as_view(), name="create"),
    path("grupos/<int:pk>/editar/", views.GrupoUpdateView.as_view(), name="update"),
    path("grupos/<int:pk>/eliminar/", views.GrupoDeleteView.as_view(), name="delete"),
    path("grupos/<int:grupo_id>/movimientos/nuevo/", views.MovimientoCreateView.as_view(), name="mov_new"),

    path("especie/nueva/", views.EspecieCreateView.as_view(), name="especie_new"),
    path("cepa/nueva/", views.CepaCreateView.as_view(), name="cepa_new"),
    path("jaula/nueva/", views.JaulaCreateView.as_view(), name="jaula_new"),
]
