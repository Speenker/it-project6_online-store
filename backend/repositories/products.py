import psycopg2
import psycopg2.extras
import os
from elasticsearch import Elasticsearch
from fastapi import HTTPException
import traceback

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
    "user": os.getenv("POSTGRES_USER", "user"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
    "dbname": os.getenv("POSTGRES_DB", "store_db"),
}

def get_all_products():
    query = "SELECT product_id, name, price FROM products"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()

def get_product_details(product_id):
    query = "SELECT * FROM products WHERE product_id = %s"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, (product_id,))
            return cur.fetchone()

def get_product_reviews(product_id):
    query = "SELECT r.review_text, r.rating FROM reviews r WHERE r.product_id = %s"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, (product_id,))
            return cur.fetchall()

def get_manufacturer_name(manufacturer_id):
    query = "SELECT name FROM manufacturers WHERE manufacturer_id = %s"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (manufacturer_id,))
            row = cur.fetchone()
            return row[0] if row else None

def search_products(query):
    try:
        es = Elasticsearch(hosts=[{"host": os.getenv("ELASTIC_HOST", "elasticsearch"), "port": int(os.getenv("ELASTIC_PORT", 9200)), "scheme": "http"}])
        es_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["name", "description"]
                }
            }
        }
        res = es.search(index="products", body=es_query)
        hits = res.get("hits", {}).get("hits", [])
        return [hit["_source"] for hit in hits]
    except Exception as e:
        print("Elasticsearch search error:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Elasticsearch error: {str(e)}") 