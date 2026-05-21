import pandas as pd
import logging
from sqlalchemy import create_engine

def charger_dimension(df: pd.DataFrame, table_name: str, engine, schema='dwh_mexora'):
    """Charge une table de dimension."""
    try:
        df.to_sql(
            name=table_name,
            con=engine,
            schema=schema,
            if_exists='replace',
            index=False,
            method='multi',
            chunksize=1000
        )
        logging.info(f"[LOAD] {table_name}: {len(df)} lignes chargées")
    except Exception as e:
        logging.error(f"Erreur lors du chargement de {table_name}: {e}")
        raise e

def charger_faits(df: pd.DataFrame, table_name: str, engine, schema='dwh_mexora'):
    """Charge la table de faits."""
    try:
        df.to_sql(
            name=table_name,
            con=engine,
            schema=schema,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=1000
        )
        logging.info(f"[LOAD] {table_name}: {len(df)} lignes chargées")
    except Exception as e:
        logging.error(f"Erreur lors du chargement de {table_name}: {e}")
        raise e
