import time
import anthropic
from django.core.management.base import BaseCommand
from myapp.models import articulos


EMPRESA_MAESTRA = 2


def generar_descripcion(client, nombre_producto):
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Generá una descripción SEO corta (2 oraciones, máximo 150 palabras) "
                    f"para el siguiente producto de una gomería y distribuidora de neumáticos argentina: '{nombre_producto}'. "
                    f"La descripción debe mencionar el producto, sus características técnicas inferidas del nombre, "
                    f"y que está disponible en Gomería y Distribuidora Silva, Paso del Rey, Buenos Aires. "
                    f"Respondé solo con la descripción, sin comillas ni explicaciones."
                )
            }
        ]
    )
    return message.content[0].text.strip()


class Command(BaseCommand):
    help = 'Genera descripciones SEO con Claude Haiku para los artículos de empresa 2 y las replica al resto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--solo-empresa-2',
            action='store_true',
            help='Solo genera descripciones para empresa 2, sin replicar',
        )
        parser.add_argument(
            '--solo-replicar',
            action='store_true',
            help='Solo replica desde empresa 2 al resto, sin llamar a la API',
        )

    def handle(self, *args, **kwargs):
        solo_empresa_2 = kwargs['solo_empresa_2']
        solo_replicar = kwargs['solo_replicar']

        client = anthropic.Anthropic()  # toma ANTHROPIC_API_KEY del entorno

        if not solo_replicar:
            self.generar_para_empresa_maestra(client)

        if not solo_empresa_2:
            self.replicar_a_otras_empresas()

    def generar_para_empresa_maestra(self, client):
        pendientes = articulos.objects.filter(
            idempresa=EMPRESA_MAESTRA,
            descripcion_seo__isnull=True
        ).order_by('id')

        total = pendientes.count()
        self.stdout.write(f"Productos pendientes en empresa {EMPRESA_MAESTRA}: {total}")

        for i, articulo in enumerate(pendientes, 1):
            try:
                descripcion = generar_descripcion(client, articulo.descripcion)
                articulo.descripcion_seo = descripcion
                articulo.save(update_fields=['descripcion_seo'])
                self.stdout.write(f"[{i}/{total}] ✓ {articulo.descripcion[:60]}")
                time.sleep(0.3)  # evitar rate limiting

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"[{i}/{total}] ✗ {articulo.descripcion[:60]} — Error: {e}")
                )
                continue

        self.stdout.write(self.style.SUCCESS("✅ Generación empresa maestra completada."))

    def replicar_a_otras_empresas(self):
        self.stdout.write("Replicando descripciones a otras empresas...")

        # Mapa nombre -> descripcion_seo de empresa maestra
        maestra = articulos.objects.filter(
            idempresa=EMPRESA_MAESTRA,
            descripcion_seo__isnull=False
        ).values('descripcion', 'descripcion_seo')

        mapa = {item['descripcion']: item['descripcion_seo'] for item in maestra}

        otras = articulos.objects.exclude(
            idempresa=EMPRESA_MAESTRA
        ).filter(descripcion_seo__isnull=True)

        actualizados = 0
        no_encontrados = 0

        for articulo in otras:
            seo = mapa.get(articulo.descripcion)
            if seo:
                articulo.descripcion_seo = seo
                articulo.save(update_fields=['descripcion_seo'])
                actualizados += 1
            else:
                no_encontrados += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Replicados: {actualizados} | Sin match: {no_encontrados}"))