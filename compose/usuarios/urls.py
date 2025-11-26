# /compose/usuarios/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    PerfilView,
    UsuarioListView,
    UsuarioCreateView,
    UsuarioUpdateView,
    UsuarioRolesView,
    UsuarioResetPasswordView,
    UsuarioToggleActivoView,
    CambiarMiPasswordView,
)

app_name = "usuarios"

urlpatterns = [
    path("perfil/", PerfilView.as_view(), name="perfil"),
    path("", UsuarioListView.as_view(), name="list"),
    path("nuevo/", UsuarioCreateView.as_view(), name="new"),
    path("<int:pk>/editar/", UsuarioUpdateView.as_view(), name="edit"),
    path("<int:pk>/roles/", UsuarioRolesView.as_view(), name="roles"),
    path("<int:pk>/reset-pass/", UsuarioResetPasswordView.as_view(), name="reset_password"),
    path("<int:pk>/toggle/", UsuarioToggleActivoView.as_view(), name="toggle"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("cambiar-password/", CambiarMiPasswordView.as_view(), name="change_password"),  # <---

]
