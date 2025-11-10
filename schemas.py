"""
Database Schemas for Lobster Business

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase class name.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Literal

class Lobsterproduct(BaseModel):
    """
    Collection: "lobsterproduct"
    Represents a lobster item for sale (seed/juvenile, broodstock, consumption).
    """
    name: str = Field(..., description="Product name, e.g., Benih Lobster 2-3 cm")
    type: Literal["benih", "induk", "konsumsi"] = Field(..., description="Jenis produk")
    size: Optional[str] = Field(None, description="Ukuran/grade, misal 2-3 cm atau 100-150 gr")
    price: float = Field(..., ge=0, description="Harga dalam Rupiah")
    stock: int = Field(0, ge=0, description="Stok tersedia (ekor/kg)")
    unit: Literal["ekor", "kg"] = Field("ekor", description="Satuan stok/penjualan")
    description: Optional[str] = Field(None, description="Deskripsi singkat")
    image_url: Optional[HttpUrl] = Field(None, description="URL foto produk")

class Inquiry(BaseModel):
    """
    Collection: "inquiry"
    Leads/pertanyaan dari pengunjung website.
    """
    name: str = Field(..., description="Nama pelanggan")
    phone: str = Field(..., description="Nomor WhatsApp/telepon")
    email: Optional[str] = Field(None, description="Email (opsional)")
    message: str = Field(..., description="Pesan atau kebutuhan")
    source: Optional[str] = Field("website", description="Sumber lead")
