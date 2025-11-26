from django import forms
from .models import GrupoAnimal, MovimientoGrupo, Especie, Cepa, Jaula


class EspecieForm(forms.ModelForm):
    class Meta:
        model = Especie
        fields = ["nombre", "descripcion"]


class CepaForm(forms.ModelForm):
    class Meta:
        model = Cepa
        fields = ["especie", "nombre", "descripcion"]


class JaulaForm(forms.ModelForm):
    class Meta:
        model = Jaula
        fields = ["nombre", "ubicacion", "capacidad"]


class GrupoAnimalForm(forms.ModelForm):
    class Meta:
        model = GrupoAnimal
        fields = [
            "especie", "cepa", "jaula",
            "stock_minimo_machos", "stock_minimo_hembras",
            "activo",
        ]
        help_texts = {"cepa": "Opcional. Déjalo vacío si no aplica."}


class MovimientoGrupoForm(forms.ModelForm):
    class Meta:
        model = MovimientoGrupo
        fields = [
            "grupo", "categoria", "motivo",
            "cantidad_machos", "cantidad_hembras",
            "protocolo", "jaula_destino",
            "observacion",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        cat = (self.data.get("categoria") or getattr(self.instance, "categoria", None))
        mot = (self.data.get("motivo") or getattr(self.instance, "motivo", None))

        # --- Filtrar motivos permitidos por categoría (validación de seguridad) ---
        if cat in MovimientoGrupo.MOTIVOS_POR_CATEGORIA:
            permitidos = MovimientoGrupo.MOTIVOS_POR_CATEGORIA[cat]
            self.fields["motivo"].choices = [
                c for c in MovimientoGrupo.MOTIVOS_ALL if c[0] in permitidos
            ]

        # Protocolo: NO lo ocultamos, solo lo dejamos no obligatorio.
        # La obligatoriedad se controla en clean() cuando motivo == MOT_PRO.
        self.fields["protocolo"].required = False

        # Jaula destino: igual, visible pero no obligatoria salvo categoría TRASLADO.
        self.fields["jaula_destino"].required = False

        # Refuerza que solo se puedan elegir protocolos aprobados
        if "protocolo" in self.fields:
            self.fields["protocolo"].queryset = \
                self.fields["protocolo"].queryset.filter(estado="aprobado")

    def clean(self):
        cleaned = super().clean()
        cat = cleaned.get("categoria")
        mot = cleaned.get("motivo")
        protocolo = cleaned.get("protocolo")
        jaula_destino = cleaned.get("jaula_destino")

        # 1) Motivo coherente con la categoría
        if cat and mot:
            permitidos = MovimientoGrupo.MOTIVOS_POR_CATEGORIA.get(cat, [])
            if mot not in permitidos:
                self.add_error(
                    "motivo",
                    "El motivo seleccionado no corresponde a la categoría elegida."
                )

        # 2) Protocolo obligatorio si el motivo es 'Protocolo'
        if mot == MovimientoGrupo.MOT_PRO and not protocolo:
            self.add_error(
                "protocolo",
                "Debe seleccionar un protocolo cuando el motivo es 'Protocolo'."
            )

        # 3) Jaula destino obligatoria si es traslado
        if cat == MovimientoGrupo.CAT_TRASLADO and not jaula_destino:
            self.add_error(
                "jaula_destino",
                "Debe seleccionar la jaula destino para un traslado."
            )

        # 4) Si NO es traslado, borramos cualquier jaula_destino enviada por error
        if cat != MovimientoGrupo.CAT_TRASLADO:
            cleaned["jaula_destino"] = None

        return cleaned



