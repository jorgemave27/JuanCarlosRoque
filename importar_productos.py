import os
import django
import pandas as pd

# 1) Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carlos_roque.settings")
django.setup()

from sistema.models import Producto

def importar_productos():
    # 2) Nombre del archivo (debe estar junto a manage.py)
    archivo = "productos_jc.xlsx"

    # 3) Leer el Excel
    #   header=1 porque la fila 0 tiene los títulos "CLAVE, DESCRIPCION, PRECIO CJA, PRECIO PZ"
    df = pd.read_excel(archivo, header=1)

    # 4) Recorrer filas e insertar en la BD
    for _, row in df.iterrows():
        clave = row.get("CLAVE")
        descripcion = row.get("DESCRIPCION")
        precio_caja = row.get("PRECIO CJA")
        precio_pieza = row.get("PRECIO PZ")

        # Si no hay clave o descripción, saltamos la fila
        if pd.isna(clave) and pd.isna(descripcion):
            continue

        Producto.objects.create(
            clave=clave,
            descripcion=descripcion,
            precio_caja=precio_caja,
            precio_pieza=precio_pieza,
        )

    print("✅ Productos importados correctamente.")

if __name__ == "__main__":
    importar_productos()

