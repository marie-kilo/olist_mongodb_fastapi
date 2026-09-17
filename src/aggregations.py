"""Agrégations MongoDB utilisées par le projet Olist."""

from pymongo.collection import Collection

from src.database import get_collection, get_database


def sales_by_category(
    collection: Collection,
    limit: int = 10,
) -> list[dict]:
    """Calcule le montant des articles vendus par catégorie."""

    pipeline = [
        {"$unwind": "$items"},
        {"$match": {"items.category": {"$ne": None}}},
        {
            "$group": {
                "_id": "$items.category",
                "total_sales": {"$sum": "$items.price"},
                "items_sold": {"$sum": 1},
            }
        },
        {"$sort": {"total_sales": -1}},
        {"$limit": limit},
        {
            "$project": {
                "_id": 0,
                "category": "$_id",
                "total_sales": 1,
                "items_sold": 1,
            }
        },
    ]

    return list(collection.aggregate(pipeline))


def sales_by_state(
    collection: Collection,
    limit: int = 10,
) -> list[dict]:
    """Calcule les commandes et montants payés par État."""

    pipeline = [
        {"$set": {"order_total": {"$sum": "$payments.value"}}},
        {
            "$group": {
                "_id": "$customer.state",
                "orders_count": {"$sum": 1},
                "total_payment_value": {"$sum": "$order_total"},
                "average_order_value": {"$avg": "$order_total"},
            }
        },
        {"$sort": {"total_payment_value": -1}},
        {"$limit": limit},
        {
            "$project": {
                "_id": 0,
                "state": "$_id",
                "orders_count": 1,
                "total_payment_value": 1,
                "average_order_value": 1,
            }
        },
    ]

    return list(collection.aggregate(pipeline))


def main() -> None:
    """Teste l'agrégation des ventes par catégorie."""

    database = get_database()
    collection = get_collection(database)

    categories = sales_by_category(
        collection,
        limit=10,
    )

    print("\nTOP 10 CATÉGORIES PAR MONTANT DES ARTICLES VENDUS")

    for category in categories:
        print(category)

    print("\nTOP 10 ÉTATS PAR MONTANT TOTAL PAYÉ")

    states = sales_by_state(
        collection,
        limit=10,
    )

    for state in states:
        print(state)


if __name__ == "__main__":
    main()
