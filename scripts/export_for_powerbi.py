import shutil
import os

source_dir = 'mexora_etl/data'
dest_dir = 'export_powerbi'

files_to_copy = [
    'fait_ventes_transformed.csv',
    'dim_temps_transformed.csv',
    'dim_region_transformed.csv',
    'dim_client_transformed.csv',
    'dim_produit_transformed.csv',
    'dim_livreur_transformed.csv'
]

for file_name in files_to_copy:
    src = os.path.join(source_dir, file_name)
    dst = os.path.join(dest_dir, file_name)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Copié: {file_name}")
    else:
        print(f"Erreur: {file_name} n'existe pas dans {source_dir}")
