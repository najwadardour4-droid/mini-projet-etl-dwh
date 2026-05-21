import pandas as pd
import numpy as np
import random
import json
import os
# from faker import Faker
from datetime import datetime, timedelta

# fake = Faker(['fr_FR'])

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'mexora_etl', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def generate_regions():
    regions_data = [
        ["TNG", "Tanger", "Tanger-Assilah", "Tanger-Tétouan-Al Hoceïma", "Nord", 947952, "90000"],
        ["CAS", "Casablanca", "Casablanca", "Casablanca-Settat", "Centre", 3359818, "20000"],
        ["RAK", "Marrakech", "Marrakech", "Marrakech-Safi", "Sud", 928850, "40000"],
        ["RAB", "Rabat", "Rabat", "Rabat-Salé-Kénitra", "Nord", 577827, "10000"],
        ["FEZ", "Fès", "Fès", "Fès-Meknès", "Centre", 1112072, "30000"],
        ["AGA", "Agadir", "Agadir-Ida-Ou-Tanane", "Souss-Massa", "Sud", 421844, "80000"],
        ["OUJ", "Oujda", "Oujda-Angad", "Oriental", "Est", 494252, "60000"],
        ["MEK", "Meknès", "Meknès", "Fès-Meknès", "Centre", 635822, "50000"],
    ]
    df = pd.DataFrame(regions_data, columns=["code_ville", "nom_ville_standard", "province", "region_admin", "zone_geo", "population", "code_postal"])
    df.to_csv(f"{DATA_DIR}/regions_maroc.csv", index=False, encoding='utf-8')
    return df

def generate_products():
    categories = ["Electronique", "Mode", "Alimentation"]
    sub_categories = {
        "Electronique": ["Smartphones", "Laptops", "Accessoires"],
        "Mode": ["Vêtements", "Chaussures", "Sacs"],
        "Alimentation": ["Épicerie", "Boissons", "Frais"]
    }
    brands = {
        "Electronique": ["Apple", "Samsung", "Sony", "HP"],
        "Mode": ["Zara", "H&M", "Nike", "Adidas"],
        "Alimentation": ["Centrale Danone", "Cosumar", "Lesieur"]
    }
    
    products = []
    for i in range(1, 101):
        cat = random.choice(categories)
        sub_cat = random.choice(sub_categories[cat])
        brand = random.choice(brands[cat])
        
        # Intentional problem: inconsistent case for categories
        if random.random() < 0.2:
            cat = cat.lower()
        elif random.random() < 0.1:
            cat = cat.upper()
            
        prod_id = f"P{str(i).zfill(3)}"
        price = round(random.uniform(10, 15000), 2)
        
        # Intentional problem: null price for some products
        if random.random() < 0.05:
            price = None
            
        products.append({
            "id_produit": prod_id,
            "nom": f"{brand} {sub_cat} Model {random.randint(1, 20)}",
            "categorie": cat,
            "sous_categorie": sub_cat,
            "marque": brand,
            "fournisseur": f"{brand} MENA",
            "prix_catalogue": price,
            "origine_pays": random.choice(["USA", "China", "France", "Morocco"]),
            "date_creation": (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 300))).strftime("%Y-%m-%d"),
            "actif": random.random() > 0.1 # Some products are inactive
        })
    
    with open(f"{DATA_DIR}/produits_mexora.json", 'w', encoding='utf-8') as f:
        json.dump({"produits": products}, f, indent=2, ensure_ascii=False)
    return products

def generate_clients(regions_df):
    clients = []
    villes_raw = regions_df['nom_ville_standard'].tolist()
    first_names = ["Ahmed", "Fatima", "Youssef", "Khadija", "Omar", "Sanaa", "Mehdi", "Imane", "Zineb", "Anas"]
    last_names = ["Alami", "Bennani", "Chraibi", "Drissi", "El Fassi", "Ghazali", "Haddad", "Idrissi", "Jebli", "Kabbaj"]
    domains = ["gmail.com", "yahoo.fr", "hotmail.com", "outlook.com"]
    
    for i in range(1, 5001):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{random.choice(domains)}"
        
        # Intentional problem: malformed email
        if random.random() < 0.05:
            email = email.replace("@", "")
            
        # Intentional problem: mixed sexe codes
        sexe_rand = random.random()
        if sexe_rand < 0.3:
            sexe = random.choice(['m', 'f'])
        elif sexe_rand < 0.6:
            sexe = random.choice(['1', '0'])
        else:
            sexe = random.choice(['Homme', 'Femme'])
            
        # Intentional problem: invalid birth dates
        birth_year = random.randint(1900, 2025)
        birth_date = datetime(birth_year, random.randint(1, 12), random.randint(1, 28))
        
        ville = random.choice(villes_raw)
        # Intentional problem: inconsistent city names
        if ville == "Tanger":
            ville = random.choice(["tanger", "TNG", "TANGER", "Tnja", "Tanger"])
            
        clients.append({
            "id_client": f"C{str(i).zfill(5)}",
            "nom": last_name,
            "prenom": first_name,
            "email": email,
            "date_naissance": birth_date.strftime("%Y-%m-%d"),
            "sexe": sexe,
            "ville": ville,
            "telephone": f"06{random.randint(10000000, 99999999)}",
            "date_inscription": (datetime.now() - timedelta(days=random.randint(0, 730))).strftime("%Y-%m-%d"),
            "canal_acquisition": random.choice(["Facebook", "Google", "Instagram", "Direct"])
        })
    
    # Intentional problem: duplicate clients (same email, different id)
    for _ in range(50):
        orig = random.choice(clients)
        dup = orig.copy()
        dup["id_client"] = f"C{random.randint(10000, 99999)}"
        clients.append(dup)
        
    df = pd.DataFrame(clients)
    df.to_csv(f"{DATA_DIR}/clients_mexora.csv", index=False, encoding='utf-8')
    return df

def generate_orders(clients_df, products_list, regions_df):
    orders = []
    statuses = ["livré", "annulé", "en_cours", "retourné"]
    villes_raw = regions_df['nom_ville_standard'].tolist()
    clients_records = clients_df.to_dict('records')
    
    for i in range(1, 50001): # 50,000 rows as requested
        client = random.choice(clients_records)
        product = random.choice(products_list)
        
        order_id = f"ORD-{str(i).zfill(6)}"
        
        # Intentional problem: mixed date formats
        order_date_obj = datetime.now() - timedelta(days=random.randint(0, 365))
        date_rand = random.random()
        if date_rand < 0.33:
            date_str = order_date_obj.strftime("%d/%m/%Y")
        elif date_rand < 0.66:
            date_str = order_date_obj.strftime("%Y-%m-%d")
        else:
            date_str = order_date_obj.strftime("%b %d %Y")
            
        qty = random.randint(1, 5)
        # Intentional problem: negative quantity
        if random.random() < 0.01:
            qty = -random.randint(1, 5)
            
        price = product['prix_catalogue'] if product['prix_catalogue'] is not None else 0
        # Intentional problem: zero price
        if random.random() < 0.01:
            price = 0
            
        status = random.choice(statuses)
        # Intentional problem: non-standard status
        if random.random() < 0.05:
            status = random.choice(["OK", "KO", "DONE"])
            
        ville = random.choice(villes_raw)
        if ville == "Tanger":
            ville = random.choice(["tanger", "TNG", "TANGER", "Tnja"])
            
        livreur_id = f"L{str(random.randint(1, 20)).zfill(3)}"
        # Intentional problem: missing livreur
        if random.random() < 0.07:
            livreur_id = None
            
        orders.append({
            "id_commande": order_id,
            "id_client": client['id_client'],
            "id_produit": product['id_produit'],
            "date_commande": date_str,
            "quantite": qty,
            "prix_unitaire": price,
            "statut": status,
            "ville_livraison": ville,
            "mode_paiement": random.choice(["Cash", "Card", "Transfer"]),
            "id_livreur": livreur_id,
            "date_livraison": (order_date_obj + timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d") if status == "livré" else None
        })
        
    # Intentional problem: duplicates on id_commande (~3%)
    num_dups = int(len(orders) * 0.03)
    for _ in range(num_dups):
        orig = random.choice(orders)
        orders.append(orig.copy())
        
    df = pd.DataFrame(orders)
    df.to_csv(f"{DATA_DIR}/commandes_mexora.csv", index=False, encoding='utf-8')
    return df

if __name__ == "__main__":
    print(f"Current working directory: {os.getcwd()}")
    print(f"Target data directory: {DATA_DIR}")
    print("Generating regions...")
    regions_df = generate_regions()
    print(f"Regions saved to {DATA_DIR}/regions_maroc.csv")
    print("Generating products...")
    products_list = generate_products()
    print(f"Products saved to {DATA_DIR}/produits_mexora.json")
    print("Generating clients...")
    clients_df = generate_clients(regions_df)
    print(f"Clients saved to {DATA_DIR}/clients_mexora.csv")
    print("Generating orders...")
    generate_orders(clients_df, products_list, regions_df)
    print(f"Orders saved to {DATA_DIR}/commandes_mexora.csv")
    print("Data generation complete!")
