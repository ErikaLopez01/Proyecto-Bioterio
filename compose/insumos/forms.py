from django import forms
from .models import Insumo, MovimientoInsumo, Categoria

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion"]

class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ["nombre", "categoria", "unidad", "stock_minimo", "precio_unitario", "activo"]

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = MovimientoInsumo
        fields = ["tipo", "cantidad", "motivo"]
        widgets = {
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "cantidad": forms.NumberInput(attrs={"step": "0.001", "class": "form-control"}),
            "motivo": forms.TextInput(attrs={"class": "form-control"}),
        }
