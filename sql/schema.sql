-- Schéma de l'entrepôt de données Mexora Analytics

-- Création du schéma
CREATE SCHEMA IF NOT EXISTS dwh_mexora;

-- Table de dimension Temps
CREATE TABLE dwh_mexora.dim_temps (
    id_date INTEGER PRIMARY KEY,
    date_complete DATE,
    jour INTEGER,
    mois INTEGER,
    trimestre INTEGER,
    annee INTEGER,
    semaine INTEGER,
    libelle_jour VARCHAR(20),
    libelle_mois VARCHAR(20),
    est_weekend BOOLEAN,
    est_ferie_maroc BOOLEAN,
    periode_ramadan BOOLEAN
);

-- Table de dimension Région
CREATE TABLE dwh_mexora.dim_region (
    id_region SERIAL PRIMARY KEY,
    code_ville VARCHAR(10),
    ville VARCHAR(100),
    province VARCHAR(100),
    region_admin VARCHAR(100),
    zone_geo VARCHAR(50)
);

-- Table de dimension Produit (SCD Type 2)
CREATE TABLE dwh_mexora.dim_produit (
    sk_produit SERIAL PRIMARY KEY, -- Clé de substitution
    id_produit VARCHAR(20),        -- Clé naturelle
    nom_produit VARCHAR(255),
    categorie VARCHAR(100),
    sous_categorie VARCHAR(100),
    marque VARCHAR(100),
    fournisseur VARCHAR(100),
    prix_standard DECIMAL(12, 2),
    origine_pays VARCHAR(100),
    date_debut DATE,
    date_fin DATE,
    est_actuel BOOLEAN
);

-- Table de dimension Client
CREATE TABLE dwh_mexora.dim_client (
    id_client VARCHAR(20) PRIMARY KEY,
    nom_complet VARCHAR(255),
    email VARCHAR(255),
    tranche_age VARCHAR(20),
    sexe VARCHAR(20),
    ville VARCHAR(100),
    region VARCHAR(100),
    segment_client VARCHAR(50),
    canal_acquisition VARCHAR(100)
);

-- Table de dimension Livreur
CREATE TABLE dwh_mexora.dim_livreur (
    id_livreur VARCHAR(20) PRIMARY KEY,
    nom_livreur VARCHAR(255),
    type_transport VARCHAR(100),
    zone_couverture VARCHAR(100)
);

-- Table de faits Ventes
CREATE TABLE dwh_mexora.fait_ventes (
    id_vente SERIAL PRIMARY KEY,
    id_commande VARCHAR(20),
    id_date INTEGER REFERENCES dwh_mexora.dim_temps(id_date),
    id_client VARCHAR(20) REFERENCES dwh_mexora.dim_client(id_client),
    sk_produit INTEGER REFERENCES dwh_mexora.dim_produit(sk_produit),
    id_region INTEGER REFERENCES dwh_mexora.dim_region(id_region),
    id_livreur VARCHAR(20) REFERENCES dwh_mexora.dim_livreur(id_livreur),
    quantite INTEGER,
    prix_unitaire DECIMAL(12, 2),
    montant_ttc DECIMAL(12, 2),
    statut VARCHAR(50)
);

-- Index pour optimiser les performances
CREATE INDEX idx_fait_ventes_date ON dwh_mexora.fait_ventes(id_date);
CREATE INDEX idx_fait_ventes_client ON dwh_mexora.fait_ventes(id_client);
CREATE INDEX idx_fait_ventes_produit ON dwh_mexora.fait_ventes(sk_produit);
CREATE INDEX idx_fait_ventes_region ON dwh_mexora.fait_ventes(id_region);
CREATE INDEX idx_fait_ventes_statut ON dwh_mexora.fait_ventes(statut);

-- Vues matérialisées pour la performance
-- Rapport de CA par région et mois (très utilisé par le DG)
CREATE MATERIALIZED VIEW dwh_mexora.mv_ca_region_mensuel AS
SELECT 
    r.region_admin,
    t.annee,
    t.mois,
    t.libelle_mois,
    SUM(f.montant_ttc) as ca_total,
    COUNT(DISTINCT f.id_commande) as nb_commandes
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_region r ON f.id_region = r.id_region
JOIN dwh_mexora.dim_temps t ON f.id_date = t.id_date
WHERE f.statut = 'livré'
GROUP BY r.region_admin, t.annee, t.mois, t.libelle_mois;

-- Index sur la vue matérialisée
CREATE INDEX idx_mv_ca_region_date ON dwh_mexora.mv_ca_region_mensuel(annee, mois);

-- Procédure de rafraîchissement des vues (à programmer après l'ETL)
-- REFRESH MATERIALIZED VIEW dwh_mexora.mv_ca_region_mensuel;
