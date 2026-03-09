from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from models import UserCreate
router = APIRouter()
@router.post("/create_user")
def create_user(user: UserCreate):
    return user
sample_products = [
    {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.99},
    {"product_id": 456, "name": "Phone Case",  "category": "Accessories", "price": 19.99},
    {"product_id": 789, "name": "Iphone",      "category": "Electronics", "price": 1299.99},
    {"product_id": 101, "name": "Headphones",  "category": "Accessories", "price": 99.99},
    {"product_id": 202, "name": "Smartwatch",  "category": "Electronics", "price": 299.99},
]


@router.get("/product/{product_id}")
def get_product(product_id: int):
    for p in sample_products:
        if p["product_id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")
@router.get("/products/search")
def search_products(
    keyword: str,
    category: Optional[str] = None,
    limit: int = 10,
):
    results = [
        p for p in sample_products
        if keyword.lower() in p["name"].lower()
        and (category is None or p["category"].lower() == category.lower())
    ]
    return results[:limit]