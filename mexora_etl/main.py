import logging
import sys
import os
import urllib.parse
from datetime import datetime
from sqlalchemy import create_engine

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from extract.extractor import extract_commandes, extract_produits, extract_clients, extract_regions
from transform.clean_commandes import transform_commandes
from transform.clean_clients import transform_clients, calculate_segments
from transform.clean_produits import transform_produits
from transform.build_dimensions import build_dim_temps, build_dim_region, build_dim_livreur, build_fait_ventes
from load.loader import charger_dimension, charger_faits

# Configure logging
os.makedirs('mexora_etl/logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'mexora_etl/logs/etl_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

def run_pipeline():
    start_time = datetime.now()
    logging.info("=" * 60)
    logging.info("DÉMARRAGE DU PIPELINE ETL MEXORA")
    logging.info("=" * 60)

    try:
        # 1. EXTRACT
        logging.info("--- PHASE EXTRACT ---")
        df_commandes_raw = extract_commandes(settings.COMMANDES_PATH)
        df_produits_raw = extract_produits(settings.PRODUITS_PATH)
        df_clients_raw = extract_clients(settings.CLIENTS_PATH)
        df_regions_raw = extract_regions(settings.REGIONS_PATH)

        # 2. TRANSFORM
        logging.info("--- PHASE TRANSFORM ---")
        df_commandes = transform_commandes(df_commandes_raw, df_regions_raw)
        df_clients = transform_clients(df_clients_raw)
        df_produits = transform_produits(df_produits_raw)
        df_clients = calculate_segments(df_clients, df_commandes)
        
        logging.info("--- CONSTRUCTION DES DIMENSIONS ---")
        dim_temps = build_dim_temps('2024-01-01', '2025-12-31')
        dim_region = build_dim_region(df_regions_raw)
        dim_livreur = build_dim_livreur(df_commandes)
        
        dim_client = df_clients[['id_client', 'nom_complet', 'email', 'tranche_age', 'sexe', 'ville', 'segment_client', 'canal_acquisition']].copy()
        dim_client = dim_client.merge(dim_region[['ville', 'region_admin']], on='ville', how='left').rename(columns={'region_admin': 'region'})
        
        dim_produit = df_produits.copy()
        dim_produit.columns = ['id_produit', 'nom_produit', 'categorie', 'sous_categorie', 'marque', 'fournisseur', 'prix_standard', 'origine_pays', 'date_creation', 'actif']
        dim_produit['sk_produit'] = range(1, len(dim_produit) + 1)
        dim_produit['date_debut'] = '2024-01-01'
        dim_produit['date_fin'] = None
        dim_produit['est_actuel'] = True
        
        logging.info("--- CONSTRUCTION DE LA TABLE DE FAITS ---")
        fait_ventes = build_fait_ventes(df_commandes, dim_produit, dim_region)

        # 3. LOAD
        logging.info("--- PHASE LOAD ---")
        try:
            # FIX: Encoding du mot de passe avec @ (najwa@123)
            # On extrait les composants de l'URL pour encoder uniquement le mot de passe
            raw_url = settings.DATABASE_URL
            # Format attendu: postgresql://user:password@host:port/dbname
            prefix, rest = raw_url.split("://")
            user_pass, host_port_db = rest.rsplit("@", 1)
            user, password = user_pass.split(":", 1)
            
            safe_password = urllib.parse.quote_plus(password)
            final_url = f"{prefix}://{user}:{safe_password}@{host_port_db}"
            
            engine = create_engine(final_url)
            
            charger_dimension(dim_temps, 'dim_temps', engine)
            charger_dimension(dim_region, 'dim_region', engine)
            charger_dimension(dim_livreur, 'dim_livreur', engine)
            charger_dimension(dim_client, 'dim_client', engine)
            charger_dimension(dim_produit, 'dim_produit', engine)
            charger_faits(fait_ventes, 'fait_ventes', engine)
            
            logging.info("Chargement terminé avec succès dans PostgreSQL")
        except Exception as db_err:
            logging.error(f"Erreur de connexion DB: {db_err}")
            logging.info("Sauvegarde des données en local (CSV) suite à l'échec de la connexion DB...")
            
            os.makedirs(settings.DATA_DIR, exist_ok=True)
            fait_ventes.to_csv(os.path.join(settings.DATA_DIR, 'fait_ventes_transformed.csv'), index=False)
            dim_temps.to_csv(os.path.join(settings.DATA_DIR, 'dim_temps_transformed.csv'), index=False)
            dim_region.to_csv(os.path.join(settings.DATA_DIR, 'dim_region_transformed.csv'), index=False)
            dim_client.to_csv(os.path.join(settings.DATA_DIR, 'dim_client_transformed.csv'), index=False)
            dim_produit.to_csv(os.path.join(settings.DATA_DIR, 'dim_produit_transformed.csv'), index=False)
            dim_livreur.to_csv(os.path.join(settings.DATA_DIR, 'dim_livreur_transformed.csv'), index=False)

        end_time = datetime.now()
        duration = end_time - start_time
        logging.info("=" * 60)
        logging.info(f"PIPELINE TERMINÉ EN {duration}")
        logging.info("=" * 60)

    except Exception as e:
        logging.error(f"ÉCHEC DU PIPELINE: {e}", exc_info=True)

if __name__ == "__main__":
    run_pipeline()