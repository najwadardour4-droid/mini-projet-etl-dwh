import pandas as pd
import numpy as np

def transform_mexora_data():
    print("🧹 Début de la transformation des données...")

    # 1. Chargement
    df_orders = pd.read_csv('mexora_etl/data/commandes_mexora.csv')
    df_clients = pd.read_csv('mexora_etl/data/clients_mexora.csv')
    df_regions = pd.read_csv('mexora_etl/data/regions_maroc.csv')

    # --- A. Nettoyage des Commandes ---
    
    # Standardisation des dates (le plus important !)
    # errors='coerce' va mettre NaT pour les formats bizarres, puis on gère
    df_orders['date_commande'] = pd.to_datetime(df_orders['date_commande'], errors='coerce')
    df_orders = df_orders.dropna(subset=['date_commande']) # Supprimer si la date est vraiment illisible
    
    # Création d'un ID de date propre (YYYYMMDD) pour le lien avec dim_temps
    df_orders['id_date'] = df_orders['date_commande'].dt.strftime('%Y%m%d').astype(int)

    # Normalisation des villes (TNG, Tnja -> Tanger)
    mapping_villes = {
        'tanger': 'Tanger', 'TNG': 'Tanger', 'TANGER': 'Tanger', 'Tnja': 'Tanger',
        'casablanca': 'Casablanca', 'CAS': 'Casablanca',
        'rak': 'Marrakech', 'RAK': 'Marrakech'
    }
    df_orders['ville_livraison'] = df_orders['ville_livraison'].replace(mapping_villes)

    # Supprimer les quantités négatives ou prix nuls
    df_orders = df_orders[df_orders['quantite'] > 0]
    df_orders = df_orders[df_orders['prix_unitaire'] > 0]

    # Gérer les Livreur manquants (Blank -> L000)
    df_orders['id_livreur'] = df_orders['id_livreur'].fillna('L000')

    # --- B. Nettoyage des Clients ---
    
    # Supprimer les doublons sur l'email (on garde le premier)
    df_clients = df_clients.drop_duplicates(subset=['email'])

    # Normalisation du sexe (m/1/Homme -> Homme)
    sexe_map = {
        'm': 'Homme', '1': 'Homme', 'Homme': 'Homme',
        'f': 'Femme', '0': 'Femme', 'Femme': 'Femme'
    }
    df_clients['sexe'] = df_clients['sexe'].map(sexe_map).fillna('Inconnu')

    # Gestion des segments vides
    if 'segment_client' in df_clients.columns:
        df_clients['segment_client'] = df_clients['segment_client'].fillna('Standard')

    # --- C. Vérification de l'Intégrité (Anti-Blank Power BI) ---
    # On ne garde que les commandes dont le client existe vraiment dans notre table Dim_Client
    df_orders = df_orders[df_orders['id_client'].isin(df_clients['id_client'])]

    # 3. Exportation des données propres pour Power BI
    df_orders.to_csv('export_powerbi/fait_ventes_transformed.csv', index=False)
    df_clients.to_csv('export_powerbi/dim_client_transformed.csv', index=False)
    print("✅ Transformation terminée. Les fichiers sont prêts dans 'export_powerbi/'.")

if __name__ == "__main__":
    transform_mexora_data()