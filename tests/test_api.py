"""Tests automatisés de l'API FastAPI."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_root() -> None:
    """Vérifie que la route racine fonctionne."""

    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {"message": "Olist API is running"}


def test_get_existing_order() -> None:
    """Vérifie la récupération d'une commande existante."""

    order_id = "e481f51cbdc54678b7cc49136f2d6af7"

    response = client.get(f"/orders/{order_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["order_id"] == order_id
    assert data["status"] == "delivered"


def test_get_unknown_order() -> None:
    """Vérifie qu'une commande inexistante retourne 404."""

    response = client.get("/orders/commande_inexistante")

    assert response.status_code == 404

    assert response.json() == {"detail": "Commande introuvable"}


def test_invalid_limit() -> None:
    """Vérifie qu'un limit inférieur à 1 retourne 422."""

    response = client.get("/orders/status/delivered?limit=0")

    assert response.status_code == 422


def test_sales_by_category() -> None:
    """Vérifie la route d'agrégation des ventes par catégorie."""

    response = client.get("/analytics/categories/sales?limit=3")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3

    assert "category" in data[0]
    assert "total_sales" in data[0]
    assert "items_sold" in data[0]
