import pandas as pd
import functools
import os

@functools.lru_cache(maxsize=1)
def load_products() -> pd.DataFrame:
    path = "retailmind_products.csv"
    return pd.read_csv(path)

@functools.lru_cache(maxsize=1)
def load_reviews() -> pd.DataFrame:
    path = "retailmind_reviews.csv"
    return pd.read_csv(path)

def resolve_product_id(name_hint: str) -> str | None:
    """Fuzzy match product name to product_id"""
    if not name_hint:
        return None
    df = load_products()
    mask = df['product_name'].str.lower().str.contains(name_hint.lower(), na=False)
    matches = df[mask]
    if not matches.empty:
        return matches.iloc[0]['product_id']
    return None

def get_all_product_ids() -> list:
    return load_products()['product_id'].tolist()
