"""Requêtes MongoDB utilisées par le projet Olist."""

from pymongo.collection import Collection

from src.database import get_collection, get_database


def find_order_by_id(
    collection: Collection,
    order_id: str,
) -> dict | None:
    """Recherche une commande à partir de son order_id."""

    return collection.find_one({"order_id": order_id})


def find_orders_by_status(
    collection: Collection,
    status: str,
    limit: int = 10,
) -> list[dict]:
    """Recherche des commandes selon leur statut."""

    cursor = collection.find({"status": status}).limit(limit)

    return list(cursor)


def find_orders_by_customer(
    collection: Collection,
    customer_unique_id: str,
    limit: int = 10,
) -> list[dict]:
    """Recherche les commandes d'un client unique."""

    cursor = collection.find({"customer.customer_unique_id": customer_unique_id}).limit(
        limit
    )

    return list(cursor)


def find_orders_by_state(
    collection: Collection,
    state: str,
    limit: int = 10,
) -> list[dict]:
    """Recherche des commandes selon l'État du client."""

    cursor = collection.find({"customer.state": state}).limit(limit)

    return list(cursor)


def main() -> None:
    """Teste la recherche d'une commande."""

    database = get_database()
    collection = get_collection(database)

    order_id = "e481f51cbdc54678b7cc49136f2d6af7"

    order = find_order_by_id(
        collection,
        order_id,
    )

    if order is None:
        print("Commande introuvable.")
        return

    print("\nCOMMANDE TROUVÉE")
    print("Order ID :", order["order_id"])
    print("Status :", order["status"])
    print("Client :", order["customer"])
    print("Nombre d'items :", len(order["items"]))
    print("Nombre de paiements :", len(order["payments"]))
    print("Nombre de reviews :", len(order["reviews"]))

    print("\nCOMMANDES DELIVERED")

    orders = find_orders_by_status(
        collection,
        status="delivered",
        limit=5,
    )

    for order in orders:
        print(
            order["order_id"],
            "-",
            order["status"],
        )

    print("\nCOMMANDES DU CLIENT")

    customer_unique_id = "7c396fd4830fd04220f754e42b4e5bff"

    customer_orders = find_orders_by_customer(
        collection,
        customer_unique_id=customer_unique_id,
        limit=10,
    )

    print(
        "Nombre de commandes trouvées :",
        len(customer_orders),
    )

    for order in customer_orders:
        print(
            order["order_id"],
            "-",
            order["status"],
        )

    print("\nCOMMANDES DE L'ÉTAT SP")

    state_orders = find_orders_by_state(
        collection,
        state="SP",
        limit=5,
    )

    print(
        "Nombre de commandes retournées :",
        len(state_orders),
    )

    for order in state_orders:
        print(
            order["order_id"],
            "-",
            order["customer"]["city"],
            "-",
            order["customer"]["state"],
        )


if __name__ == "__main__":
    main()
