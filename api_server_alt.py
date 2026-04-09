from fastapi import FastAPI

app = FastAPI()


@app.get("/products")
def get_products():
    return [
        {
            "item_id": "101",
            "title": "Gaming Laptop RTX 4070",
            "group_name": "electronics",
            "maker": "MSI",
            "unit_price": 1899.99,
            "details": "High performance gaming laptop"
        },
        {
            "item_id": "102",
            "title": "Wireless Headphones Sony",
            "group_name": "electronics",
            "maker": "Sony",
            "unit_price": 199.99,
            "details": "Noise cancelling headphones"
        },
        {
            "item_id": "103",
            "title": "Office Chair Ergonomic",
            "group_name": "furniture",
            "maker": "Ikea",
            "unit_price": 149.99,
            "details": "Comfortable office chair"
        }
    ]


@app.get("/stock")
def get_stock():
    return [
        {"item_ref": "101", "available_count": 3},
        {"item_ref": "102", "available_count": 10},
        {"item_ref": "103", "available_count": 0}
    ]


@app.get("/orders")
def get_orders():
    return [
        {"code": "ORD9001", "state": "delivered"},
        {"code": "ORD9002", "state": "cancelled"}
    ]