"""Transformation des données Olist vers un modèle documentaire MongoDB."""

from datetime import datetime
from pathlib import Path

import pandas as pd

DATA_DIR = Path("data/raw")


def load_data() -> dict[str, pd.DataFrame]:
    """Charge les fichiers CSV nécessaires au projet."""

    data = {
        "orders": pd.read_csv(DATA_DIR / "olist_orders_dataset.csv"),
        "customers": pd.read_csv(DATA_DIR / "olist_customers_dataset.csv"),
        "items": pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv"),
        "payments": pd.read_csv(DATA_DIR / "olist_order_payments_dataset.csv"),
        "reviews": pd.read_csv(DATA_DIR / "olist_order_reviews_dataset.csv"),
        "products": pd.read_csv(DATA_DIR / "olist_products_dataset.csv"),
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


def to_python_datetime(value) -> datetime | None:
    """Convertit une date Pandas en datetime Python ou None."""

    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    return value


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
                "creation_date": to_python_datetime(row.review_creation_date),
                "answer_timestamp": to_python_datetime(row.review_answer_timestamp),
            }

            order_reviews.append(review)

        reviews_by_order[order_id] = order_reviews

    return reviews_by_order


def build_order_documents(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    items_by_order: dict[str, list[dict[str, object]]],
    payments_by_order: dict[str, list[dict[str, object]]],
    reviews_by_order: dict[str, list[dict[str, object]]],
) -> list[dict[str, object]]:
    """Construit un document MongoDB pour chaque commande."""

    documents = []

    customers_by_id = customers.set_index("customer_id").to_dict(orient="index")

    for row in orders.itertuples(index=False):
        customer = customers_by_id[row.customer_id]

        document = {
            "order_id": row.order_id,
            "status": row.order_status,
            "customer": {
                "customer_id": row.customer_id,
                "customer_unique_id": customer["customer_unique_id"],
                "zip_code_prefix": int(customer["customer_zip_code_prefix"]),
                "city": customer["customer_city"],
                "state": customer["customer_state"],
            },
            "dates": {
                "purchase": to_python_datetime(row.order_purchase_timestamp),
                "approved": to_python_datetime(row.order_approved_at),
                "delivered_carrier": to_python_datetime(
                    row.order_delivered_carrier_date
                ),
                "delivered_customer": to_python_datetime(
                    row.order_delivered_customer_date
                ),
                "estimated_delivery": to_python_datetime(
                    row.order_estimated_delivery_date
                ),
            },
            "items": items_by_order.get(
                row.order_id,
                [],
            ),
            "payments": payments_by_order.get(
                row.order_id,
                [],
            ),
            "reviews": reviews_by_order.get(
                row.order_id,
                [],
            ),
        }

        documents.append(document)

    return documents


def main() -> None:
    """Construit les documents MongoDB Olist."""

    data = load_data()

    orders = prepare_orders(data["orders"])

    items = prepare_items(
        data["items"],
        data["products"],
    )

    reviews = prepare_reviews(data["reviews"])

    items_by_order = build_items_by_order(items)

    payments_by_order = build_payments_by_order(data["payments"])

    reviews_by_order = build_reviews_by_order(reviews)

    documents = build_order_documents(
        orders=orders,
        customers=data["customers"],
        items_by_order=items_by_order,
        payments_by_order=payments_by_order,
        reviews_by_order=reviews_by_order,
    )

    print("\nNOMBRE DE COMMANDES")
    print(len(orders))

    print("\nNOMBRE DE DOCUMENTS CRÉÉS")
    print(len(documents))

    print("\nPREMIER DOCUMENT")
    print(documents[0])


if __name__ == "__main__":
    main()
