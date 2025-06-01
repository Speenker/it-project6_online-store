import psycopg2
import psycopg2.extras
import os
from elasticsearch import Elasticsearch, helpers

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", 5433),
    "user": os.getenv("POSTGRES_USER", "user"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
    "dbname": os.getenv("POSTGRES_DB", "store_db"),
}

ES_HOST = os.getenv("ELASTIC_HOST", "elasticsearch")
ES_PORT = int(os.getenv("ELASTIC_PORT", 9200))


def get_all_products():
    query = "SELECT * FROM products"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()

def index_products(products):
    es = Elasticsearch(hosts=[{"host": ES_HOST, "port": ES_PORT, "scheme": "http"}])
    actions = [
        {
            "_index": "products",
            "_id": product["product_id"],
            "_source": product
        }
        for product in products
    ]
    helpers.bulk(es, actions)
    print(f"Indexed {len(actions)} products to Elasticsearch.")

if __name__ == "__main__":
    products = get_all_products()
    index_products(products) 