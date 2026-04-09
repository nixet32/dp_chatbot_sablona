import json
import os
import requests

USE_API = True
API_BASE_URL = "http://localhost:8000"


def _project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _load_json(filename):
    path = os.path.join(_project_root(), "backend_mock", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_products():
    if USE_API:
        response = requests.get(f"{API_BASE_URL}/products", timeout=5)
        response.raise_for_status()
        return response.json()
    return _load_json("products.json")


def get_stock():
    if USE_API:
        response = requests.get(f"{API_BASE_URL}/stock", timeout=5)
        response.raise_for_status()
        return response.json()
    return _load_json("stock.json")


def get_orders():
    if USE_API:
        response = requests.get(f"{API_BASE_URL}/orders", timeout=5)
        response.raise_for_status()
        return response.json()
    return _load_json("orders.json")