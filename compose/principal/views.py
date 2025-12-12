"""
Vista del dashboard (página principal).
- Muestra KPIs básicos de Insumos y Animales
- Lista últimos movimientos (breve)
- Provee accesos a administrar Animales / Insumos
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import F, Sum
from django.http import HttpResponse
import csv
from .forms import (
    ReporteMovimientosAnimalesForm,
    ReporteProtocolosForm,
    ReporteMovimientosInsumosForm,
    ReporteConsumosForm,
)
from animales.models import GrupoAnimal, MovimientoGrupo
from insumos.models import Insumo, MovimientoInsumo
from protocolos.models import Protocolo


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "principal/dashboard.html"
    login_url = "login"
    redirect_field_name = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        # === KPIs de protocolos ===
        qs_proto = Protocolo.objects.all()
        ctx["total_protocolos"] = qs_proto.count()
        ctx["total_proto_borrador"] = qs_proto.filter(estado="borrador").count()
        ctx["total_proto_enviados"] = qs_proto.filter(estado="enviado").count()
        ctx["total_proto_aprobados"] = qs_proto.filter(estado="aprobado").count()
        ctx["total_proto_rechazados"] = qs_proto.filter(estado="rechazado").count()

        # === Animales bajo mínimo ===
        grupos = GrupoAnimal.objects.select_related("especie", "cepa", "jaula")
        ctx["anim_bajo_machos"] = grupos.filter(
            cantidad_machos__lt=F("stock_minimo_machos")
        ).count()
        ctx["anim_bajo_hembras"] = grupos.filter(
            cantidad_hembras__lt=F("stock_minimo_hembras")
        ).count()

        # === Insumos bajo mínimo ===
        ctx["ins_bajo_min"] = Insumo.objects.filter(
            stock_actual__lt=F("stock_minimo")
        ).count()

        # === Alertas / pendientes de protocolos ===
        es_admin = user.is_superuser or user.groups.filter(name="Administrador").exists()
        ctx["es_admin"] = es_admin

        if es_admin:
            ctx["protocolos_pendientes"] = (
                Protocolo.objects
                .filter(estado="enviado")
                .select_related("creado_por")
                .order_by("-id")[:5]
            )
            ctx["protocolos_aprobados_usuario"] = None
        else:
            ctx["protocolos_pendientes"] = None
            ctx["protocolos_aprobados_usuario"] = (
                Protocolo.objects
                .filter(estado="aprobado", creado_por=user)
                .order_by("-id")[:5]
            )

        # === Últimos movimientos de animales e insumos ===
        ctx["ult_mov_animales"] = (
            MovimientoGrupo.objects
            .select_related("grupo", "grupo__especie", "grupo__jaula")
            .order_by("-fecha")[:5]
        )

        ctx["ult_mov_insumos"] = (
            MovimientoInsumo.objects
            .select_related("insumo")
            .order_by("-fecha")[:5]
        )

        return ctx


class ReportesHomeView(LoginRequiredMixin, TemplateView):
    """
    Página sencilla con links a todos los reportes.
    Puedes reutilizar las mismas cards que pusimos en el dashboard.
    """
    template_name = "principal/reportes_home.html"


class ReporteMovimientosAnimalesView(LoginRequiredMixin, TemplateView):
    template_name = "principal/reporte_mov_animales.html"

    def get_queryset(self, form):
        qs = MovimientoGrupo.objects.select_related("grupo", "grupo__especie", "grupo__jaula")

        fecha_desde = form.cleaned_data.get("fecha_desde")
        fecha_hasta = form.cleaned_data.get("fecha_hasta")
        grupo = form.cleaned_data.get("grupo")
        motivo = form.cleaned_data.get("motivo")

        if fecha_desde:
            qs = qs.filter(fecha__date__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha__date__lte=fecha_hasta)
        if grupo:
            qs = qs.filter(grupo=grupo)
        if motivo:
            qs = qs.filter(motivo__icontains=motivo)

        return qs.order_by("-fecha")

    def get(self, request, *args, **kwargs):
        form = ReporteMovimientosAnimalesForm(request.GET or None)
        
        movimientos = MovimientoGrupo.objects.none()

        if form.is_valid():
            movimientos = self.get_queryset(form)
           
            if request.GET.get("export") == "csv":
                return self._export_csv(movimientos)

        ctx = self.get_context_data(form=form, movimientos=movimientos)
        return self.render_to_response(ctx)

    def _export_csv(self, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="reporte_movimientos_animales.csv"'
        writer = csv.writer(response)
        writer.writerow(["Fecha", "Grupo", "Especie", "Jaula", "Motivo", "Machos", "Hembras"])

        for mov in queryset:
            writer.writerow([
                mov.fecha,
                getattr(mov.grupo, "id", ""),
                getattr(mov.grupo.especie, "nombre", "") if mov.grupo and mov.grupo.especie else "",
                getattr(mov.grupo.jaula, "nombre", "") if mov.grupo and mov.grupo.jaula else "",
                getattr(mov, "motivo", ""),
                getattr(mov, "cantidad_machos", ""),
                getattr(mov, "cantidad_hembras", ""),
            ])

        return response


class ReporteProtocolosView(LoginRequiredMixin, TemplateView):
    template_name = "principal/reporte_protocolos.html"

    def get_queryset(self, form):
        qs = Protocolo.objects.select_related("creado_por")

        fecha_desde = form.cleaned_data.get("fecha_desde")
        fecha_hasta = form.cleaned_data.get("fecha_hasta")
        estado = form.cleaned_data.get("estado")

        if fecha_desde:
            qs = qs.filter(creado_en__date__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(creado_en__date__lte=fecha_hasta)
        if estado:
            qs = qs.filter(estado=estado)

        return qs.order_by("-creado_en")

    def get(self, request, *args, **kwargs):
        form = ReporteProtocolosForm(request.GET or None)
        items = Protocolo.objects.none()

        if form.is_valid():
            items = self.get_queryset(form)

        ctx = self.get_context_data(form=form, protocolos=items)
        return self.render_to_response(ctx)


class ReporteMovimientosInsumosView(LoginRequiredMixin, TemplateView):
    template_name = "principal/reporte_mov_insumos.html"

    def get_queryset(self, form):
        qs = MovimientoInsumo.objects.select_related("insumo")

        fecha_desde = form.cleaned_data.get("fecha_desde")
        fecha_hasta = form.cleaned_data.get("fecha_hasta")
        insumo = form.cleaned_data.get("insumo")
        tipo = form.cleaned_data.get("tipo")

        if fecha_desde:
            qs = qs.filter(fecha__date__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha__date__lte=fecha_hasta)
        if insumo:
            qs = qs.filter(insumo=insumo)
        if tipo:
            qs = qs.filter(tipo__icontains=tipo)

        return qs.order_by("-fecha")

    def get(self, request, *args, **kwargs):
        form = ReporteMovimientosInsumosForm(request.GET or None)
        items = MovimientoInsumo.objects.none()

        if form.is_valid():
            items = self.get_queryset(form)

        ctx = self.get_context_data(form=form, movimientos=items)
        return self.render_to_response(ctx)


class ReporteConsumosView(LoginRequiredMixin, TemplateView):
    """
    Stub sencillo: agrupa consumo de insumos por insumo.
    Más adelante se puede extender con jaula/especie.
    """
    template_name = "principal/reporte_consumos.html"

    def get(self, request, *args, **kwargs):
        form = ReporteConsumosForm(request.GET or None)

        queryset = MovimientoInsumo.objects.select_related("insumo")
        if form.is_valid():
            fecha_desde = form.cleaned_data.get("fecha_desde")
            fecha_hasta = form.cleaned_data.get("fecha_hasta")
            insumo = form.cleaned_data.get("insumo")

            if fecha_desde:
                queryset = queryset.filter(fecha__date__gte=fecha_desde)
            if fecha_hasta:
                queryset = queryset.filter(fecha__date__lte=fecha_hasta)
            if insumo:
                queryset = queryset.filter(insumo=insumo)

        agregados = (
            queryset
            .values("insumo__nombre")
            .annotate(total=Sum("cantidad"))
            .order_by("insumo__nombre")
        )

        ctx = self.get_context_data(form=form, consumos=agregados)
        return self.render_to_response(ctx)