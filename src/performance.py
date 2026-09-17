"""Analyse des performances des requêtes MongoDB."""

from pymongo import ASCENDING
from pymongo.collection import Collection

from src.database import get_collection, get_database

INDEX_NAME = "idx_customer_unique_id"


def explain_customer_query(
    collection: Collection,
    customer_unique_id: str,
) -> dict:
    """Analyse la recherche des commandes d'un client."""

    database = collection.database

    explain_result = database.command(
        "explain",
        {
            "find": collection.name,
            "filter": {"customer.customer_unique_id": customer_unique_id},
        },
        verbosity="executionStats",
    )

    return explain_result


def create_customer_index(
    collection: Collection,
) -> str:
    """Crée un index sur l'identifiant unique du client."""

    index_name = collection.create_index(
        [
            (
                "customer.customer_unique_id",
                ASCENDING,
            )
        ],
        name=INDEX_NAME,
    )

    return index_name


def drop_customer_index(
    collection: Collection,
) -> None:
    """Supprime l'index client s'il existe déjà."""

    indexes = collection.index_information()

    if INDEX_NAME in indexes:
        collection.drop_index(INDEX_NAME)


def print_execution_stats(
    title: str,
    explain_result: dict,
) -> None:
    """Affiche les principales statistiques d'exécution."""

    stats = explain_result["executionStats"]

    print(f"\n{title}")

    print(
        "Documents retournés :",
        stats["nReturned"],
    )

    print(
        "Documents examinés :",
        stats["totalDocsExamined"],
    )

    print(
        "Clés d'index examinées :",
        stats["totalKeysExamined"],
    )

    print(
        "Temps d'exécution :",
        stats["executionTimeMillis"],
        "ms",
    )


def main() -> None:
    """Compare les performances avant et après création de l'index."""

    database = get_database()
    collection = get_collection(database)

    customer_unique_id = "7c396fd4830fd04220f754e42b4e5bff"

    # Supprime l'index s'il existe déjà afin de pouvoir
    # mesurer réellement les performances avant index.
    drop_customer_index(collection)

    result_before = explain_customer_query(
        collection,
        customer_unique_id,
    )

    print_execution_stats(
        "PERFORMANCE AVANT INDEX",
        result_before,
    )

    print("\nCRÉATION DE L'INDEX")

    index_name = create_customer_index(collection)

    print(
        "Index créé :",
        index_name,
    )

    result_after = explain_customer_query(
        collection,
        customer_unique_id,
    )

    print_execution_stats(
        "PERFORMANCE APRÈS INDEX",
        result_after,
    )


if __name__ == "__main__":
    main()
