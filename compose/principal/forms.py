# principal/forms.py
from django import forms
from animales.models import GrupoAnimal, MovimientoGrupo

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
