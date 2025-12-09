# usuarios/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class MustChangePasswordMiddleware:
    """
    Si el usuario tiene must_change_password=True,
    lo obliga a ir a la vista de cambio de contraseña antes de usar el sistema.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        # Rutas que SÍ se permiten aunque deba cambiar la contraseña
        allowed_paths = {
            reverse("password_change_forced"),    # vista de cambio obligatorio
            reverse("password_change_done"),      # después de cambiar
            reverse("logout"),                    # poder salir
            reverse("login"),                     # login
        }

        if user.is_authenticated:
            must_change = False

            # Opción A: modelo Usuario con campo propio
            if hasattr(user, "must_change_password"):
                must_change = user.must_change_password

            # Opción B: perfil de seguridad
            elif hasattr(user, "security"):
                must_change = user.security.must_change_password

            if must_change and request.path not in allowed_paths:
                return redirect("password_change_forced")

        response = self.get_response(request)
        return response
