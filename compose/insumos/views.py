from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db import transaction
from django.db.models import F
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from .forms import InsumoForm, MovimientoForm, CategoriaForm
from .models import Insumo, MovimientoInsumo, Categoria

class InsumoListView(ListView):
    model = Insumo
    template_name = "insumos/insumo_list.html"
    context_object_name = "insumos"

    def get_queryset(self):
        qs = super().get_queryset().select_related("categoria")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nombre__icontains=q)
        critico = self.request.GET.get("critico")
        if critico in ("1", "true", "yes", "si", "sí"):
            qs = qs.filter(stock_actual__lt=F("stock_minimo"))

        return qs

class InsumoCreateView(LoginRequiredMixin, CreateView):
    model = Insumo
    form_class = InsumoForm
    template_name = "insumos/insumo_form.html"
    success_url = reverse_lazy("insumos:list")

class InsumoUpdateView(LoginRequiredMixin, UpdateView):
    model = Insumo
    form_class = InsumoForm
    template_name = "insumos/insumo_form.html"
    success_url = reverse_lazy("insumos:list")

class InsumoDeleteView(LoginRequiredMixin, DeleteView):
    model = Insumo
    template_name = "insumos/insumo_form.html"
    success_url = reverse_lazy("insumos:list")

class MovimientoCreateView(LoginRequiredMixin, FormView):
    template_name = "insumos/movimiento_form.html"
    form_class = MovimientoForm

    def dispatch(self, request, *args, **kwargs):
        self.insumo = get_object_or_404(Insumo, pk=kwargs["insumo_id"])
        return super().dispatch(request, *args, **kwargs)

    @transaction.atomic
    def form_valid(self, form):
        mov = form.save(commit=False)
        mov.insumo = self.insumo
        mov.usuario = self.request.user if self.request.user.is_authenticated else None
        mov.save()
        messages.success(self.request, "Movimiento registrado correctamente.")
        return redirect("insumos:list")

class CategoriaCreateView(LoginRequiredMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "insumos/insumo_form.html"
    success_url = reverse_lazy("insumos:list")
