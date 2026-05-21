# Mexora Analytics - Pipeline ETL & Data Warehouse

Ce projet implémente un pipeline ETL complet pour transformer les données opérationnelles de Mexora en un entrepôt de données décisionnel sous PostgreSQL.

## Structure du Projet

- `mexora_etl/` : Code source du pipeline Python
  - `extract/` : Extraction des sources (CSV, JSON)
  - `transform/` : Nettoyage et construction des dimensions/faits
  - `load/` : Chargement dans PostgreSQL
  - `config/` : Paramètres de connexion
  - `data/` : Données brutes et référentiels
- `sql/` : Scripts de création du schéma de l'entrepôt
- `scripts/` : Script de génération de données de test
- `RAPPORT_MODELISATION.md` : Justification des choix de modélisation (SCD, granularité)

## Installation

1. Cloner le repository
2. Installer les dépendances :
   ```bash
   pip install -r mexora_etl/requirements.txt
   ```

## Utilisation

1. **Génération des données de test** :
   ```bash
   python scripts/generate_fake_data.py
   ```
2. **Création du schéma SQL** :
   Exécutez le script `sql/schema.sql` dans votre instance PostgreSQL.
3. **Exécution du pipeline ETL** :
   Configurez vos accès DB dans `.env` ou `mexora_etl/config/settings.py`, puis lancez :
   ```bash
   python mexora_etl/main.py
   ```

## Préparation pour Power BI

Les données sont prêtes pour être importées dans Power BI. Vous trouverez les fichiers CSV nettoyés et structurés en schéma en étoile dans le dossier :
👉 `export_powerbi/`

### Fichiers inclus :
- `fait_ventes_transformed.csv` : Table de faits centrale.
- `dim_*.csv` : Tables de dimensions (Temps, Client, Produit, Région, Livreur).

*Note : Pour Power BI, il suffit de charger ces fichiers et de recréer les relations basées sur les clés (id_client, sk_produit, id_region, etc.).*

## Choix Techniques

- **Modélisation** : Schéma en étoile pour optimiser les performances des requêtes analytiques.
- **SCD** : Type 2 pour la dimension Produit afin de préserver l'historique des catégories.
- **ETL** : Approche modulaire en Python avec Pandas pour la manipulation des données.
