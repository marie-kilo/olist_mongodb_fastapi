"""Transformation des données Olist vers un modèle documentaire MongoDB."""

from pathlib import Path

import pandas as pd

DATA_DIR = Path("data/raw")


def load_data() -> dict[str, pd.DataFrame]:
    """Charge les fichiers CSV nécessaires au projet."""

    data = {
        "orders": pd.read_csv(
            DATA_DIR / "olist_orders_dataset.csv"
        ),
        "customers": pd.read_csv(
            DATA_DIR / "olist_customers_dataset.csv"
        ),
        "items": pd.read_csv(
            DATA_DIR / "olist_order_items_dataset.csv"
        ),
        "payments": pd.read_csv(
            DATA_DIR / "olist_order_payments_dataset.csv"
        ),
        "reviews": pd.read_csv(
            DATA_DIR / "olist_order_reviews_dataset.csv"
        ),
        "products": pd.read_csv(
            DATA_DIR / "olist_products_dataset.csv"
        ),
    }

    return data

def prepare_orders(orders: pd.DataFrame) -> pd.DataFrame:
    """Convertit les colonnes de dates des commandes."""

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for column in date_columns:
        orders[column] = pd.to_datetime(
            orders[column],
            errors="coerce",
        )

    return orders

def prepare_items(
    items: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    """Ajoute les informations produit aux articles commandés."""

    product_columns = [
        "product_id",
        "product_category_name",
    ]

    items = items.merge(
        products[product_columns],
        on="product_id",
        how="left",
    )

    return items

def build_items_by_order(
    items: pd.DataFrame,
) -> dict[str, list[dict[str, object]]]:
    """Regroupe les articles par commande."""

    items_by_order = {}

    for order_id, group in items.groupby("order_id", sort=False):
        order_items = []

        for row in group.itertuples(index=False):
            item = {
                "order_item_id": int(row.order_item_id),
                "product_id": row.product_id,
                "seller_id": row.seller_id,
                "category": (
                    None
                    if pd.isna(row.product_category_name)
                    else row.product_category_name
                ),
                "price": float(row.price),
                "freight_value": float(row.freight_value),
            }

            order_items.append(item)

        items_by_order[order_id] = order_items

    return items_by_order


def prepare_reviews(reviews: pd.DataFrame) -> pd.DataFrame:
    """Convertit les colonnes de dates des avis."""

    date_columns = [
        "review_creation_date",
        "review_answer_timestamp",
    ]

    for column in date_columns:
        reviews[column] = pd.to_datetime(
            reviews[column],
            errors="coerce",
        )

    return reviews


def build_payments_by_order(
    payments: pd.DataFrame,
) -> dict[str, list[dict[str, object]]]:
    """Regroupe les paiements par commande."""

    payments_by_order = {}

    for order_id, group in payments.groupby("order_id", sort=False):
        order_payments = []

        for row in group.itertuples(index=False):
            payment = {
                "sequence": int(row.payment_sequential),
                "type": row.payment_type,
                "installments": int(row.payment_installments),
                "value": float(row.payment_value),
            }

            order_payments.append(payment)

        payments_by_order[order_id] = order_payments

    return payments_by_order

def build_reviews_by_order(
    reviews: pd.DataFrame,
) -> dict[str, list[dict[str, object]]]:
    """Regroupe les avis par commande."""

    reviews_by_order = {}

    for order_id, group in reviews.groupby("order_id", sort=False):
        order_reviews = []

        for row in group.itertuples(index=False):
            review = {
                "review_id": row.review_id,
                "score": int(row.review_score),
                "title": (
                    None
                    if pd.isna(row.review_comment_title)
                    else row.review_comment_title
                ),
                "message": (
                    None
                    if pd.isna(row.review_comment_message)
                    else row.review_comment_message
                ),
                "creation_date": row.review_creation_date,
                "answer_timestamp": row.review_answer_timestamp,
            }

            order_reviews.append(review)

        reviews_by_order[order_id] = order_reviews

    return reviews_by_order

def main() -> None:
    """Teste les transformations Olist."""

    data = load_data()

    # Préparation des commandes
    orders = prepare_orders(data["orders"])

    # Préparation et enrichissement des items
    items = prepare_items(
        data["items"],
        data["products"],
    )

    # Préparation des reviews
    reviews = prepare_reviews(data["reviews"])

    # Regroupement par commande
    items_by_order = build_items_by_order(items)

    payments_by_order = build_payments_by_order(
        data["payments"]
    )

    reviews_by_order = build_reviews_by_order(
        reviews
    )

    # Vérification des types des commandes
    print("\nORDERS")
    print(orders.dtypes)

    # Vérification des items enrichis
    print("\nITEMS ENRICHIS")
    print(
        items[
            [
                "order_id",
                "product_id",
                "product_category_name",
                "price",
            ]
        ].head()
    )

    # -----------------------------
    # ITEMS
    # -----------------------------

    print("\nNOMBRE DE COMMANDES AVEC ITEMS")
    print(len(items_by_order))

    items_count = items.groupby("order_id").size()

    order_with_most_items = items_count.idxmax()

    print("\nCOMMANDE AVEC LE PLUS D'ITEMS")
    print(order_with_most_items)

    print("\nNOMBRE D'ITEMS")
    print(items_count.max())

    print("\nITEMS DE CETTE COMMANDE")
    print(items_by_order[order_with_most_items])

    # -----------------------------
    # PAIEMENTS
    # -----------------------------

    print("\nNOMBRE DE COMMANDES AVEC PAIEMENT")
    print(len(payments_by_order))

    payments_count = (
        data["payments"]
        .groupby("order_id")
        .size()
    )

    order_with_most_payments = payments_count.idxmax()

    print("\nCOMMANDE AVEC LE PLUS DE PAIEMENTS")
    print(order_with_most_payments)

    print("\nNOMBRE DE PAIEMENTS")
    print(payments_count.max())

    print("\nPAIEMENTS DE CETTE COMMANDE")
    print(
        payments_by_order[
            order_with_most_payments
        ]
    )

    # -----------------------------
    # REVIEWS
    # -----------------------------

    print("\nNOMBRE DE COMMANDES AVEC REVIEW")
    print(len(reviews_by_order))

    reviews_count = (
        reviews
        .groupby("order_id")
        .size()
    )

    order_with_most_reviews = reviews_count.idxmax()

    print("\nCOMMANDE AVEC LE PLUS DE REVIEWS")
    print(order_with_most_reviews)

    print("\nNOMBRE DE REVIEWS")
    print(reviews_count.max())

    print("\nREVIEWS DE CETTE COMMANDE")
    print(
        reviews_by_order[
            order_with_most_reviews
        ]
    )


if __name__ == "__main__":
    main()