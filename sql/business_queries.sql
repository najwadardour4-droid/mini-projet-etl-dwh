-- Requêtes décisionnelles pour Mexora Analytics

-- R1 : Quelle région génère le plus de CA ?
-- Analyse : Chiffre d'affaires total par région administrative
SELECT 
    r.region_admin,
    SUM(f.montant_ttc) as ca_total
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_region r ON f.id_region = r.id_region
WHERE f.statut = 'livré'
GROUP BY r.region_admin
ORDER BY ca_total DESC;

-- R2 : Évolution du CA sur les 12 derniers mois
SELECT 
    t.annee,
    t.mois,
    t.libelle_mois,
    SUM(f.montant_ttc) as ca_mensuel
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_temps t ON f.id_date = t.id_date
WHERE f.statut = 'livré'
GROUP BY t.annee, t.mois, t.libelle_mois
ORDER BY t.annee DESC, t.mois DESC
LIMIT 12;

-- R3 : Top 10 produits les plus vendus par trimestre à Tanger
WITH TopProduits AS (
    SELECT 
        t.trimestre,
        t.annee,
        p.nom_produit,
        SUM(f.quantite) as total_vendu,
        RANK() OVER (PARTITION BY t.annee, t.trimestre ORDER BY SUM(f.quantite) DESC) as rang
    FROM dwh_mexora.fait_ventes f
    JOIN dwh_mexora.dim_produit p ON f.sk_produit = p.sk_produit
    JOIN dwh_mexora.dim_region r ON f.id_region = r.id_region
    JOIN dwh_mexora.dim_temps t ON f.id_date = t.id_date
    WHERE r.ville = 'Tanger' AND f.statut = 'livré'
    GROUP BY t.annee, t.trimestre, p.nom_produit
)
SELECT * FROM TopProduits WHERE rang <= 10;

-- R4 : Segment client avec le panier moyen le plus élevé
-- Panier moyen = Total CA / Nombre de commandes uniques
SELECT 
    c.segment_client,
    SUM(f.montant_ttc) / COUNT(DISTINCT f.id_commande) as panier_moyen
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_client c ON f.id_client = c.id_client
WHERE f.statut = 'livré'
GROUP BY c.segment_client
ORDER BY panier_moyen DESC;

-- R5 : Taux de retour par catégorie de produit
-- Taux de retour = (Commandes retournées / Total commandes) * 100
SELECT 
    p.categorie,
    COUNT(CASE WHEN f.statut = 'retourné' THEN 1 END) * 100.0 / COUNT(*) as taux_retour_pourcentage
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_produit p ON f.sk_produit = p.sk_produit
GROUP BY p.categorie
ORDER BY taux_retour_pourcentage DESC;

-- R6 : Effet Ramadan sur les ventes d'alimentation
-- Comparaison du CA moyen quotidien (Alimentation) : Ramadan vs Hors Ramadan
SELECT 
    t.periode_ramadan,
    AVG(ca_quotidien) as ca_moyen_quotidien_alimentation
FROM (
    SELECT 
        f.id_date,
        SUM(f.montant_ttc) as ca_quotidien
    FROM dwh_mexora.fait_ventes f
    JOIN dwh_mexora.dim_produit p ON f.sk_produit = p.sk_produit
    WHERE p.categorie = 'Alimentation' AND f.statut = 'livré'
    GROUP BY f.id_date
) sub
JOIN dwh_mexora.dim_temps t ON sub.id_date = t.id_date
GROUP BY t.periode_ramadan;

-- R7 : Meilleurs clients à Tanger ce trimestre (Demande DG)
SELECT 
    c.nom_complet,
    SUM(f.montant_ttc) as ca_client
FROM dwh_mexora.fait_ventes f
JOIN dwh_mexora.dim_client c ON f.id_client = c.id_client
JOIN dwh_mexora.dim_region r ON f.id_region = r.id_region
JOIN dwh_mexora.dim_temps t ON f.id_date = t.id_date
WHERE r.ville = 'Tanger' 
  AND t.annee = EXTRACT(YEAR FROM CURRENT_DATE)
  AND t.trimestre = EXTRACT(QUARTER FROM CURRENT_DATE)
  AND f.statut = 'livré'
GROUP BY c.nom_complet
ORDER BY ca_client DESC
LIMIT 10;
