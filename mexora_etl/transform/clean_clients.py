import pandas as pd
import logging
import re
from datetime import date

def transform_clients(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique les règles de nettoyage sur les clients Mexora.
    """
    if df.empty:
        return df
        
    initial = len(df)

    # R1 — Déduplication sur email normalisé
    df['email_norm'] = df['email'].str.lower().str.strip()
    df['date_inscription'] = pd.to_datetime(df['date_inscription'], errors='coerce')
    df = df.sort_values('date_inscription').drop_duplicates(subset=['email_norm'], keep='last')
    logging.info(f"[TRANSFORM] R1 déduplication clients: {initial - len(df)} doublons supprimés")

    # R2 — Standardisation du sexe
    mapping_sexe = {
        'm': 'm', 'f': 'f', '1': 'm', '0': 'f',
        'homme': 'm', 'femme': 'f', 'male': 'm', 'female': 'f',
        'h': 'm'
    }
    df['sexe'] = df['sexe'].str.lower().str.strip().map(mapping_sexe).fillna('inconnu')

    # R3 — Validation des dates de naissance
    df['date_naissance'] = pd.to_datetime(df['date_naissance'], errors='coerce')
    today = pd.Timestamp(date.today())
    df['age'] = (today - df['date_naissance']).dt.days // 365
    
    # Validation âge entre 16 et 100 ans
    df.loc[(df['age'] < 16) | (df['age'] > 100), 'date_naissance'] = pd.NaT
    df['age'] = (today - df['date_naissance']).dt.days // 365
    
    # Tranches d'âge
    df['tranche_age'] = pd.cut(
        df['age'].fillna(0),
        bins=[0, 18, 25, 35, 45, 55, 65, 200],
        labels=['<18', '18-24', '25-34', '35-44', '45-54', '55-64', '65+']
    )

    # R4 — Validation email
    pattern_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    df.loc[~df['email'].str.match(pattern_email, na=False), 'email'] = None
    
    # Concaténation nom complet
    df['nom_complet'] = df['prenom'] + " " + df['nom']

    logging.info(f"[TRANSFORM] Clients final: {len(df)} lignes")
    return df

def calculate_segments(df_clients: pd.DataFrame, df_commandes: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule le segment client basé sur le CA des 12 derniers mois.
    """
    from datetime import timedelta
    
    date_limite = pd.Timestamp(date.today() - timedelta(days=365))
    
    df_recents = df_commandes[
        (df_commandes['date_commande'] >= date_limite) & 
        (df_commandes['statut'] == 'livré')
    ].copy()
    
    df_recents['montant_ttc'] = df_recents['quantite'] * df_recents['prix_unitaire']
    ca_par_client = df_recents.groupby('id_client')['montant_ttc'].sum().reset_index()
    ca_par_client.columns = ['id_client', 'ca_12m']
    
    def segmenter(ca):
        if ca >= 15000: return 'Gold'
        elif ca >= 5000: return 'Silver'
        else: return 'Bronze'
        
    ca_par_client['segment_client'] = ca_par_client['ca_12m'].apply(segmenter)
    
    # Joindre avec le dataframe client
    df_final = df_clients.merge(ca_par_client, on='id_client', how='left')
    df_final['segment_client'] = df_final['segment_client'].fillna('Bronze')
    
    return df_final
