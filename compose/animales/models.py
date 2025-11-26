from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction


class Especie(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Cepa(models.Model):
    especie = models.ForeignKey(Especie, on_delete=models.CASCADE, related_name="cepas")
    nombre = models.CharField(max_length=80)
    descripcion = models.TextField(blank=True)

    class Meta:
        unique_together = [("especie", "nombre")]
        ordering = ["especie__nombre", "nombre"]

    def __str__(self):
        return f"{self.especie} - {self.nombre}"


class Jaula(models.Model):
    nombre = models.CharField(max_length=40, unique=True)
    ubicacion = models.CharField(max_length=120, blank=True)
    capacidad = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class GrupoAnimal(models.Model):
    """Unidad de inventario por jaula (mixto M/F)."""
    especie = models.ForeignKey(Especie, on_delete=models.PROTECT)
    cepa = models.ForeignKey(Cepa, on_delete=models.PROTECT, null=True, blank=True)
    jaula = models.ForeignKey(Jaula, on_delete=models.PROTECT)

    cantidad_machos = models.PositiveIntegerField(default=0)
    cantidad_hembras = models.PositiveIntegerField(default=0)

    stock_minimo_machos = models.PositiveIntegerField(default=0)
    stock_minimo_hembras = models.PositiveIntegerField(default=0)

    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("especie", "cepa", "jaula")]
        ordering = ["especie__nombre", "cepa__nombre", "jaula__nombre"]

    def __str__(self):
        cepa = self.cepa.nombre if self.cepa else "-"
        return f"{self.especie}/{cepa} @ {self.jaula} (M:{self.cantidad_machos} F:{self.cantidad_hembras})"

    @property
    def cantidad_total(self) -> int:
        return (self.cantidad_machos or 0) + (self.cantidad_hembras or 0)


class MovimientoGrupo(models.Model):
    # Categorías
    CAT_INGRESO = "ING"
    CAT_SALIDA  = "SAL"
    CAT_AJUSTE  = "AJU"
    CAT_TRASLADO = "TRA"

    CATEGORIAS = [
        (CAT_INGRESO, "Ingreso"),
        (CAT_SALIDA,  "Salida"),
        (CAT_AJUSTE,  "Ajuste"),
        (CAT_TRASLADO, "Traslado"),
    ]

    # Motivos
    MOT_NAC = "NAC"       # ingreso
    MOT_COM = "COM"       # ingreso
    MOT_VEN = "VEN"       # salida
    MOT_EUT = "EUT"       # salida
    MOT_MUE = "MUE"       # salida
    MOT_PRO = "PRO"       # salida -> protocolo
    MOT_AJU_POS = "APO"   # ajuste positivo
    MOT_AJU_NEG = "ANE"   # ajuste negativo
    MOT_TRA = "TRA"       # traslado (único motivo bajo categoría TRASLADO)

    MOTIVOS_ALL = [
        (MOT_NAC, "Nacimiento"),
        (MOT_COM, "Compra"),
        (MOT_VEN, "Venta"),
        (MOT_EUT, "Eutanasia"),
        (MOT_MUE, "Muerte"),
        (MOT_PRO, "Protocolo"),
        (MOT_AJU_POS, "Ajuste positivo"),
        (MOT_AJU_NEG, "Ajuste negativo"),
        (MOT_TRA, "Traslado"),
    ]

    MOTIVOS_POR_CATEGORIA = {
        CAT_INGRESO: {MOT_NAC, MOT_COM},
        CAT_SALIDA:  {MOT_VEN, MOT_EUT, MOT_MUE, MOT_PRO},
        CAT_AJUSTE:  {MOT_AJU_POS, MOT_AJU_NEG},
        CAT_TRASLADO:{MOT_TRA},
    }

    grupo = models.ForeignKey("GrupoAnimal", on_delete=models.CASCADE, related_name="movimientos")

    categoria = models.CharField(max_length=3, choices=CATEGORIAS)
    motivo = models.CharField(max_length=3, choices=MOTIVOS_ALL)

    cantidad_machos = models.PositiveIntegerField(default=0)
    cantidad_hembras = models.PositiveIntegerField(default=0)

    # Solo para motivo = Protocolo (limitado a 'aprobado')
    protocolo = models.ForeignKey(
        "protocolos.Protocolo",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        limit_choices_to={"estado": "aprobado"},
        help_text="Requerido si el motivo es 'Protocolo'.",
    )

    # Solo para categoría TRASLADO: elegir jaula destino
    jaula_destino = models.ForeignKey(
        "Jaula",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Requerido si la categoría es 'Traslado'.",
    )

    observacion = models.CharField(max_length=200, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        getattr(settings, "AUTH_USER_MODEL", "auth.User"),
        on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-fecha"]

    # ---------- Validaciones ----------
    def clean(self):
        total = (self.cantidad_machos or 0) + (self.cantidad_hembras or 0)
        if self.cantidad_machos < 0 or self.cantidad_hembras < 0:
            raise ValidationError("Las cantidades deben ser no negativas.")
        if total == 0:
            raise ValidationError("Debe ingresar al menos una cantidad (machos o hembras).")

        # Motivo válido para la categoría
        permitidos = self.MOTIVOS_POR_CATEGORIA.get(self.categoria, set())
        if self.motivo not in permitidos:
            raise ValidationError("El motivo no corresponde a la categoría seleccionada.")

        # Reglas por motivo
        if self.motivo == self.MOT_PRO:
            if not self.protocolo_id:
                raise ValidationError("Seleccione un Protocolo (aprobado) para motivo 'Protocolo'.")
        else:
            if self.protocolo_id:
                raise ValidationError("Solo puede asociar un Protocolo cuando el motivo es 'Protocolo'.")

        # Reglas para traslado
        if self.categoria == self.CAT_TRASLADO:
            if not self.jaula_destino_id:
                raise ValidationError("Debe seleccionar una jaula destino para el traslado.")
            if self.grupo.jaula_id == self.jaula_destino_id:
                raise ValidationError("La jaula destino debe ser diferente a la jaula origen.")

    # ---------- Helpers stock ----------
    def _add(self, g, m, f):
        g.cantidad_machos += m
        g.cantidad_hembras += f
        if g.cantidad_machos < 0 or g.cantidad_hembras < 0:
            raise ValidationError("El stock no puede quedar negativo.")
        g.save(update_fields=["cantidad_machos", "cantidad_hembras"])

    def _sub(self, g, m, f):
        if g.cantidad_machos < m or g.cantidad_hembras < f:
            raise ValidationError("Stock insuficiente para el movimiento.")
        g.cantidad_machos -= m
        g.cantidad_hembras -= f
        g.save(update_fields=["cantidad_machos", "cantidad_hembras"])

    @transaction.atomic
    def apply(self):
        origen = GrupoAnimal.objects.select_for_update().get(pk=self.grupo_id)
        m, f = self.cantidad_machos, self.cantidad_hembras

        if self.categoria == self.CAT_INGRESO:
            self._add(origen, m, f)

        elif self.categoria == self.CAT_SALIDA:
            self._sub(origen, m, f)

        elif self.categoria == self.CAT_AJUSTE:
            if self.motivo == self.MOT_AJU_POS:
                self._add(origen, m, f)
            else:  # MOT_AJU_NEG
                self._sub(origen, m, f)

        elif self.categoria == self.CAT_TRASLADO:
            # Buscar/crear grupo destino con misma especie/cepa y jaula_destino
            dest, _created = GrupoAnimal.objects.select_for_update().get_or_create(
                especie_id=origen.especie_id,
                cepa_id=origen.cepa_id,
                jaula_id=self.jaula_destino_id,
                defaults={"cantidad_machos": 0, "cantidad_hembras": 0, "activo": True},
            )
            # mover: restar en origen, sumar en destino
            self._sub(origen, m, f)
            self._add(dest, m, f)

    @transaction.atomic
    def save(self, *args, **kwargs):
        creating = self.pk is None
        self.clean()
        super().save(*args, **kwargs)
        if creating:
            self.apply()