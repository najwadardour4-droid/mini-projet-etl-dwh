# Rapport de Modélisation - Mexora Analytics

Ce document détaille les choix de conception pour l'entrepôt de données de Mexora Analytics.

## 1. Analyse des besoins décisionnels (Top-Down)

Conformément à la méthodologie Top-Down, nous avons formalisé les besoins métier sous forme de requêtes-types structurées en trois clauses : **Analyser**, **En fonction de**, **Pour**.

- **Requête R1 (Performance Régionale)** :
  - **Analyser** → le chiffre d'affaires (montant TTC)
  - **En fonction de** → la région administrative
  - **Pour** → les commandes avec statut "livré" uniquement.

- **Requête R2 (Top Produits à Tanger)** :
  - **Analyser** → la quantité vendue
  - **En fonction de** → le produit et le trimestre
  - **Pour** → la ville de Tanger et le statut "livré".

- **Requête R3 (Fidélité et Panier Moyen)** :
  - **Analyser** → le panier moyen (CA / Nombre de commandes)
  - **En fonction de** → le segment client (Gold, Silver, Bronze)
  - **Pour** → l'ensemble des ventes livrées.

- **Requête R4 (Qualité de Service / Retours)** :
  - **Analyser** → le taux de retour (commandes retournées / total commandes)
  - **En fonction de** → la catégorie de produit
  - **Pour** → toutes les catégories.

- **Requête R5 (Impact Saisonnier Ramadan)** :
  - **Analyser** → le chiffre d'affaires quotidien moyen
  - **En fonction de** → la période (Ramadan vs Hors Ramadan)
  - **Pour** → la catégorie de produit "Alimentation".

## 2. Choix de Granularité

La granularité choisie pour la table de faits `fait_ventes` est **la ligne de commande (order line item)**.
Chaque enregistrement représente la vente d'un produit spécifique au sein d'une commande unique.

**Justification** : Cette granularité fine permet d'agréger les données à n'importe quel niveau supérieur (par commande, par client, par jour, par catégorie) sans perte d'information, répondant ainsi à toutes les demandes du Directeur Général.

## 3. Mesures et Additivité

| Mesure | Type d'additivité | Justification métier |
| :--- | :--- | :--- |
| `quantite` | Additive | Somme des unités vendues sur n'importe quelle dimension. |
| `montant_ttc` | Additive | Valeur monétaire totale des transactions. |
| `prix_unitaire` | Non-additive | Sommer les prix unitaires n'a pas de sens ; on utilise la moyenne ou le min/max. |

## 4. Gestion des Slowly Changing Dimensions (SCD)

Nous avons implémenté les stratégies suivantes pour garantir la cohérence historique :

1.  **SCD Type 2 pour `dim_produit`** :
    - **Cas** : Changement de catégorie ou de prix catalogue d'un produit.
    - **Justification** : Si un produit passe de "Électronique" à "Accessoires", nous voulons que les ventes passées restent comptabilisées dans "Électronique" pour la précision des rapports annuels.
    - **Attributs** : `sk_produit` (clé de substitution), `date_debut`, `date_fin`, `est_actuel`.

2.  **SCD Type 1 pour `dim_client`** :
    - **Cas** : Mise à jour des informations de contact (email, téléphone).
    - **Justification** : Nous privilégions l'exactitude des coordonnées actuelles pour le marketing.
    - **Exception** : Le `segment_client` est recalculé dynamiquement lors de l'ETL basé sur le CA glissant des 12 derniers mois.

## 5. Architecture du Schéma en Étoile

L'entrepôt repose sur un schéma en étoile optimisé pour les performances de lecture :

- **Table de Faits** : `fait_ventes`
- **Dimensions** :
  - `dim_temps` : Inclut les spécificités locales (jours fériés marocains, périodes de Ramadan).
  - `dim_produit` : Versionnée via SCD Type 2.
  - `dim_client` : Segmentée dynamiquement (Gold/Silver/Bronze).
  - `dim_region` : Référentiel géographique harmonisé.
  - `dim_livreur` : Suivi des performances logistiques.

## 6. Rapport de Transformations (ETL)

Le pipeline Python applique les règles métier suivantes pour garantir la qualité des données :

### 6.1 Commandes (`clean_commandes.py`)
- **R1 - Déduplication** : Suppression des doublons sur `id_commande` (maintien de la dernière occurrence).
- **R2 - Standardisation des Dates** : Conversion des formats mixtes (ex: "15/11/2024", "Nov 15 2024") en format ISO `YYYY-MM-DD`.
- **R3 - Harmonisation Géographique** : Mapping des villes (ex: "TNG", "Tnja" -> "Tanger") via le référentiel officiel.
- **R4 - Standardisation des Statuts** : Mapping des valeurs non-standards ("OK", "DONE", "KO") vers `livré`, `annulé`, `en_cours`, `retourné`.
- **R5 - Nettoyage Quantités** : Suppression des lignes avec `quantite <= 0`.
- **R6 - Nettoyage Prix** : Suppression des commandes de test (`prix_unitaire = 0`).
- **R7 - Gestion des Nuls** : Remplacement des `id_livreur` manquants par `-1` (Livreur Inconnu).

### 6.2 Clients (`clean_clients.py`)
- **R1 - Déduplication Email** : Suppression des doublons basés sur l'email normalisé.
- **R2 - Standardisation Sexe** : Conversion des formats h/f, 1/0, Homme/Femme en format unifié `m` / `f`.
- **R3 - Validation Âge** : Invalidation des dates de naissance pour les âges < 16 ans ou > 100 ans.
- **R4 - Validation Email** : Vérification du format via Regex (présence de @ et domaine).
- **R5 - Segmentation Dynamique** : Attribution du segment (Gold/Silver/Bronze) basé sur le CA glissant des 12 derniers mois.

### 6.3 Produits (`clean_produits.py`)
- **R1 - Normalisation Catégories** : Correction de la casse (ex: "ELECTRONIQUE" -> "Electronique").
- **R2 - Gestion des Prix Nuls** : Remplacement des prix catalogue `null` par le prix moyen de la sous-catégorie.

## 7. Optimisations Techniques

Pour répondre à la demande de performance du DG ("en quelques secondes, pas en 6 minutes"), nous avons mis en place :
- **Index B-Tree** sur toutes les clés étrangères de la table de faits.
- **Partitionnement temporel** (recommandé pour la production) sur la table de faits.
- **Vues matérialisées** pour les agrégats fréquents (CA par région/mois).
