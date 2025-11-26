from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse


urlpatterns = [
    path("admin/", admin.site.urls),

    # Módulos
    path("insumos/", include("insumos.urls")),
    path("animales/", include("animales.urls")),
    path("usuarios/", include("usuarios.urls")),
    path("protocolos/", include("protocolos.urls")),

    # Auth built-in (login/logout/password reset)
    path("", include("django.contrib.auth.urls")),

    # Dashboard al final para que capture "/"
    path("", include("principal.urls")),
]
