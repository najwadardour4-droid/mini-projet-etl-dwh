import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv('DB_USER', 'postgres')
# Hna k-n-codiw l-password bach i-qbel dik @
DB_PASS = urllib.parse.quote_plus(os.getenv('DB_PASS', 'najwa@123')) 
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'mexora_dwh')


# Dak l-password li fih @ khassu i-t-codé
password = "najwa@123" 
safe_password = urllib.parse.quote_plus(password)

# Daba l-URL ghadi i-koun s-hih 100%
DATABASE_URL = f"postgresql://postgres:{safe_password}@localhost:5432/mexora_dwh"

# File paths
DATA_DIR = 'mexora_etl/data'
COMMANDES_PATH = os.path.join(DATA_DIR, 'commandes_mexora.csv')
PRODUITS_PATH = os.path.join(DATA_DIR, 'produits_mexora.json')
CLIENTS_PATH = os.path.join(DATA_DIR, 'clients_mexora.csv')
REGIONS_PATH = os.path.join(DATA_DIR, 'regions_maroc.csv')
