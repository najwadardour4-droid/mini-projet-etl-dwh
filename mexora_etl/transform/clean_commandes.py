import pandas as pd
import logging

def transform_commandes(df: pd.DataFrame, regions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique l'ensemble des règles de nettoyage sur les commandes Mexora.
    """
    if df.empty:
        return df
        
    initial = len(df)

    # R1 — Suppression des doublons
    df = df.drop_duplicates(subset=['id_commande'], keep='last')
    logging.info(f"[TRANSFORM] R1 doublons: {initial - len(df)} lignes supprimées")

    # R2 — Standardisation des dates
    df['date_commande'] = pd.to_datetime(
        df['date_commande'], format='mixed', dayfirst=True, errors='coerce'
    )
    dates_invalides = df['date_commande'].isna().sum()
    df = df.dropna(subset=['date_commande'])
    logging.info(f"[TRANSFORM] R2 dates: {dates_invalides} dates invalides supprimées")

    # R3 — Harmonisation des villes
    # On utilise regions_maroc pour mapper les noms de villes
    mapping_villes = {
        'tng': 'Tanger', 'tanger': 'Tanger', 'tanger ': 'Tanger', 'tnja': 'Tanger',
        'cas': 'Casablanca', 'casa': 'Casablanca', 'casablanca': 'Casablanca',
        'rak': 'Marrakech', 'marrakech': 'Marrakech',
        'rab': 'Rabat', 'rabat': 'Rabat',
        'fez': 'Fès', 'fes': 'Fès', 'fès': 'Fès',
        'aga': 'Agadir', 'agadir': 'Agadir',
        'ouj': 'Oujda', 'oujda': 'Oujda',
        'mek': 'Meknès', 'meknes': 'Meknès', 'meknès': 'Meknès'
    }
    
    df['ville_livraison'] = df['ville_livraison'].str.strip().str.lower().replace(mapping_villes)
    
    # R4 — Standardisation des statuts
    mapping_statuts = {
        'livré': 'livré', 'livre': 'livré', 'LIVRE': 'livré', 'DONE': 'livré',
        'annulé': 'annulé', 'annule': 'annulé', 'KO': 'annulé',
        'en_cours': 'en_cours', 'OK': 'en_cours',
        'retourné': 'retourné', 'retourne': 'retourné'
    }
    df['statut'] = df['statut'].replace(mapping_statuts)
    invalides = ~df['statut'].isin(['livré', 'annulé', 'en_cours', 'retourné'])
    df.loc[:, 'date_commande'] = pd.to_datetime(df['date_commande'], errors='coerce')
    df.loc[invalides, 'statut'] = 'inconnu'

    # R5 — Quantités invalides
    avant = len(df)
    df['quantite'] = pd.to_numeric(df['quantite'], errors='coerce')
    df = df[df['quantite'] > 0]
    logging.info(f"[TRANSFORM] R5 quantités: {avant - len(df)} lignes supprimées (quantité <= 0)")

    # R6 — Prix nuls (commandes test)
    avant = len(df)
    df['prix_unitaire'] = pd.to_numeric(df['prix_unitaire'], errors='coerce')
    df = df[df['prix_unitaire'] > 0]
    logging.info(f"[TRANSFORM] R6 prix: {avant - len(df)} commandes test supprimées")

    # R7 — Livreurs manquants
    nb_manquants = df['id_livreur'].isna().sum()
    df['id_livreur'] = df['id_livreur'].fillna('-1')
    logging.info(f"[TRANSFORM] R7 livreurs: {nb_manquants} valeurs manquantes remplacées par -1")

    logging.info(f"[TRANSFORM] Commandes final: {len(df)} lignes")
    return df
