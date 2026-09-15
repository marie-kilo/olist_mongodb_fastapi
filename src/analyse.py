"""Analyse exploratoire des fichiers Olist."""

from pathlib import Path

import pandas as pd

DATA_DIR = Path("data/raw")

FILES = [
    "olist_orders_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_products_dataset.csv",
]


def analyse_file(filename: str) -> None:
    """Affiche les principales informations d'un fichier CSV."""
    path = DATA_DIR / filename

    df = pd.read_csv(path)

    print(f"\nFichier: {filename}")
    print(f"\nNombre de lignes: {len(df)}")
    print(f"\nNombre de colonnes: {len(df.columns)}")

    print("\nColonnes:")
    print(df.columns.tolist())

    print("\nTypes :")
    print(df.dtypes)

    print("\nValeurs manquantes :")
    print(df.isna().sum())

    print("\nDoublons complets :")
    print(df.duplicated().sum())

    print("\n" + "=" * 50 + "\n")

def analyse_relations() -> None:
    """Analyse les relations entre les fichiers Olist."""

    orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv")
    customers = pd.read_csv(DATA_DIR / "olist_customers_dataset.csv")
    items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")
    payments = pd.read_csv(DATA_DIR / "olist_order_payments_dataset.csv")
    reviews = pd.read_csv(DATA_DIR / "olist_order_reviews_dataset.csv")
    products = pd.read_csv(DATA_DIR / "olist_products_dataset.csv")

    print("\n" + "=" * 70)
    print("ANALYSE DES RELATIONS")
    print("=" * 70)

    print("\nUnicité des identifiants :")

    print(
        "order_id uniques :",
        orders["order_id"].nunique(),
        "/",
        len(orders),
    )

    print(
        "customer_id uniques :",
        customers["customer_id"].nunique(),
        "/",
        len(customers),
    )

    print(
        "customer_unique_id uniques :",
        customers["customer_unique_id"].nunique(),
    )

    print(
        "product_id uniques :",
        products["product_id"].nunique(),
        "/",
        len(products),
    )

    print("\nIntégrité des relations :")

    missing_customers = ~orders["customer_id"].isin(
        customers["customer_id"]
    )

    print(
        "Orders avec customer_id inexistant :",
        missing_customers.sum(),
    )

    missing_item_orders = ~items["order_id"].isin(
        orders["order_id"]
    )

    print(
        "Items avec order_id inexistant :",
        missing_item_orders.sum(),
    )

    missing_products = ~items["product_id"].isin(
        products["product_id"]
    )

    print(
        "Items avec product_id inexistant :",
        missing_products.sum(),
    )

    missing_payment_orders = ~payments["order_id"].isin(
        orders["order_id"]
    )

    print(
        "Paiements avec order_id inexistant :",
        missing_payment_orders.sum(),
    )

    missing_review_orders = ~reviews["order_id"].isin(
        orders["order_id"]
    )

    print(
        "Reviews avec order_id inexistant :",
        missing_review_orders.sum(),
    )

def main() -> None:
    """Lance les analyses du dataset Olist."""

    for filename in FILES:
        analyse_file(filename)

    analyse_relations()


if __name__ == "__main__":
    main()
