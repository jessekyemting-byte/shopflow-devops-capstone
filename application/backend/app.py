import os
import redis
import psycopg2
from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_NAME", "shopflow")
DB_USER = os.getenv("DB_USER", "shopuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "shoppassword")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, connect_timeout=3
    )

@app.route('/health', methods=['GET'])
def health():
    try:
        conn = get_db_connection()
        conn.close()
        r = redis.Redis(host=REDIS_HOST, port=6379, socket_timeout=2)
        r.ping()
        return jsonify({"status": "healthy", "database": "connected", "redis": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/ready', methods=['GET'])
def ready():
    return jsonify({"status": "ready"}), 200

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify([
        {"id": 1, "name": "DevOps Handbook", "price": 29.99},
        {"id": 2, "name": "Kubernetes in Action", "price": 45.00}
    ]), 200

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json() or {}
    return jsonify({"status": "order_created", "order": data}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
