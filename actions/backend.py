import json
import os
import requests

# Umožňuje prepínať zdroj dát bez zmeny zvyšku aplikácie.
BACKEND_PROVIDER = os.getenv("BACKEND_PROVIDER", "mock")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
GENERIC_API_CONFIG = os.getenv("GENERIC_API_CONFIG", "generic_api_config.json")


def _project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _load_json(filename):
    path = os.path.join(_project_root(), "backend_mock", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_generic_config():
    path = os.path.join(_project_root(), GENERIC_API_CONFIG)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Niektoré API vracajú položky priamo, iné ich majú vnorené v odpovedi.
def _extract_items(data, items_path):
    if not items_path:
        return data
    current = data
    for part in items_path.split("."):
        current = current[part]
    return current

# Zjednotenie názvov polí z rôznych API na jednodtný formát.
def _map_item(item, mapping):
    mapped = {}
    for target_key, source_key in mapping.items():
        mapped[target_key] = item.get(source_key)
    return mapped


def _generic_fetch(resource_name):
    config = _load_generic_config()
    resource = config[resource_name]

    url = config["base_url"].rstrip("/") + resource["endpoint"]
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()
    items = _extract_items(data, resource.get("items_path", ""))

    if isinstance(items, dict):
        items = [items]

    mapped = [_map_item(item, resource["mapping"]) for item in items]
    return mapped


def get_products():
    if BACKEND_PROVIDER == "mock":
        return _load_json("products.json")

    if BACKEND_PROVIDER == "local_api":
        response = requests.get(f"{API_BASE_URL}/products", timeout=5)
        response.raise_for_status()
        return response.json()

    if BACKEND_PROVIDER == "generic_api":
        products = _generic_fetch("products")
        normalized = []
        for p in products:
            normalized.append({
                "id": str(p.get("id", "")),
                "name": p.get("name", "") or "",
                "category": p.get("category", "") or "",
                "brand": p.get("brand", "") or "",
                "price": float(p.get("price", 0) or 0),
                "description": p.get("description", "") or ""
            })
        return normalized

    raise ValueError(f"Unknown BACKEND_PROVIDER: {BACKEND_PROVIDER}")


def get_stock():
    if BACKEND_PROVIDER == "mock":
        return _load_json("stock.json")

    if BACKEND_PROVIDER == "local_api":
        response = requests.get(f"{API_BASE_URL}/stock", timeout=5)
        response.raise_for_status()
        return response.json()

    if BACKEND_PROVIDER == "generic_api":
        stock_items = _generic_fetch("stock")
        normalized = []
        for s in stock_items:
            normalized.append({
                "product_id": str(s.get("product_id", "")),
                "stock": int(s.get("stock", 0) or 0)
            })
        return normalized

    raise ValueError(f"Unknown BACKEND_PROVIDER: {BACKEND_PROVIDER}")


def get_orders():
    if BACKEND_PROVIDER == "mock":
        return _load_json("orders.json")

    if BACKEND_PROVIDER == "local_api":
        response = requests.get(f"{API_BASE_URL}/orders", timeout=5)
        response.raise_for_status()
        return response.json()

    if BACKEND_PROVIDER == "generic_api":
        orders = _generic_fetch("orders")
        normalized = []
        for o in orders:
            normalized.append({
                "order_id": str(o.get("order_id", "")),
                "status": o.get("status", "") or ""
            })
        return normalized

    raise ValueError(f"Unknown BACKEND_PROVIDER: {BACKEND_PROVIDER}")