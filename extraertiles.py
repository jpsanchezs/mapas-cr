#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extractor Simple de MBTiles
Doble click en este archivo y sigue las instrucciones
"""

import sqlite3
import os

print("=" * 60)
print("   EXTRACTOR DE MBTILES A CARPETA DE TILES")
print("=" * 60)
print()

# Pedir nombre del archivo
mbtiles_file = input("Nombre del archivo .mbtiles (ej: costarica.mbtiles): ").strip()

# Verificar que existe
if not os.path.exists(mbtiles_file):
    print(f"\n❌ ERROR: No se encuentra el archivo '{mbtiles_file}'")
    print(f"   Asegúrate de que este script está en la misma carpeta que el .mbtiles")
    input("\nPresiona ENTER para salir...")
    exit(1)

# Pedir nombre de carpeta de salida
output_dir = input("Nombre de la carpeta de salida (ej: tiles): ").strip()

# Crear carpeta si no existe
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"\n✓ Carpeta '{output_dir}' creada")
else:
    print(f"\n⚠ La carpeta '{output_dir}' ya existe, se agregarán los tiles ahí")

print(f"\n🔄 Extrayendo tiles de '{mbtiles_file}'...\n")

# Conectar a la base de datos
try:
    conn = sqlite3.connect(mbtiles_file)
    cursor = conn.cursor()
    
    # Contar tiles
    cursor.execute("SELECT COUNT(*) FROM tiles")
    total_tiles = cursor.fetchone()[0]
    print(f"📦 Total de tiles a extraer: {total_tiles}\n")
    
    # Extraer tiles
    cursor.execute("SELECT zoom_level, tile_column, tile_row, tile_data FROM tiles")
    
    count = 0
    for row in cursor:
        zoom, col, row_tms, tile_data = row
        
        # Convertir TMS a XYZ
        max_row = (2 ** zoom) - 1
        row_xyz = max_row - row_tms
        
        # Crear estructura de directorios
        tile_dir = os.path.join(output_dir, str(zoom), str(col))
        os.makedirs(tile_dir, exist_ok=True)
        
        # Guardar tile
        tile_path = os.path.join(tile_dir, f"{row_xyz}.png")
        with open(tile_path, 'wb') as f:
            f.write(tile_data)
        
        count += 1
        
        # Mostrar progreso cada 50 tiles
        if count % 50 == 0:
            percentage = (count * 100) // total_tiles
            print(f"   Progreso: {count}/{total_tiles} tiles ({percentage}%)")
    
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"✅ EXTRACCIÓN COMPLETADA")
    print(f"{'='*60}")
    print(f"   📊 {count} tiles extraídos exitosamente")
    print(f"   📁 Guardados en: {os.path.abspath(output_dir)}")
    print()
    
    # Mostrar estructura
    print("📂 Estructura de carpetas creada:")
    for zoom_dir in sorted(os.listdir(output_dir), key=int):
        zoom_path = os.path.join(output_dir, zoom_dir)
        if os.path.isdir(zoom_path):
            tile_count = sum([len(files) for r, d, files in os.walk(zoom_path)])
            print(f"   Zoom {zoom_dir}: {tile_count} tiles")
    
    print(f"\n✓ Ahora puedes usar la carpeta '{output_dir}' en tu página HTML")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nVerifica que el archivo .mbtiles no esté corrupto")

print()
input("Presiona ENTER para salir...")