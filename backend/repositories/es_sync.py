import psycopg2
import psycopg2.extras
import os
from elasticsearch import Elasticsearch, helpers
import time

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
    "user": os.getenv("POSTGRES_USER", "user"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
    "dbname": os.getenv("POSTGRES_DB", "store_db"),
}

ES_HOST = os.getenv("ELASTIC_HOST", "elasticsearch")
ES_PORT = int(os.getenv("ELASTIC_PORT", 9200))

PRODUCTS_INDEX = "products"

# Используем только стандартный анализатор "russian"
PRODUCTS_MAPPING = {
    "mappings": {
        "properties": {
            "name": {"type": "text", "analyzer": "russian"},
            "description": {"type": "text", "analyzer": "russian"},
            "product_id": {"type": "integer"},
            "price": {"type": "float"},
            "stock": {"type": "integer"},
            "manufacturer_id": {"type": "integer"},
            "category_id": {"type": "integer"}
        }
    }
}

def get_all_products():
    for attempt in range(10):
        try:
            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute("SELECT * FROM products")
                    return cur.fetchall()
        except Exception as e:
            print(f"[get_all_products] Attempt {attempt+1}/10: PostgreSQL not ready: {e}")
            time.sleep(3)
    print("[get_all_products] ERROR: Could not connect to PostgreSQL after 10 attempts.")
    return []

def sync_products_to_es():
    try:
        es = None
        for attempt in range(10):
            try:
                es = Elasticsearch(hosts=[{"host": ES_HOST, "port": ES_PORT, "scheme": "http"}])
                if es.ping():
                    break
            except Exception as e:
                print(f"[sync_products_to_es] Attempt {attempt+1}/10: Elasticsearch not ready: {e}")
            time.sleep(3)
        else:
            print("[sync_products_to_es] ERROR: Could not connect to Elasticsearch after 10 attempts.")
            return
        # Проверяем, есть ли индекс
        if not es.indices.exists(index=PRODUCTS_INDEX):
            es.indices.create(index=PRODUCTS_INDEX, body=PRODUCTS_MAPPING)
        products = get_all_products()
        actions = [
            {
                "_index": PRODUCTS_INDEX,
                "_id": product["product_id"],
                "_source": product
            }
            for product in products
        ]
        if actions:
            helpers.bulk(es, actions)
        print(f"[sync_products_to_es] Indexed {len(actions)} products to Elasticsearch.")
    except Exception as e:
        import traceback
        print("[sync_products_to_es] ERROR:", e)
        traceback.print_exc() 