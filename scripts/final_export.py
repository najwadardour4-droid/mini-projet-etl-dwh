import shutil
import os

# Le chemin du projet actuel
project_path = r'c:\Users\LENOVO\Documents\trae_projects\Data_engineering'
# Le chemin de destination (votre dossier Documents)
zip_destination = r'C:\Users\LENOVO\Documents\Mexora_Analytics_Project'

try:
    # Créer un fichier ZIP de tout le projet
    shutil.make_archive(zip_destination, 'zip', project_path)
    print(f"✅ Succès ! Tout le projet a été compressé ici : {zip_destination}.zip")
    
    # Créer aussi un dossier simple avec juste les résultats Power BI pour plus de facilité
    export_folder = r'C:\Users\LENOVO\Documents\Mexora_Data_PowerBI'
    if os.path.exists(export_folder):
        shutil.rmtree(export_folder)
    shutil.copytree(os.path.join(project_path, 'export_powerbi'), export_folder)
    print(f"✅ Succès ! Les fichiers CSV pour Power BI sont ici : {export_folder}")

except Exception as e:
    print(f"❌ Erreur : {e}")
