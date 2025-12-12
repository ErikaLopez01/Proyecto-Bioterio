# usuarios/views.py
from django import forms
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, View, FormView
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.utils.crypto import get_random_string
from .forms import UserCreateForm, UserUpdateForm, PasswordChangeCustomForm 


def _is_admin(user):
    return user.is_superuser or user.groups.filter(name="Administrador").exists()


class PerfilView(LoginRequiredMixin, TemplateView):
    template_name = "usuarios/perfil.html"


class UsuarioListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = "usuarios/usuario_list.html"
    context_object_name = "usuarios"

    def test_func(self):
        return _is_admin(self.request.user)


class UsuarioCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "usuarios/usuario_form.html"
    success_url = reverse_lazy("usuarios:list")

    def test_func(self):
        return _is_admin(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Usuario creado correctamente.")
        return super().form_valid(form)


class UsuarioUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "usuarios/usuario_form.html"
    success_url = reverse_lazy("usuarios:list")

    def test_func(self):
        return _is_admin(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Usuario actualizado correctamente.")
        return super().form_valid(form)


class UsuarioToggleActivoView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Activa/Desactiva un usuario (link o botón)"""
    def test_func(self):
        return _is_admin(self.request.user)

    def post(self, request, pk):
        usuario = get_object_or_404(User, pk=pk)
        if usuario == request.user:
            messages.warning(request, "No puedes desactivarte a ti mismo.")
            return redirect("usuarios:list")
        usuario.is_active = not usuario.is_active
        usuario.save()
        messages.success(request, f"Usuario {'activado' if usuario.is_active else 'desactivado'}.")
        return redirect("usuarios:list")


class UsuarioRolesView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    """Asigna un único rol (grupo) al usuario."""
    template_name = "usuarios/usuario_roles.html"
    success_url = reverse_lazy("usuarios:list")

    def test_func(self):
        return _is_admin(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        self.usuario = get_object_or_404(User, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        class RoleForm(forms.Form):
            role = forms.ModelChoiceField(
                label="Rol (Grupo)",
                queryset=Group.objects.all().order_by("name"),
                required=False,
                help_text="Selecciona un rol para el usuario (opcional).",
                widget=forms.Select(attrs={"class": "form-select"})
            )
        return RoleForm

    def get_initial(self):
        actual = self.usuario.groups.first()
        return {"role": actual}

    def form_valid(self, form):
        role = form.cleaned_data.get("role")
        self.usuario.groups.clear()
        if role:
            self.usuario.groups.add(role)
        messages.success(self.request, "Rol actualizado correctamente.")
        return super().form_valid(form)


class UsuarioResetPasswordView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Resetea la contraseña del usuario a una temporal y le marca 'must_change_password' si lo implementas."""
    def test_func(self):
        return _is_admin(self.request.user)

    def post(self, request, pk):
        usuario = get_object_or_404(User, pk=pk)
        temp = get_random_string(12)
        usuario.set_password(temp)
        usuario.save()
        # 1) marcar el flag
        if hasattr(usuario, "security"):
            usuario.security.must_change_password = True
            usuario.security.save()

        # 2) mensaje sin mostrar la clave
        messages.success(
            request,
            f"Se generó una contraseña temporal para {usuario.username}. "
            "El usuario deberá cambiarla al iniciar sesión."
        )

        return redirect("usuarios:list")

class CambiarMiPasswordView(LoginRequiredMixin, FormView):
    template_name = "usuarios/password_change.html"
    success_url = reverse_lazy("usuarios:perfil")  # o donde quieras redirigir
    form_class = PasswordChangeCustomForm

    def get_form_kwargs(self):
        """
        Pasamos el usuario logueado al formulario.
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        nuevo_pass = form.cleaned_data["new_password1"]
        user = self.request.user
        user.set_password(nuevo_pass)
        user.save()

        # Muy importante: mantener la sesión iniciada
        update_session_auth_hash(self.request, user)

        messages.success(self.request, "Tu contraseña se actualizó correctamente.")
        return super().form_valid(form)

class ForcedPasswordChangeView(PasswordChangeView):
    template_name = "usuarios/password_change_forced.html"
    success_url = reverse_lazy("usuarios:password_change_done")

    def form_valid(self, form):
        response = super().form_valid(form)

        user = self.request.user

        # Desmarcar el flag después de cambiar contraseña
        if hasattr(user, "security"):
            user.security.must_change_password = False
            user.security.save()

        messages.success(self.request, "Tu contraseña ha sido actualizada. Puedes continuar usando el sistema.")
        return response
    

class ForcedPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    """
    Vista que se muestra después de que el usuario cambia
    su contraseña obligatoriamente.
    """
    template_name = "usuarios/password_change_done.html"
