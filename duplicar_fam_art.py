# scripts/duplicar_empresa.py

import os
import sys
import django

# 1️⃣ Inicializar Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disilva.settings')
django.setup()

# 2️⃣ Imports del proyecto
from django.db import transaction
from myapp.models import empresas, familias, articulos


def duplicar_empresa(empresa_origen_id, empresa_destino_id):
    empresa_origen = empresas.objects.get(id=empresa_origen_id)
    empresa_destino = empresas.objects.get(id=empresa_destino_id)

    print(f"Duplicando datos de {empresa_origen} → {empresa_destino}")

    # 🔹 1. Familias
    familias_origen = familias.objects.filter(idempresa=empresa_origen)
    familia_map = {}

    with transaction.atomic():
        for fam in familias_origen:
            old_id = fam.id
            fam.pk = None
            fam.idempresa = empresa_destino
            fam.save()
            familia_map[old_id] = fam

        # 🔹 2. Artículos
        articulos_origen = articulos.objects.filter(idempresa=empresa_origen)

        for art in articulos_origen:
            art.pk = None
            art.idempresa = empresa_destino
            art.familia = familia_map.get(art.familia_id)
            art.save()

    print("✔ Duplicación finalizada correctamente")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python duplicar_empresa.py <empresa_origen_id> <empresa_destino_id>")
        sys.exit(1)

    duplicar_empresa(int(sys.argv[1]), int(sys.argv[2]))