"""API FastAPI du projet Olist."""

from typing import Literal

from fastapi import FastAPI, HTTPException, Query

from src.aggregations import (
    sales_by_category,
    sales_by_state,
)
from src.database import get_collection, get_database
from src.queries import (
    find_order_by_id,
    find_orders_by_customer,
    find_orders_by_state,
    find_orders_by_status,
)

app = FastAPI(
    title="Olist MongoDB API",
    description="API REST permettant de consulter les données Olist.",
    version="1.0.0",
)


database = get_database()
collection = get_collection(database)


OrderStatus = Literal[
    "approved",
    "canceled",
    "created",
    "delivered",
    "invoiced",
    "processing",
    "shipped",
    "unavailable",
]

StateCode = Literal[
    "AC",
    "AL",
    "AM",
    "AP",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MG",
    "MS",
    "MT",
    "PA",
    "PB",
    "PE",
    "PI",
    "PR",
    "RJ",
    "RN",
    "RO",
    "RR",
    "RS",
    "SC",
    "SE",
    "SP",
    "TO",
]


@app.get("/")
def root() -> dict:
    """Vérifie que l'API fonctionne."""

    return {"message": "Olist API is running"}


@app.get("/orders/{order_id}")
def get_order(order_id: str) -> dict:
    """Retourne une commande à partir de son identifiant."""

    order = find_order_by_id(
        collection,
        order_id,
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Commande introuvable",
        )

    order["_id"] = str(order["_id"])

    return order


@app.get("/orders/status/{status}")
def get_orders_by_status(
    status: OrderStatus,
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
) -> list[dict]:
    """Retourne les commandes correspondant à un statut."""

    orders = find_orders_by_status(
        collection,
        status=status,
        limit=limit,
    )

    for order in orders:
        order["_id"] = str(order["_id"])

    return orders


@app.get("/customers/{customer_unique_id}/orders")
def get_orders_by_customer(
    customer_unique_id: str,
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
) -> list[dict]:
    """Retourne les commandes d'un client unique."""

    orders = find_orders_by_customer(
        collection,
        customer_unique_id=customer_unique_id,
        limit=limit,
    )

    for order in orders:
        order["_id"] = str(order["_id"])

    return orders


@app.get("/states/{state}/orders")
def get_orders_by_state(
    state: StateCode,
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
) -> list[dict]:
    """Retourne les commandes d'un État."""

    orders = find_orders_by_state(
        collection,
        state=state,
        limit=limit,
    )

    for order in orders:
        order["_id"] = str(order["_id"])

    return orders


@app.get("/analytics/categories/sales")
def get_sales_by_category(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
) -> list[dict]:
    """Retourne les catégories par montant d'articles vendus."""

    return sales_by_category(
        collection,
        limit=limit,
    )


@app.get("/analytics/states/sales")
def get_sales_by_state(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
) -> list[dict]:
    """Retourne les statistiques de ventes par État."""

    return sales_by_state(
        collection,
        limit=limit,
    )
