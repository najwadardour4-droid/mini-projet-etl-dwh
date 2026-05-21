import pandas as pd
import logging

def transform_produits(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique les règles de nettoyage sur les produits Mexora.
    """
    if df.empty:
        return df
        
    initial = len(df)

    # Standardisation des catégories (casse)
    df['categorie'] = df['categorie'].str.strip().str.capitalize()
    
    # Gestion des prix nuls/manquants
    df['prix_catalogue'] = pd.to_numeric(df['prix_catalogue'], errors='coerce')
    median_price = df['prix_catalogue'].median()
    df['prix_catalogue'] = df['prix_catalogue'].fillna(median_price)
    
    logging.info(f"[TRANSFORM] Produits final: {len(df)} lignes")
    return df
