# usuarios/middleware.py
from django.shortcuts import redirect
from django.urls import reverse


class MustChangePasswordMiddleware:
    """
    Si el usuario tiene el flag must_change_password=True,
    lo fuerza a pasar por la pantalla de cambio de contraseña
    antes de poder navegar el sistema.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        # Si no está autenticado, no hacemos nada
        if not user.is_authenticated:
            return self.get_response(request)

        # Si el usuario no tiene perfil de seguridad, seguimos normal
        security = getattr(user, "security", None)
        if not security or not security.must_change_password:
            return self.get_response(request)

        # Rutas que SÍ se permiten aunque el usuario deba cambiar la contraseña
        forced_url = reverse("usuarios:password_change_forced")
        done_url = reverse("usuarios:password_change_done")
        login_url = reverse("login")  # asumiendo que tu login se llama 'login'
        logout_url = reverse("usuarios:logout")

        allowed_paths = {forced_url, done_url, login_url, logout_url}

        # Si está intentando ir a otra ruta, lo redirigimos al cambio forzado
        if request.path not in allowed_paths:
            return redirect("usuarios:password_change_forced")

        return self.get_response(request)
