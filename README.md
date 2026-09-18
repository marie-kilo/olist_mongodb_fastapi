# Olist - MongoDB & FastAPI

Projet Data Engineering basé sur le dataset public **Brazilian E-Commerce Public Dataset by Olist**.

L'objectif du projet est de transformer plusieurs fichiers CSV liés en un modèle documentaire MongoDB cohérent, puis de mettre ces données à disposition via une API REST développée avec FastAPI.

Le projet couvre la chaîne suivante :

```text
CSV Olist
   ↓
Analyse et contrôle qualité
   ↓
Transformation des données
   ↓
Modélisation documentaire
   ↓
MongoDB
   ↓
Requêtes et agrégations
   ↓
FastAPI
   ↓
API REST
   ↓
JSON
```

---

# 1. Objectifs du projet

Les principaux objectifs sont :

- analyser plusieurs fichiers liés du dataset Olist ;
- comprendre leurs relations ;
- contrôler les types, valeurs manquantes, doublons et incohérences ;
- sélectionner les données utiles aux usages retenus ;
- proposer une modélisation MongoDB adaptée ;
- réaliser un import reproductible ;
- développer plusieurs requêtes MongoDB ;
- réaliser au moins deux agrégations utiles ;
- analyser les performances d'une requête avec `explain()` ;
- mettre en place un index justifié ;
- exposer les données avec FastAPI ;
- maîtriser le volume des réponses ;
- valider les paramètres reçus par l'API ;
- gérer les erreurs HTTP ;
- fournir une documentation Swagger/OpenAPI exploitable ;
- mettre en place des tests automatisés.

---

# 2. Dataset Olist

Le dataset Olist contient des données issues d'une plateforme e-commerce brésilienne.

Il contient environ **100 000 commandes réalisées entre 2016 et 2018**.

Source :

**Brazilian E-Commerce Public Dataset by Olist - Kaggle**

## Fichiers exploités

Le projet utilise principalement six fichiers liés :

```text
olist_orders_dataset.csv
olist_customers_dataset.csv
olist_order_items_dataset.csv
olist_order_payments_dataset.csv
olist_order_reviews_dataset.csv
olist_products_dataset.csv
```

Ces fichiers permettent de couvrir les principaux besoins retenus :

- commandes ;
- clients ;
- articles commandés ;
- produits ;
- paiements ;
- avis clients.

Le fichier de géolocalisation n'est pas nécessaire aux usages retenus dans ce projet.

---

# 3. Relations entre les fichiers

Les principales relations identifiées sont :

```text
olist_orders_dataset
        │
        │ customer_id
        ▼
olist_customers_dataset
```

```text
olist_orders_dataset
        │
        │ order_id
        ▼
olist_order_items_dataset
```

```text
olist_orders_dataset
        │
        │ order_id
        ▼
olist_order_payments_dataset
```

```text
olist_orders_dataset
        │
        │ order_id
        ▼
olist_order_reviews_dataset
```

```text
olist_order_items_dataset
        │
        │ product_id
        ▼
olist_products_dataset
```

Les contrôles d'intégrité référentielle réalisés sur ces relations principales n'ont détecté aucune référence inexistante.

---

# 4. Volumes analysés

| Fichier | Nombre de lignes |
|---|---:|
| Orders | 99 441 |
| Customers | 99 441 |
| Order items | 112 650 |
| Payments | 103 886 |
| Reviews | 99 224 |
| Products | 32 951 |

Quelques informations complémentaires :

- `customer_id` est unique dans le fichier `customers` ;
- plusieurs `customer_id` peuvent appartenir au même `customer_unique_id` ;
- certaines commandes possèdent plusieurs articles ;
- certaines commandes possèdent plusieurs paiements ;
- certaines commandes possèdent plusieurs avis.

---

# 5. Analyse et qualité des données

L'analyse est réalisée dans :

```text
src/analyse.py
```

Le script permet notamment d'analyser :

- le nombre de lignes et colonnes ;
- les noms de colonnes ;
- les types ;
- les valeurs manquantes ;
- les doublons complets ;
- les identifiants uniques ;
- les relations entre fichiers ;
- l'intégrité référentielle ;
- certaines incohérences métier.

---

## 5.1 Contrôles d'intégrité

Les relations suivantes ont été contrôlées :

```text
orders.customer_id
→ customers.customer_id

order_items.order_id
→ orders.order_id

payments.order_id
→ orders.order_id

reviews.order_id
→ orders.order_id

order_items.product_id
→ products.product_id
```

Les contrôles réalisés n'ont pas détecté de références inexistantes sur ces relations.

---

## 5.2 Dates de livraison

Le projet contrôle les commandes avec :

```text
order_status = delivered
```

mais sans :

```text
order_delivered_customer_date
```

Le projet a identifié **8 commandes** dans cette situation.

Le choix retenu est de :

- conserver la commande ;
- conserver le statut `delivered` ;
- laisser la date manquante à `null` ;
- ne pas inventer de valeur.

---

## 5.3 Prix et paiements

Les contrôles suivants ont été réalisés :

```text
price < 0
freight_value < 0
payment_value < 0
```

Résultat :

```text
0 prix négatif
0 frais de livraison négatif
0 paiement négatif
```

---

## 5.4 Avis

Les scores doivent être compris entre :

```text
1 et 5
```

Aucun score hors de cet intervalle n'a été détecté.

Les champs :

```text
review_comment_title
review_comment_message
```

peuvent contenir des valeurs manquantes.

Ces valeurs sont conservées sous forme :

```python
None
```

dans Python puis :

```json
null
```

dans MongoDB et dans les réponses JSON.

---

# 6. Choix de modélisation MongoDB

La structure relationnelle des CSV n'est pas reproduite automatiquement dans MongoDB.

Les usages retenus sont principalement centrés sur la **commande**.

Le choix a donc été de créer une collection principale :

```text
orders
```

Chaque document représente une commande complète avec les informations nécessaires à ses principaux usages.

---

# 7. Structure d'un document MongoDB

Exemple simplifié :

```json
{
  "order_id": "e481f51cbdc54678b7cc49136f2d6af7",
  "status": "delivered",

  "customer": {
    "customer_id": "9ef432eb6251297304e76186b10a928d",
    "customer_unique_id": "7c396fd4830fd04220f754e42b4e5bff",
    "zip_code_prefix": 3149,
    "city": "sao paulo",
    "state": "SP"
  },

  "dates": {
    "purchase": "2017-10-02T10:56:33",
    "approved": "2017-10-02T11:07:15",
    "delivered_carrier": "2017-10-04T19:55:00",
    "delivered_customer": "2017-10-10T21:25:13",
    "estimated_delivery": "2017-10-18T00:00:00"
  },

  "items": [
    {
      "order_item_id": 1,
      "product_id": "87285b34884572647811a353c7ac498a",
      "seller_id": "3504c0cb71d7fa48d967e0e4c94d59d9",
      "category": "utilidades_domesticas",
      "price": 29.99,
      "freight_value": 8.72
    }
  ],

  "payments": [
    {
      "sequence": 1,
      "type": "credit_card",
      "installments": 1,
      "value": 18.12
    }
  ],

  "reviews": [
    {
      "review_id": "a54f0611adc9ed256b57ede6b6eb5114",
      "score": 4,
      "title": null,
      "message": "...",
      "creation_date": "2017-10-11T00:00:00",
      "answer_timestamp": "2017-10-12T03:43:48"
    }
  ]
}
```

MongoDB ajoute également automatiquement un champ :

```text
_id
```

de type `ObjectId`.

---

# 8. Pourquoi embarquer ces données ?

Les données suivantes sont intégrées dans le document commande :

- client ;
- articles ;
- catégorie produit ;
- paiements ;
- avis.

Ce choix est cohérent avec les usages retenus.

Une commande peut ainsi être récupérée avec :

```text
commande
+ client
+ articles
+ paiements
+ avis
```

sans avoir besoin de reconstruire plusieurs jointures.

Le modèle permet également d'interroger directement des champs imbriqués avec la notation MongoDB :

```text
customer.customer_unique_id
customer.state
```

Les fichiers qui ne répondent pas directement aux usages retenus, comme la
géolocalisation, les vendeurs ou la traduction des catégories, ne sont pas
intégrés au document final.

Ce choix permet d'éviter de surcharger les documents avec des informations
qui ne sont pas utilisées par les routes actuelles de l'API.

---

# 9. Transformation des données

La transformation est réalisée dans :

```text
src/transform.py
```

Le script :

1. charge les six fichiers CSV ;
2. convertit les colonnes de dates ;
3. enrichit les articles avec leur catégorie produit ;
4. regroupe les articles par commande ;
5. regroupe les paiements par commande ;
6. regroupe les avis par commande ;
7. ajoute les informations client ;
8. construit les documents MongoDB finaux.

Les dates Pandas sont converties en objets Python :

```python
datetime
```

Les valeurs manquantes sont converties en :

```python
None
```

avant l'insertion dans MongoDB.

---

# 10. Connexion MongoDB et import

La connexion et l'import sont gérés dans :

```text
src/database.py
```

La base utilisée est :

```text
olist
```

La collection finale est :

```text
orders
```

Le nombre final de documents est :

```text
99 441
```

---

## 10.1 Authentification MongoDB

Les informations de connexion sont chargées depuis :

```text
.env
```

Le mot de passe n'est donc pas écrit directement dans le code.

Exemple :

```env
MONGO_USER=your_username
MONGO_PASSWORD=your_password
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=olist
MONGO_COLLECTION=orders
MONGO_AUTH_SOURCE=admin
```

### Création de l'utilisateur MongoDB

Si l'utilisateur MongoDB n'existe pas encore, il peut être créé dans la base
d'authentification `admin`.

Depuis `mongosh` :

```javascript
use admin

db.createUser({
  user: "admin",
  pwd: "votre_mot_de_passe",
  roles: [
    {
      role: "readWrite",
      db: "olist"
    }
  ]
})
```

Le fichier `.env` doit ensuite contenir les mêmes informations :

```env
MONGO_USER=admin
MONGO_PASSWORD=votre_mot_de_passe
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=olist
MONGO_COLLECTION=orders
MONGO_AUTH_SOURCE=admin
```

Le mot de passe réel ne doit jamais être ajouté au dépôt Git.

---


## 10.2 Import reproductible

L'import utilise :

```python
ReplaceOne(
    {"order_id": document["order_id"]},
    document,
    upsert=True,
)
```

Cela signifie :

- si la commande existe déjà, elle est remplacée ;
- si elle n'existe pas, elle est insérée.

L'import peut donc être rejoué sans créer de doublons de commandes.

Les opérations sont envoyées par lots avec :

```python
bulk_write()
```

---

## 10.3 Index unique sur `order_id`

Lors de l'import, un index unique est créé sur :

```text
order_id
```

Il garantit qu'un même `order_id` ne peut pas apparaître plusieurs fois dans la collection.

---

# 11. Architecture du projet

```text
olist_mongodb_fastapi/
│
├── api/
│   ├── __init__.py
│   └── main.py
│
├── data/
│   └── raw/
│
├── src/
│   ├── __init__.py
│   ├── analyse.py
│   ├── transform.py
│   ├── database.py
│   ├── queries.py
│   ├── aggregations.py
│   └── performance.py
│
├── tests/
│   └── test_api.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```
> Le fichier `.env` est créé localement à partir de `.env.example`.  
> Il contient les identifiants de connexion et n'est pas versionné.

---

# 12. Rôle des fichiers

## `src/analyse.py`

Analyse :

- les fichiers ;
- les types ;
- les valeurs manquantes ;
- les doublons ;
- les relations ;
- les incohérences métier.

---

## `src/transform.py`

Transforme les fichiers CSV en documents Python adaptés à MongoDB.

---

## `src/database.py`

Gère :

- la connexion à MongoDB ;
- l'authentification ;
- la construction des documents ;
- l'import par batch ;
- les upserts ;
- l'index unique sur `order_id`.

---

## `src/queries.py`

Contient les principales requêtes MongoDB de consultation.

---

## `src/aggregations.py`

Contient les pipelines d'agrégation MongoDB.

---

## `src/performance.py`

Analyse les performances avec :

```text
explain()
```

et compare la même requête avant et après création d'un index.

---

## `api/main.py`

Contient :

- l'application FastAPI ;
- les routes REST ;
- la validation des paramètres ;
- les erreurs HTTP ;
- la documentation Swagger/OpenAPI.

---

## `tests/test_api.py`

Contient les tests automatisés des comportements essentiels de l'API.

---

# 13. Installation

## Prérequis

Le projet nécessite :

- Python ;
- MongoDB ;
- Git.

Le serveur MongoDB doit être démarré avant l'import et avant l'utilisation de l'API.

---

## Cloner le dépôt

```bash
git clone https://github.com/marie-kilo/olist_mongodb_fastapi.git
```

Puis :

```bash
cd olist_mongodb_fastapi
```

---

## Créer un environnement virtuel

```bash
python -m venv env
```

Sous Windows :

```powershell
env\Scripts\activate
```

---

## Installer les dépendances

```bash
pip install -r requirements.txt
```

---

# 14. Dépendances principales

Le projet utilise notamment :

```text
pandas
pymongo
python-dotenv
fastapi
uvicorn
pytest
httpx
ruff
```

| Technologie | Utilisation |
|---|---|
| Pandas | Lecture et transformation des CSV |
| PyMongo | Communication Python ↔ MongoDB |
| python-dotenv | Lecture du fichier `.env` |
| FastAPI | API REST |
| Uvicorn | Serveur ASGI |
| Pytest | Tests automatisés |
| HTTPX | Client utilisé par TestClient |
| Ruff | Qualité du code |

---

# 15. Configuration du fichier `.env`

Créer un fichier :

```text
.env
```

à partir de :

```text
.env.example
```

Exemple :

```env
MONGO_USER=your_username
MONGO_PASSWORD=your_password
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=olist
MONGO_COLLECTION=orders
MONGO_AUTH_SOURCE=admin
```

Le fichier :

```text
.env
```

contient les vraies informations locales et ne doit pas être versionné.

Le fichier :

```text
.env.example
```

contient uniquement des valeurs d'exemple.

---

# 16. Initialisation du projet

Le projet n'utilise volontairement pas un seul `main.py` qui exécute automatiquement toutes les étapes.

Chaque fichier possède un rôle spécifique.

Cela permet de séparer :

```text
analyse
transformation
import
requêtes
agrégations
performance
API
tests
```

---

## Première utilisation

Lors de la première installation du projet, il faut :

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Configurer `.env`

Créer le fichier à partir de `.env.example`.

### 3. Vérifier que MongoDB est démarré

### 4. Importer les données

```bash
python -m src.database
```

### 5. Lancer FastAPI

```bash
uvicorn api.main:app --reload
```

---

# 17. Utilisation quotidienne

Une fois les données importées dans MongoDB, il n'est pas nécessaire de relancer :

```bash
python -m src.database
```

à chaque utilisation.

Il suffit normalement de démarrer MongoDB puis de lancer :

```bash
uvicorn api.main:app --reload
```

FastAPI appellera automatiquement les fonctions présentes dans :

```text
queries.py
aggregations.py
database.py
```

selon la route demandée.

---

# 18. Quels fichiers faut-il exécuter ?

## `analyse.py`

À utiliser uniquement lorsqu'on souhaite refaire l'analyse des données :

```bash
python -m src.analyse
```

Ce n'est pas nécessaire au démarrage quotidien de l'API.

---

## `transform.py`

Ce fichier contient les fonctions de transformation utilisées par l'import.

Il n'est normalement pas nécessaire de le lancer manuellement.

---

## `database.py`

À lancer lors de l'initialisation ou lorsqu'on souhaite reconstruire/réimporter la collection :

```bash
python -m src.database
```

---

## `queries.py`

Contient les fonctions utilisées automatiquement par FastAPI.

Il n'est pas nécessaire de l'exécuter avant de lancer l'API.

---

## `aggregations.py`

Contient les fonctions d'agrégation utilisées automatiquement par FastAPI.

Il n'est pas nécessaire de l'exécuter avant de lancer l'API.

---

## `performance.py`

À lancer uniquement pour reproduire la démonstration `explain()` et index :

```bash
python -m src.performance
```

---

## `tests/`

À utiliser lorsqu'on souhaite vérifier automatiquement l'application :

```bash
python -m pytest -v
```

---

## `api/main.py`

C'est le point d'entrée principal du service FastAPI.

Il est lancé avec :

```bash
uvicorn api.main:app --reload
```

---

# 19. Fonctionnement automatique de FastAPI

Une fois l'API démarrée, il n'est pas nécessaire d'exécuter manuellement `queries.py` ou `aggregations.py`.

Exemple :

```text
GET /orders/{order_id}
        ↓
api/main.py
        ↓
find_order_by_id()
        ↓
queries.py
        ↓
PyMongo
        ↓
MongoDB
```

Pour une agrégation :

```text
GET /analytics/categories/sales
        ↓
api/main.py
        ↓
sales_by_category()
        ↓
aggregations.py
        ↓
MongoDB aggregate()
        ↓
JSON
```

---

# 20. Requêtes MongoDB

Les requêtes principales sont définies dans :

```text
src/queries.py
```

---

## 20.1 Recherche par `order_id`

```python
find_order_by_id()
```

Permet de retrouver une commande précise.

---

## 20.2 Recherche par statut

```python
find_orders_by_status()
```

Permet de récupérer plusieurs commandes selon leur statut.

Les résultats sont limités.

---

## 20.3 Recherche par client

```python
find_orders_by_customer()
```

La recherche utilise :

```text
customer.customer_unique_id
```

Le champ `customer_unique_id` permet d'identifier le même client à travers plusieurs commandes, même lorsque `customer_id` change.

---

## 20.4 Recherche par État

```python
find_orders_by_state()
```

La recherche utilise :

```text
customer.state
```

---

# 21. Agrégations MongoDB

Les agrégations sont définies dans :

```text
src/aggregations.py
```

Deux agrégations métier sont disponibles.

---

# 22. Agrégation 1 - ventes par catégorie

Fonction :

```python
sales_by_category()
```

Objectif :

> identifier les catégories ayant le montant d'articles vendus le plus élevé.

Pipeline :

```text
$unwind
   ↓
$match
   ↓
$group
   ↓
$sort
   ↓
$limit
   ↓
$project
```

---

## `$unwind`

Sépare le tableau :

```text
items
```

pour travailler article par article.

---

## `$match`

Ignore les articles pour lesquels :

```text
items.category = null
```

---

## `$group`

Regroupe les articles selon :

```text
items.category
```

---

## `$sum`

Calcule :

```text
total_sales
```

comme la somme de :

```text
items.price
```

et :

```text
items_sold
```

comme le nombre d'articles.

---

## `$sort`

Classe les catégories par montant décroissant.

---

## `$limit`

Limite le nombre de résultats.

---

## `$project`

Produit une réponse plus lisible pour l'API.

Exemple :

```json
{
  "category": "beleza_saude",
  "total_sales": 1258681.34,
  "items_sold": 9670
}
```

`total_sales` représente la somme du prix des articles.

Les frais de livraison ne sont pas inclus.

---

# 23. Agrégation 2 - statistiques par État

Fonction :

```python
sales_by_state()
```

Elle calcule pour chaque État :

- le nombre de commandes ;
- le montant total payé ;
- le montant moyen payé par commande.

Pipeline :

```text
$set
   ↓
$group
   ↓
$sort
   ↓
$limit
   ↓
$project
```

Exemple :

```json
{
  "state": "SP",
  "orders_count": 41746,
  "total_payment_value": 5998226.96,
  "average_order_value": 143.683872945911
}
```

---

# 24. Analyse des performances

L'analyse se trouve dans :

```text
src/performance.py
```

La requête analysée est :

> rechercher les commandes d'un client avec `customer.customer_unique_id`.

Cette requête correspond à un usage réel du service.

---

## Avant index

Résultat observé :

```text
Documents retournés : 2
Documents examinés : 99441
Clés d'index examinées : 0
Temps d'exécution observé : 71 ms
```

MongoDB devait parcourir toute la collection pour retrouver seulement deux documents.

---

## Index créé

Un index a été créé sur :

```text
customer.customer_unique_id
```

Nom :

```text
idx_customer_unique_id
```

---

## Après index

Résultat observé :

```text
Documents retournés : 2
Documents examinés : 2
Clés d'index examinées : 2
Temps d'exécution observé : 17 ms
```

La principale amélioration est :

```text
99 441 documents examinés
           ↓
2 documents examinés
```

Le temps d'exécution est donné uniquement à titre indicatif car il peut varier selon :

- la machine ;
- la mémoire ;
- le cache ;
- la charge système.

Le nombre de documents examinés est donc l'indicateur le plus significatif.

---

## Reproduire le test

```bash
python -m src.performance
```

Le script :

1. supprime l'index de test s'il existe ;
2. exécute `explain()` sans l'index ;
3. affiche les statistiques ;
4. crée l'index ;
5. rejoue exactement la même requête ;
6. affiche les statistiques après index.

---

# 25. Lancement de FastAPI

Lancer :

```bash
uvicorn api.main:app --reload
```

Le serveur devient disponible sur :

```text
http://127.0.0.1:8000
```

L'option :

```text
--reload
```

permet à Uvicorn de redémarrer automatiquement le serveur lorsqu'un fichier Python est modifié pendant le développement.

---

# 26. Flux FastAPI - MongoDB

Le fonctionnement général est :

```text
Client
   │
   │ requête HTTP
   ▼
FastAPI
   │
   │ validation
   ▼
fonction de requête
ou d'agrégation
   │
   │ PyMongo
   ▼
MongoDB
   │
   │ document ou résultat agrégé
   ▼
FastAPI
   │
   │ sérialisation JSON
   ▼
Client
```

---

# 27. Pourquoi utiliser une API ?

Donner un accès direct à MongoDB obligerait les clients à :

- connaître la structure de la base ;
- connaître les requêtes MongoDB ;
- posséder des identifiants de connexion ;
- gérer eux-mêmes les règles de validation.

Avec FastAPI, on ajoute une couche contrôlée.

L'API permet :

- de choisir les données exposées ;
- de valider les paramètres ;
- de limiter le volume des réponses ;
- de gérer les erreurs HTTP ;
- de centraliser les règles métier ;
- de fournir une interface stable ;
- de documenter les usages disponibles.

---

# 28. Routes FastAPI disponibles

## État de l'API

```http
GET /
```

Réponse :

```json
{
  "message": "Olist API is running"
}
```

---

## Rechercher une commande

```http
GET /orders/{order_id}
```

Exemple :

```text
/orders/e481f51cbdc54678b7cc49136f2d6af7
```

Commande trouvée :

```text
200 OK
```

Commande inexistante :

```text
404 Not Found
```

---

## Commandes par statut

```http
GET /orders/status/{status}
```

Exemple :

```text
/orders/status/delivered?limit=5
```

Statuts autorisés :

```text
approved
canceled
created
delivered
invoiced
processing
shipped
unavailable
```

Ces valeurs correspondent aux statuts réellement présents dans MongoDB.

---

## Commandes d'un client

```http
GET /customers/{customer_unique_id}/orders
```

Exemple :

```text
/customers/7c396fd4830fd04220f754e42b4e5bff/orders
```

---

## Commandes par État

```http
GET /states/{state}/orders
```

Exemple :

```text
/states/SP/orders?limit=5
```

États autorisés :

```text
AC
AL
AM
AP
BA
CE
DF
ES
GO
MA
MG
MS
MT
PA
PB
PE
PI
PR
RJ
RN
RO
RR
RS
SC
SE
SP
TO
```

Ces valeurs ont été récupérées à partir des valeurs réellement présentes dans :

```text
customer.state
```

avec MongoDB `distinct()`.

Une valeur comme :

```text
ZZ
```

est refusée.

---

## Ventes par catégorie

```http
GET /analytics/categories/sales
```

Exemple :

```text
/analytics/categories/sales?limit=5
```

---

## Statistiques par État

```http
GET /analytics/states/sales
```

Exemple :

```text
/analytics/states/sales?limit=5
```

---

# 29. Maîtrise du volume

Les routes retournant plusieurs documents utilisent :

```text
limit
```

Valeur par défaut :

```text
10
```

Minimum :

```text
1
```

Maximum :

```text
100
```

Exemples invalides :

```text
?limit=0
?limit=101
?limit=abc
```

Ces requêtes sont automatiquement refusées par FastAPI.

---

# 30. Validation des paramètres

FastAPI valide les paramètres avant l'interrogation de MongoDB.

---

## Validation de `limit`

La définition :

```python
limit: int = Query(
    default=10,
    ge=1,
    le=100,
)
```

signifie :

```text
limit doit être un entier
limit >= 1
limit <= 100
```

Une valeur invalide retourne :

```text
422
```

---

## Validation de `status`

Le type `Literal` limite le statut aux valeurs réellement présentes :

```python
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
```

Par exemple :

```text
delivered
```

est valide.

```text
test
```

est refusé avec :

```text
422
```

---

## Validation de `state`

Le type `StateCode` est également défini avec `Literal`.

Exemple :

```python
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
```

Par exemple :

```text
SP
```

est valide.

```text
ZZ
```

retourne :

```text
422
```

---

# 31. Gestion des erreurs HTTP

## Commande inexistante

Une commande inconnue retourne :

```text
404 Not Found
```

Réponse :

```json
{
  "detail": "Commande introuvable"
}
```

---

## Paramètres invalides

Les paramètres ne respectant pas les contraintes FastAPI retournent :

```text
422
```

Exemples :

```text
limit=0
limit=101
limit=abc
status=test
state=ZZ
```

---

# 32. Swagger UI

FastAPI génère automatiquement une documentation Swagger.

Une fois le serveur démarré :

```bash
uvicorn api.main:app --reload
```

Swagger est disponible sur :

```text
http://127.0.0.1:8000/docs
```

Swagger permet :

- de visualiser les routes ;
- de consulter leur description ;
- de voir les paramètres ;
- de voir les valeurs autorisées ;
- de tester directement les endpoints ;
- d'envoyer les requêtes avec `Try it out` ;
- de consulter le code HTTP ;
- de consulter la réponse JSON.

---

# 33. Organisation de Swagger

La documentation est organisée avec les tags :

```text
Health
Orders
Customers
States
Analytics
```

## Health

Vérification du fonctionnement de l'API.

## Orders

Consultation des commandes.

## Customers

Consultation de l'historique des clients.

## States

Consultation des commandes par État.

## Analytics

Accès aux résultats agrégés.

---

# 34. OpenAPI

FastAPI génère également automatiquement le schéma OpenAPI brut :

```text
http://127.0.0.1:8000/openapi.json
```

Ce fichier JSON constitue le **contrat technique de l'API**.

Il décrit notamment :

- le nom de l'API ;
- sa version ;
- les routes ;
- les méthodes HTTP ;
- les paramètres ;
- leur type ;
- les valeurs autorisées ;
- les limites ;
- les réponses HTTP ;
- les schémas d'erreur ;
- les tags.

Par exemple, OpenAPI contient automatiquement les valeurs possibles pour :

```text
status
```

et :

```text
state
```

ainsi que les contraintes :

```text
minimum = 1
maximum = 100
```

pour :

```text
limit
```

---

# 35. Relation entre FastAPI, OpenAPI et Swagger

Le fonctionnement est :

```text
Code FastAPI
     ↓
génération OpenAPI
     ↓
/openapi.json
     ↓
Swagger UI
     ↓
/docs
```

FastAPI analyse notamment :

- les décorateurs `@app.get()` ;
- les types Python ;
- les `Literal` ;
- les paramètres `Query` ;
- les descriptions ;
- les réponses HTTP.

Swagger utilise ensuite le schéma OpenAPI pour produire une interface interactive.

---

# 36. Exemple d'utilisation de Swagger

Pour tester une commande :

1. ouvrir :

```text
http://127.0.0.1:8000/docs
```

2. ouvrir :

```text
GET /orders/{order_id}
```

3. cliquer sur :

```text
Try it out
```

4. saisir par exemple :

```text
e481f51cbdc54678b7cc49136f2d6af7
```

5. cliquer sur :

```text
Execute
```

Swagger affiche ensuite :

- la requête HTTP ;
- l'URL appelée ;
- le code de réponse ;
- le JSON retourné.

---

# 37. Tests automatisés

Les tests sont définis dans :

```text
tests/test_api.py
```

Ils utilisent :

```text
pytest
FastAPI TestClient
```

Avant d'exécuter les tests, MongoDB doit être démarré, la configuration
`.env` doit être valide et les données Olist doivent avoir été importées
avec :

```bash
python -m src.database
```
Ainsi personne ne se demande pourquoi un test échoue sur une base vide.

---

Pour les exécuter :

```bash
python -m pytest -v
```

La commande `python -m pytest` est utilisée afin d'exécuter Pytest avec l'environnement Python courant et la racine du projet.

Résultat actuel :

```text
5 passed
```

---

# 38. Tests couverts

## Test 1 - API disponible

Vérifie :

```http
GET /
```

Résultat attendu :

```text
200
```

---

## Test 2 - commande existante

Vérifie qu'une commande connue retourne :

```text
200
```

et contient le bon :

```text
order_id
status
```

---

## Test 3 - commande inexistante

Vérifie :

```text
404
```

et :

```json
{
  "detail": "Commande introuvable"
}
```

---

## Test 4 - validation de `limit`

Vérifie qu'un :

```text
limit=0
```

retourne :

```text
422
```

---

## Test 5 - agrégation

Vérifie que :

```text
/analytics/categories/sales?limit=3
```

retourne :

- un code `200` ;
- exactement 3 résultats ;
- les champs :
  - `category`
  - `total_sales`
  - `items_sold`.

---

# 39. Reproductibilité complète

Pour reproduire le projet sur une autre machine :

## 1. Cloner

```bash
git clone https://github.com/marie-kilo/olist_mongodb_fastapi.git
cd olist_mongodb_fastapi
```

## 2. Créer l'environnement

```bash
python -m venv env
```

Sous Windows :

```powershell
env\Scripts\activate
```

## 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

## 4. Démarrer MongoDB

Vérifier que le serveur MongoDB est disponible.

## 5. Configurer `.env`

Créer :

```text
.env
```

à partir de :

```text
.env.example
```

## 6. Importer les données

```bash
python -m src.database
```

## 7. Lancer FastAPI

```bash
uvicorn api.main:app --reload
```

## 8. Tester Swagger

```text
http://127.0.0.1:8000/docs
```

## 9. Consulter OpenAPI

```text
http://127.0.0.1:8000/openapi.json
```

## 10. Lancer les tests

```bash
python -m pytest -v
```

## 11. Reproduire l'analyse de performance

```bash
python -m src.performance
```

---

# 40. Résumé des commandes

## Première installation

```bash
pip install -r requirements.txt
python -m src.database
uvicorn api.main:app --reload
```

---

## Utilisation normale après import

```bash
uvicorn api.main:app --reload
```

---

## Tests

```bash
python -m pytest -v
```

---

## Analyse de performance

```bash
python -m src.performance
```

---

## Analyse des données

```bash
python -m src.analyse
```

---

# 41. Technologies utilisées

```text
Python
Pandas
MongoDB
PyMongo
FastAPI
Uvicorn
Swagger UI
OpenAPI
Pytest
HTTPX
Ruff
Git
GitHub
```

---

# 42. Points forts du projet

- exploitation de six fichiers liés ;
- analyse de qualité des données ;
- contrôle de l'intégrité référentielle ;
- modèle MongoDB orienté commande ;
- sous-documents et tableaux imbriqués ;
- import reproductible avec `upsert` ;
- index unique sur `order_id` ;
- plusieurs usages de consultation ;
- deux agrégations métier ;
- limitation des volumes ;
- validation avec `Query` et `Literal` ;
- gestion des erreurs `404` et `422` ;
- analyse `explain()` ;
- index de performance justifié ;
- comparaison avant/après index ;
- API FastAPI connectée à MongoDB ;
- documentation Swagger interactive ;
- génération automatique OpenAPI ;
- tests automatisés ;
- configuration externalisée avec `.env`.

---

# 43. Limites et améliorations possibles

Plusieurs améliorations pourraient être ajoutées dans une évolution future :

- pagination avec `skip` et `limit` ;
- modèles Pydantic détaillés pour les réponses ;
- davantage de tests automatisés ;
- filtres temporels ;
- analyses par mois ou année ;
- endpoints supplémentaires pour les vendeurs ;
- nouveaux index uniquement après analyse avec `explain()` ;
- Dockerisation du service ;
- pipeline CI pour lancer automatiquement les tests ;
- authentification de l'API ;
- journalisation avec des logs ;
- déploiement sur un environnement distant.

Ces évolutions ne sont pas indispensables au périmètre retenu.

Le projet privilégie un service :

```text
cohérent
maîtrisé
reproductible
démontrable
```

plutôt qu'une multiplication de fonctionnalités incomplètes.

---

# 44. Conclusion

Ce projet met en œuvre une chaîne Data Engineering complète à partir de données e-commerce réelles.

Les données suivent le parcours :

```text
CSV
 ↓
Analyse
 ↓
Contrôle qualité
 ↓
Transformation
 ↓
Modélisation documentaire
 ↓
MongoDB
 ↓
Requêtes / Agrégations
 ↓
FastAPI
 ↓
Validation
 ↓
Swagger / OpenAPI
 ↓
JSON
 ↓
Client
```

MongoDB permet de stocker les informations d'une commande dans un document cohérent adapté aux usages retenus.

FastAPI joue le rôle d'intermédiaire entre MongoDB et les futurs consommateurs du service.

L'utilisation :

- de validations ;
- de limites ;
- d'erreurs HTTP ;
- de tests automatisés ;
- de documentation Swagger/OpenAPI ;
- d'une analyse `explain()` ;
- d'un index justifié ;

permet de rendre le service plus fiable, performant, documenté et réutilisable.