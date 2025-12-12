# principal/forms.py
from django import forms
from animales.models import GrupoAnimal, MovimientoGrupo
from protocolos.models import Protocolo
from insumos.models import Insumo


class ReporteMovimientosAnimalesForm(forms.Form):
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    grupo = forms.ModelChoiceField(
        queryset=GrupoAnimal.objects.select_related("especie", "cepa", "jaula"),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    motivo = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Motivo / razón"})
    )

class ReporteMovimientosAnimalesForm(forms.Form):
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    grupo = forms.ModelChoiceField(
        queryset=GrupoAnimal.objects.select_related("especie", "cepa", "jaula"),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    motivo = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Motivo / razón"})
    )


class ReporteProtocolosForm(forms.Form):
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    estado = forms.ChoiceField(
        required=False,
        choices=[("", "Todos")] + list(Protocolo.ESTADOS),
        widget=forms.Select(attrs={"class": "form-select"})
    )


class ReporteMovimientosInsumosForm(forms.Form):
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    insumo = forms.ModelChoiceField(
        queryset=Insumo.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    tipo = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Tipo de movimiento (entrada/salida)"})
    )


class ReporteConsumosForm(forms.Form):
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    insumo = forms.ModelChoiceField(
        queryset=Insumo.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )