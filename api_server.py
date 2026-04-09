from fastapi import FastAPI
import json
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_json(filename):
    path = os.path.join(BASE_DIR, "backend_mock", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/products")
def get_products():
    return load_json("products.json")


@app.get("/stock")
def get_stock():
    return load_json("stock.json")


@app.get("/orders")
def get_orders():
    return load_json("orders.json")