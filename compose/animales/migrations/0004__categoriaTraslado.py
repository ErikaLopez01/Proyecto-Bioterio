from django.db import migrations, models

# ---- Mapear 'tipo' viejo -> (categoria, motivo) nuevos ----
def map_tipo_to_cat_mot(tipo: str):
    ING_NAC = "INGRESO_NACIMIENTO"
    ING_COM = "INGRESO_COMPRA"
    SAL_VEN = "SALIDA_VENTA"
    SAL_PRO = "SALIDA_PROTOCOLO"
    SAL_EUT = "SALIDA_EUTANASIA"
    SAL_MUE = "SALIDA_MUERTE"
    AJU_POS = "AJUSTE_POSITIVO"
    AJU_NEG = "AJUSTE_NEGATIVO"
    TRASLADO = "TRASLADO"

    CAT_ING, CAT_SAL, CAT_AJU, CAT_TRA = "ING", "SAL", "AJU", "TRA"
    MOT_NAC, MOT_COM, MOT_VEN, MOT_EUT, MOT_MUE, MOT_PRO, MOT_APO, MOT_ANE, MOT_TRA = \
        "NAC", "COM", "VEN", "EUT", "MUE", "PRO", "APO", "ANE", "TRA"

    mapping = {
        ING_NAC: (CAT_ING, MOT_NAC),
        ING_COM: (CAT_ING, MOT_COM),
        SAL_VEN: (CAT_SAL, MOT_VEN),
        SAL_PRO: (CAT_SAL, MOT_PRO),
        SAL_EUT: (CAT_SAL, MOT_EUT),
        SAL_MUE: (CAT_SAL, MOT_MUE),
        AJU_POS: (CAT_AJU, MOT_APO),
        AJU_NEG: (CAT_AJU, MOT_ANE),
        TRASLADO: (CAT_TRA, MOT_TRA),
    }
    return mapping.get(tipo, (None, None))

def forwards(apps, schema_editor):
    MovimientoGrupo = apps.get_model("animales", "MovimientoGrupo")
    GrupoAnimal = apps.get_model("animales", "GrupoAnimal")

    # Poblar categoria/motivo/jaula_destino a partir de campos viejos
    for m in MovimientoGrupo.objects.all().iterator():
        # 'tipo' existe todavía en este punto (porque lo quitamos al final)
        tipo = getattr(m, "tipo", None)
        cat, mot = map_tipo_to_cat_mot(tipo)
        m.categoria = cat
        # Ojo: 'motivo' ya existe desde 0001 (era Char(200)); aquí lo ponemos en código de 3 letras
        if mot:
            m.motivo = mot

        # Si antes era traslado, llevar grupo_destino -> jaula_destino
        if cat == "TRA" and hasattr(m, "grupo_destino_id") and m.grupo_destino_id:
            try:
                gd = GrupoAnimal.objects.get(pk=m.grupo_destino_id)
                m.jaula_destino_id = gd.jaula_id
            except GrupoAnimal.DoesNotExist:
                m.jaula_destino_id = None

        m.save()

def backwards(apps, schema_editor):
    # No se intenta reconstruir 'tipo' desde (categoria, motivo)
    pass


class Migration(migrations.Migration):

    dependencies = [
        # IMPORTANTÍSIMO: que dependa de 0002, no de la vieja 0003
        ("animales", "0002_alter_grupoanimal_options_alter_jaula_options_and_more"),
        ("protocolos", "0001_initial"),
    ]

    operations = [
        # 1) Añadir nuevos campos como NULL/blank primero (sin defaults)
        migrations.AddField(
            model_name="movimientogrupo",
            name="categoria",
            field=models.CharField(max_length=3, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="movimientogrupo",
            name="jaula_destino",
            field=models.ForeignKey(
                to="animales.jaula", on_delete=models.PROTECT,
                null=True, blank=True,
                help_text="Requerido si la categoría es 'Traslado'.",
            ),
        ),
        migrations.AddField(
            model_name="movimientogrupo",
            name="observacion",
            field=models.CharField(max_length=200, blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="movimientogrupo",
            name="protocolo",
            field=models.ForeignKey(
                to="protocolos.protocolo", on_delete=models.PROTECT,
                null=True, blank=True,
            ),
        ),

        # 2) Data migration: setear categoria/motivo/jaula_destino
        migrations.RunPython(forwards, backwards),

        # 3) Ahora que 'motivo' ya contiene códigos de 3 letras, achicar el campo
        migrations.AlterField(
            model_name="movimientogrupo",
            name="motivo",
            field=models.CharField(max_length=3),
        ),

        # 4) Eliminar campos viejos
        migrations.RemoveField(model_name="movimientogrupo", name="tipo"),
        migrations.RemoveField(model_name="movimientogrupo", name="grupo_destino"),

        # 5) Volver obligatoria 'categoria'
        migrations.AlterField(
            model_name="movimientogrupo",
            name="categoria",
            field=models.CharField(max_length=3),
        ),
    ]
