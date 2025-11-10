import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import create_document, get_documents, db
from schemas import Lobsterproduct, Inquiry

app = FastAPI(title="Lobster Air Tawar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Lobster Air Tawar Backend siap!"}

@app.get("/api/hello")
def hello():
    return {"message": "Halo dari backend lobster!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# --------- Business Endpoints ---------

@app.get("/api/products", response_model=List[Lobsterproduct])
def list_products(limit: Optional[int] = 50):
    """List lobster products from database."""
    try:
        docs = get_documents("lobsterproduct", limit=limit)
        # Map Mongo documents to Pydantic by selecting fields
        products: List[Lobsterproduct] = []
        for d in docs:
            try:
                products.append(Lobsterproduct(
                    name=d.get("name"),
                    type=d.get("type"),
                    size=d.get("size"),
                    price=float(d.get("price", 0)),
                    stock=int(d.get("stock", 0)),
                    unit=d.get("unit", "ekor"),
                    description=d.get("description"),
                    image_url=d.get("image_url")
                ))
            except Exception:
                # Skip invalid rows
                continue
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/inquiries")
def create_inquiry(inquiry: Inquiry):
    """Create a new customer inquiry (lead)."""
    try:
        _id = create_document("inquiry", inquiry)
        return {"status": "ok", "id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SeedRequest(BaseModel):
    force: bool = False

@app.post("/api/seed")
def seed_products(body: SeedRequest):
    """Seed database with example lobster products. Safe to call multiple times."""
    # Only seed if collection is empty or force is True
    try:
        existing = get_documents("lobsterproduct", limit=1)
        if existing and not body.force:
            return {"seeded": False, "message": "Products already exist"}
        samples = [
            {
                "name": "Benih Lobster Air Tawar 2-3 cm",
                "type": "benih",
                "size": "2-3 cm",
                "price": 3500,
                "stock": 5000,
                "unit": "ekor",
                "description": "Benih sehat siap tebar untuk pembesaran.",
                "image_url": "https://images.unsplash.com/photo-1544551763-7ef039d2fd88?q=80&w=1200"
            },
            {
                "name": "Lobster Konsumsi 100-150 gr",
                "type": "konsumsi",
                "size": "100-150 gr",
                "price": 230000,
                "stock": 120,
                "unit": "kg",
                "description": "Lobster air tawar segar untuk restoran dan rumah tangga.",
                "image_url": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?q=80&w=1200"
            },
            {
                "name": "Induk Lobster Siap Pijah",
                "type": "induk",
                "size": "Siap pijah",
                "price": 120000,
                "stock": 60,
                "unit": "ekor",
                "description": "Indukan pilihan produktif untuk pembenihan.",
                "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=1200"
            }
        ]
        for s in samples:
            try:
                create_document("lobsterproduct", s)
            except Exception:
                continue
        return {"seeded": True, "count": len(samples)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
