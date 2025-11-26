from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction

class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

class Insumo(models.Model):
    UNIDADES = [
        ("unid", "Unidad"),
        ("kg", "Kilogramo"),
        ("g", "Gramo"),
        ("l", "Litro"),
        ("ml", "Mililitro"),
    ]
    nombre = models.CharField(max_length=120, unique=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="insumos")
    unidad = models.CharField(max_length=10, choices=UNIDADES, default="unid")
    stock_actual = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0"))
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0"))
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

class MovimientoInsumo(models.Model):
    ENTRADA = "ENTRADA"
    SALIDA = "SALIDA"
    AJUSTE = "AJUSTE"
    TIPOS = [(ENTRADA, "Entrada"), (SALIDA, "Salida"), (AJUSTE, "Ajuste")]

    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name="movimientos")
    tipo = models.CharField(max_length=10, choices=TIPOS)
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)
    motivo = models.CharField(max_length=200, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(getattr(settings, "AUTH_USER_MODEL", "auth.User"),
                                on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-fecha"]

    def clean(self):
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser positiva.")

    def apply_to_stock(self, insumo: Insumo):
        if self.tipo == self.ENTRADA:
            insumo.stock_actual += self.cantidad
        elif self.tipo == self.SALIDA:
            if insumo.stock_actual - self.cantidad < 0:
                raise ValidationError("Stock insuficiente para realizar la salida.")
            insumo.stock_actual -= self.cantidad
        else:  # AJUSTE (cantidad puede sumar o restar según signo; usamos positiva y este caso no resta ni suma automática)
            # Para simplificar: tratamos AJUSTE como 'set' relativo: +cantidad agrega, -cantidad restaría.
            # Pero como validamos positiva arriba, lo usamos como suma/resta según motivo. Aquí tomamos como suma.
            insumo.stock_actual += self.cantidad

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.clean()
        creating = self.pk is None
        super().save(*args, **kwargs)
        if creating:
            insumo = Insumo.objects.select_for_update().get(pk=self.insumo_id)
            self.apply_to_stock(insumo)
            insumo.save()
