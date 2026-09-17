"""Connexion et import des données dans MongoDB."""

import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pymongo import MongoClient, ReplaceOne
from pymongo.collection import Collection
from pymongo.database import Database

from src.transform import build_documents

load_dotenv()


def get_database() -> Database:
    """Retourne la base de données MongoDB."""

    user = os.getenv("MONGO_USER")
    password = os.getenv("MONGO_PASSWORD")
    host = os.getenv("MONGO_HOST", "localhost")
    port = os.getenv("MONGO_PORT", "27017")
    database_name = os.getenv("MONGO_DB", "olist")
    auth_source = os.getenv("MONGO_AUTH_SOURCE", "admin")

    if not user or not password:
        raise ValueError("MONGO_USER et MONGO_PASSWORD doivent être définis dans .env")

    # quote_plus() garantit que l’URI sera valide même avec des caractères spéciaux.
    user_encoded = quote_plus(user)
    password_encoded = quote_plus(password)

    mongo_uri = (
        f"mongodb://{user_encoded}:{password_encoded}"
        f"@{host}:{port}/"
        f"?authSource={auth_source}"
    )
    # Vérification des variables d'environnement pour le débogage
    # print("USER :", user)
    # print("HOST :", host)
    # print("PORT :", port)
    # print("DATABASE :", database_name)
    # print("AUTH SOURCE :", auth_source)

    client = MongoClient(mongo_uri)

    client.admin.command("ping")

    return client[database_name]


def get_collection(database: Database) -> Collection:
    """Retourne la collection MongoDB du projet."""

    collection_name = os.getenv(
        "MONGO_COLLECTION",
        "orders",
    )

    return database[collection_name]


def import_documents(
    collection: Collection,
    documents: list[dict[str, object]],
    batch_size: int = 1000,
) -> None:
    """Importe les documents MongoDB par lots."""

    collection.create_index(
        "order_id",
        unique=True,
    )

    total = len(documents)

    for start in range(0, total, batch_size):
        batch = documents[start : start + batch_size]

        operations = [
            ReplaceOne(
                {"order_id": document["order_id"]},
                document,
                upsert=True,
            )
            for document in batch
        ]

        collection.bulk_write(operations)

        imported = min(
            start + batch_size,
            total,
        )

        print(f"{imported}/{total} documents traités")


def main() -> None:
    """Construit puis importe les documents dans MongoDB."""

    database = get_database()

    print("Connexion MongoDB réussie.")
    print(f"Base : {database.name}")

    collection = get_collection(database)

    print(f"Collection : {collection.name}")

    print("\nConstruction des documents...")
    documents = build_documents()

    print(f"{len(documents)} documents prêts à être importés.")

    print("\nImport MongoDB...")

    import_documents(
        collection,
        documents,
    )

    print("\nImport terminé.")

    print(
        "Nombre de documents dans MongoDB :",
        collection.count_documents({}),
    )


if __name__ == "__main__":
    main()
