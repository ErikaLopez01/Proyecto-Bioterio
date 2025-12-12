# protocolos/models.py
from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL

class Institucion(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Protocolo(models.Model):
    # Metadatos
    ESTADOS = [
        ("borrador", "Borrador"),
        ("enviado", "Enviado"),
        ("aprobado", "Aprobado"),
        ("rechazado", "Rechazado"),
    ]
    creado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name="protocolos")
    estado = models.CharField(max_length=20, choices=ESTADOS, default="borrador")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    # 1) Instituciones donde se realizará el proyecto
    instituciones = models.ManyToManyField(
        Institucion,
        blank=True,
        related_name="protocolos",
        verbose_name="Instituciones donde se realizará el proyecto",
    )
    
    titulo = models.CharField(max_length=200, blank=True)

    # Investigador responsable (nombre/correo/teléfono básicos)
    inv_nombre = models.CharField("Investigador responsable", max_length=200)
    inv_departamento = models.CharField(max_length=200, blank=True)
    inv_telefono = models.CharField(max_length=100, blank=True)
    inv_email = models.EmailField(blank=True)

    # 2) Justificación del experimento y procedimientos
    justificacion = models.TextField()

    # 3) Justificación de la cantidad de animales (principio 3R)
    justificacion_3r = models.TextField()

    # 4) Transporte/movilización
    transporte = models.TextField(blank=True)

    # 6) Tiempo de permanencia de los animales en protocolo
    tiempo_permanencia = models.CharField(max_length=200, blank=True)

    # 8) Descripción detallada de procedimientos (texto libre)
    descripcion_procedimientos = models.TextField(blank=True)

    # 10) Parámetros para conocer anestesia/analgesia
    parametros_anestesia = models.TextField(blank=True)

    # 11) Cuidados pre y post-operatorios
    cuidados_pre_post = models.TextField(blank=True)

    # 12) Punto final humanitario
    punto_final_humano = models.TextField(blank=True)

    # 13) Método de eutanasia
    metodo_eutanasia = models.TextField(blank=True)

    # 14) Riesgo biológico y nivel ABSL
    riesgo_biologico = models.BooleanField(default=False)
    nivel_absl = models.CharField("Nivel de Bioseguridad (ABSL)", max_length=50, blank=True)

    # 15) Destino final de los animales
    destino_animales = models.TextField(blank=True)

    # Totales (puedes calcularlos con señales o en save())
    n_grupos = models.PositiveIntegerField(default=0)
    n_por_grupo = models.PositiveIntegerField(default=0)
    n_total = models.PositiveIntegerField(default=0)

    declaracion_buena_practica = models.BooleanField(default=False, verbose_name="Acepto la declaración de buenas prácticas")
    
    # Observación cuando el protocolo es rechazado
    observacion_rechazo = models.TextField(blank=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return f"Protocolo #{self.pk} - {self.inv_nombre} ({self.get_estado_display()})"

class ProtocoloInvestigador(models.Model):
    """
    Investigadores participantes del protocolo.
    """
    protocolo = models.ForeignKey(
        Protocolo, on_delete=models.CASCADE, related_name="investigadores"
    )
    nombre = models.CharField(max_length=200)
    adscripcion = models.CharField(max_length=200, blank=True, help_text="Unidad/Departamento/Institución")
    rol = models.CharField(max_length=120, blank=True, help_text="Ej.: Responsable, Coinvestigador, Tesista, Técnico")
    correo = models.EmailField(blank=True)

    class Meta:
        verbose_name = "Investigador participante"
        verbose_name_plural = "Investigadores participantes"

    def __str__(self):
        return f"{self.nombre} ({self.rol})"

class ProtocoloAnimal(models.Model):
    """
    Tabla hija para las filas de: especie, cantidad, peso/edad/sexo.
    (punto 5 del formulario)
    """
    SEXOS = [("M", "Macho"), ("H", "Hembra"), ("ND", "No definido")]
    protocolo = models.ForeignKey(Protocolo, on_delete=models.CASCADE, related_name="animales")
    especie = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    rango_peso = models.CharField(max_length=100, blank=True)
    rango_edad = models.CharField(max_length=100, blank=True)
    sexo = models.CharField(max_length=2, choices=SEXOS, default="ND")


class ProcedimientoBase(models.Model):
    nombre = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = "Procedimiento base"
        verbose_name_plural = "Procedimientos base"
        ordering = ["id"]

    def __str__(self):
        return self.nombre

class Procedimiento(models.Model):
    """
    Punto 7 del formulario: checkboxes con detalle/frecuencia.
    """
    protocolo = models.ForeignKey(Protocolo, on_delete=models.CASCADE, related_name="procedimientos")
    nombre = models.ForeignKey(ProcedimientoBase, on_delete=models.PROTECT, null=True, blank=True)
    aplica = models.BooleanField(default=False)        # Sí/No
    detalle = models.CharField(max_length=255, blank=True)  # Frecuencia, vía, cantidad, etc.

    class Meta:
        verbose_name = "Procedimiento"
        verbose_name_plural = "Procedimientos"


class Analgesico(models.Model):
    """
    Punto 9: agentes analgésicos/anestésicos/tranquilizantes.
    """
    protocolo = models.ForeignKey(Protocolo, on_delete=models.CASCADE, related_name="analgesicos")
    tipo = models.CharField(max_length=100, blank=True)       # Analgésico / Anestésico / Tranquilizante
    agente = models.CharField(max_length=150, blank=True)
    dosis = models.CharField(max_length=100, blank=True)
    via = models.CharField("Vía de administración", max_length=100, blank=True)
    frecuencia = models.CharField(max_length=100, blank=True)



