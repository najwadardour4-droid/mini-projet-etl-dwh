import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'postgres')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'mexora_dwh')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# File paths
DATA_DIR = 'mexora_etl/data'
COMMANDES_PATH = os.path.join(DATA_DIR, 'commandes_mexora.csv')
PRODUITS_PATH = os.path.join(DATA_DIR, 'produits_mexora.json')
CLIENTS_PATH = os.path.join(DATA_DIR, 'clients_mexora.csv')
REGIONS_PATH = os.path.join(DATA_DIR, 'regions_maroc.csv')
