import pandas as pd
import logging
from datetime import datetime

def build_dim_temps(date_debut: str, date_fin: str) -> pd.DataFrame:
    """Génère la dimension temporelle."""
    dates = pd.date_range(start=date_debut, end=date_fin, freq='D')
    
    feries_maroc = [
        '2024-01-01', '2024-01-11', '2024-05-01', '2024-07-30',
        '2024-08-14', '2024-11-06', '2024-11-18',
        '2025-01-01', '2025-01-11', '2025-05-01', '2025-07-30'
    ]
    
    ramadan_periodes = [
        ('2024-03-10', '2024-04-09'),
        ('2025-02-28', '2025-03-30')
    ]
    
    df = pd.DataFrame({
        'id_date': dates.strftime('%Y%m%d').astype(int),
        'date_complete': dates,
        'jour': dates.day,
        'mois': dates.month,
        'trimestre': dates.quarter,
        'annee': dates.year,
        'semaine': dates.isocalendar().week,
        'libelle_jour': dates.strftime('%A'),
        'libelle_mois': dates.strftime('%B'),
        'est_weekend': dates.dayofweek >= 5,
        'est_ferie_maroc': dates.strftime('%Y-%m-%d').isin(feries_maroc)
    })
    
    df['periode_ramadan'] = False
    for debut, fin in ramadan_periodes:
        # Conversion explicite en datetime pour la comparaison
        debut_dt = pd.to_datetime(debut)
        fin_dt = pd.to_datetime(fin)
        mask = (df['date_complete'] >= debut_dt) & (df['date_complete'] <= fin_dt)
        df.loc[mask, 'periode_ramadan'] = True
        
    nb_jours_ramadan = df['periode_ramadan'].sum()
    logging.info(f"[DIM_TEMPS] {nb_jours_ramadan} jours marqués comme période Ramadan.")
        
    return df

def build_dim_region(regions_df: pd.DataFrame) -> pd.DataFrame:
    """Prépare la dimension région."""
    df = regions_df.copy()
    df.columns = ['code_ville', 'ville', 'province', 'region_admin', 'zone_geo', 'population', 'code_postal']
    return df[['code_ville', 'ville', 'province', 'region_admin', 'zone_geo']]

def build_dim_livreur(df_commandes: pd.DataFrame) -> pd.DataFrame:
    """Construit la dimension livreur à partir des commandes."""
    livreurs = df_commandes[['id_livreur']].drop_duplicates()
    livreurs = livreurs[livreurs['id_livreur'] != '-1']
    
    df = pd.DataFrame({
        'id_livreur': livreurs['id_livreur'],
        'nom_livreur': 'Livreur ' + livreurs['id_livreur'],
        'type_transport': 'Moto',
        'zone_couverture': 'Nationale'
    })
    
    # Ajouter le livreur inconnu
    inconnu = pd.DataFrame({
        'id_livreur': ['-1'],
        'nom_livreur': ['Livreur Inconnu'],
        'type_transport': ['Inconnu'],
        'zone_couverture': ['Inconnu']
    })
    
    return pd.concat([df, inconnu], ignore_index=True)

def build_fait_ventes(df_commandes: pd.DataFrame, dim_produit: pd.DataFrame, dim_region: pd.DataFrame) -> pd.DataFrame:
    """Construit la table de faits."""
    df = df_commandes.copy()
    
    # Mapping date_commande vers id_date
    df['id_date'] = df['date_commande'].dt.strftime('%Y%m%d').astype(int)
    
    # Join with dim_produit to get sk_produit
    # For simplicity, we use id_produit and take the current version
    df = df.merge(dim_produit[dim_produit['est_actuel'] == True][['id_produit', 'sk_produit']], on='id_produit', how='left')
    
    # Join with dim_region to get id_region
    # In a real case, we'd map ville_livraison to dim_region.id_region
    # Here we'll just use the index for now or assume a match on ville
    df = df.merge(dim_region.reset_index().rename(columns={'index': 'id_region'}), left_on='ville_livraison', right_on='ville', how='left')
    
    df['id_region'] = df['id_region'].fillna(0).astype(int)
    df['sk_produit'] = df['sk_produit'].fillna(0).astype(int)
    
    # Calcul montant_ttc
    df['montant_ttc'] = df['quantite'] * df['prix_unitaire']
    
    return df[['id_commande', 'id_date', 'id_client', 'sk_produit', 'id_region', 'id_livreur', 'quantite', 'prix_unitaire', 'montant_ttc', 'statut']]
