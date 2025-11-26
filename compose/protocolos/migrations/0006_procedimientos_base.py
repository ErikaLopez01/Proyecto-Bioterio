from django.db import migrations, models

PROC_NOMBRES = [
    "Manipulación de la dieta y del agua",
    "Toma de muestras biológicas",
    "Colocación de cánulas y sondas",
    "Observación/modificación de conducta",
    "Inoculaciones de agentes biológicos/químicos",
    "Procedimientos quirúrgicos con recuperación",
    "Procedimientos quirúrgicos sin recuperación",
    "Uso de adyuvantes",
    "Restricción física",
    "Confinamiento o aislamiento",
    "Producción de anticuerpos",
    "Inducción de lesiones",
    "Agentes teratogénicos o carcinogénicos",
    "Administración de sustancias químicas tóxicas",
    "Implantes o injertos",
    "Otros",
]

def crear_procedimientos_base(apps, schema_editor):
    ProcedimientoBase = apps.get_model("protocolos", "ProcedimientoBase")
    for nombre in PROC_NOMBRES:
        ProcedimientoBase.objects.get_or_create(nombre=nombre)

class Migration(migrations.Migration):

    dependencies = [
        ("protocolos", "0005_procedimientobase_alter_procedimiento_nombre"),  # ajusta este nombre
    ]

    operations = [
        migrations.RunPython(crear_procedimientos_base, migrations.RunPython.noop),
    ]
