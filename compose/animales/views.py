from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.db.models import F, Q

from .forms import (
    GrupoAnimalForm, MovimientoGrupoForm,
    EspecieForm, CepaForm, JaulaForm
)
from .models import GrupoAnimal, MovimientoGrupo, Especie, Cepa, Jaula


class GrupoListView(ListView):
    model = GrupoAnimal
    template_name = "animales/grupo_list.html"
    context_object_name = "grupos"

    def get_queryset(self):
        qs = super().get_queryset().select_related("especie", "cepa", "jaula")
        especie = self.request.GET.get("especie")
        jaula = self.request.GET.get("jaula")
        # --- Alertas por mínimos ---
        # alert=low_m  -> machos bajo mínimo
        # alert=low_f  -> hembras bajo mínimo
        # alert=low_any -> cualquiera de los dos bajo mínimo
        if especie:
            qs = qs.filter(especie__nombre__icontains=especie)
        if jaula:
            qs = qs.filter(jaula__nombre__icontains=jaula)
        alert = self.request.GET.get("alert")
        if alert == "low_m":
            qs = qs.filter(cantidad_machos__lt=F("stock_minimo_machos"))
        elif alert == "low_f":
            qs = qs.filter(cantidad_hembras__lt=F("stock_minimo_hembras"))
        elif alert == "low_any":
            qs = qs.filter(
                Q(cantidad_machos__lt=F("stock_minimo_machos")) |
                Q(cantidad_hembras__lt=F("stock_minimo_hembras"))
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        grupos = list(ctx["grupos"])  # aseguro evaluación para sumar en Python
        ctx["total_machos"] = sum(g.cantidad_machos for g in grupos)
        ctx["total_hembras"] = sum(g.cantidad_hembras for g in grupos)
        ctx["total_general"] = ctx["total_machos"] + ctx["total_hembras"]
        return ctx


class GrupoCreateView(LoginRequiredMixin, CreateView):
    model = GrupoAnimal
    form_class = GrupoAnimalForm
    template_name = "animales/grupo_form.html"
    success_url = reverse_lazy("animales:list")


class GrupoUpdateView(LoginRequiredMixin, UpdateView):
    model = GrupoAnimal
    form_class = GrupoAnimalForm
    template_name = "animales/grupo_form.html"
    success_url = reverse_lazy("animales:list")


class GrupoDeleteView(LoginRequiredMixin, DeleteView):
    model = GrupoAnimal
    template_name = "animales/grupo_form.html"
    success_url = reverse_lazy("animales:list")


class MovimientoCreateView(LoginRequiredMixin, FormView):
    template_name = "animales/movimiento_form.html"
    form_class = MovimientoGrupoForm

    def dispatch(self, request, *args, **kwargs):
        self.grupo = get_object_or_404(GrupoAnimal, pk=kwargs["grupo_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Ocultar y fijar el grupo en el form (aunque en form_valid lo seteamos igual)
        if "grupo" in form.fields:
            form.fields["grupo"].widget = forms.HiddenInput()
            form.fields["grupo"].initial = self.grupo.pk

        # Si eventualmente muestran jaula_destino (categoría = TRASLADO),
        # el queryset debe excluir la jaula actual del grupo origen.
        if "jaula_destino" in form.fields:
            form.fields["jaula_destino"].queryset = Jaula.objects.exclude(pk=self.grupo.jaula_id)

        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["grupo"] = self.grupo
        return ctx

    def form_valid(self, form):
        mov = form.save(commit=False)
        mov.grupo = self.grupo
        mov.usuario = self.request.user if self.request.user.is_authenticated else None
        mov.save()  # aplica stock en save()
        messages.success(self.request, "Movimiento registrado.")
        return redirect("animales:list")


# Altas auxiliares
class EspecieCreateView(LoginRequiredMixin, CreateView):
    model = Especie
    form_class = EspecieForm
    template_name = "animales/especie_form.html"   
    success_url = reverse_lazy("animales:list")


class CepaCreateView(LoginRequiredMixin, CreateView):
    model = Cepa
    form_class = CepaForm
    template_name = "animales/Cepa_form.html"
    success_url = reverse_lazy("animales:list")


class JaulaCreateView(LoginRequiredMixin, CreateView):
    model = Jaula
    form_class = JaulaForm
    template_name = "animales/Jaula_form.html"
    success_url = reverse_lazy("animales:list")
