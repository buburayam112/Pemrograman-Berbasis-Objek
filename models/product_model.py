"""
product_model.py — Model untuk manajemen produk dan kategori.

ProductModel dan CategoryModel mewarisi BaseModel (Inheritance).
Method validate() di-override sesuai aturan bisnis produk (Polymorphism).
"""

from models.base_model import BaseModel


class CategoryModel(BaseModel):
    """Model untuk operasi CRUD tabel categories."""

    def __init__(self):
        super().__init__("categories")

    def validate(self, data):
        """Validasi data kategori."""
        if not data.get("nama_kategori", "").strip():
            raise ValueError("Nama kategori tidak boleh kosong")

    def add(self, nama_kategori):
        """Tambah kategori baru."""
        self.validate({"nama_kategori": nama_kategori})
        return self._execute(
            "INSERT INTO categories (nama_kategori) VALUES (?)",
            (nama_kategori.strip(),)
        )

    def update(self, cat_id, nama_kategori):
        """Update nama kategori."""
        self.validate({"nama_kategori": nama_kategori})
        return self._execute(
            "UPDATE categories SET nama_kategori = ? WHERE id = ?",
            (nama_kategori.strip(), cat_id)
        )


class ProductModel(BaseModel):
    """
    Model untuk operasi CRUD tabel products.
    
    Menyediakan method khusus untuk pencarian, filter berdasarkan
    kategori, dan pengecekan stok minimum.
    """

    def __init__(self):
        super().__init__("products")

    def validate(self, data):
        """
        Validasi data produk.
        
        Aturan bisnis:
        - Kode barang wajib diisi
        - Nama barang wajib diisi
        - Harga beli & jual tidak boleh negatif
        - Stok tidak boleh negatif
        
        Args:
            data: dict berisi field-field produk
            
        Raises:
            ValueError: Jika ada data yang tidak valid
        """
        if not data.get("kode_barang", "").strip():
            raise ValueError("Kode barang tidak boleh kosong")
        if not data.get("nama_barang", "").strip():
            raise ValueError("Nama barang tidak boleh kosong")
        
        harga_beli = data.get("harga_beli", 0)
        harga_jual = data.get("harga_jual", 0)
        stok = data.get("stok", 0)
        
        if float(harga_beli) < 0:
            raise ValueError("Harga beli tidak boleh negatif")
        if float(harga_jual) < 0:
            raise ValueError("Harga jual tidak boleh negatif")
        if int(stok) < 0:
            raise ValueError("Stok tidak boleh negatif")

    def get_all(self):
        """Ambil semua produk beserta nama kategori (JOIN)."""
        return self._fetch_all("""
            SELECT p.*, c.nama_kategori 
            FROM products p
            LEFT JOIN categories c ON p.kategori_id = c.id
            ORDER BY p.kode_barang
        """)

    def get_by_id(self, product_id):
        """Ambil satu produk beserta nama kategori."""
        return self._fetch_one("""
            SELECT p.*, c.nama_kategori 
            FROM products p
            LEFT JOIN categories c ON p.kategori_id = c.id
            WHERE p.id = ?
        """, (product_id,))

    def search(self, keyword):
        """Cari produk berdasarkan kode atau nama barang."""
        like = f"%{keyword}%"
        return self._fetch_all("""
            SELECT p.*, c.nama_kategori 
            FROM products p
            LEFT JOIN categories c ON p.kategori_id = c.id
            WHERE p.kode_barang LIKE ? OR p.nama_barang LIKE ?
            ORDER BY p.kode_barang
        """, (like, like))

    def add(self, kode_barang, nama_barang, kategori_id, harga_beli, 
            harga_jual, stok, stok_minimum):
        """Tambah produk baru."""
        data = {
            "kode_barang": kode_barang, "nama_barang": nama_barang,
            "harga_beli": harga_beli, "harga_jual": harga_jual,
            "stok": stok
        }
        self.validate(data)
        return self._execute(
            """INSERT INTO products 
               (kode_barang, nama_barang, kategori_id, harga_beli, 
                harga_jual, stok, stok_minimum) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (kode_barang.strip(), nama_barang.strip(), kategori_id,
             float(harga_beli), float(harga_jual), int(stok), int(stok_minimum))
        )

    def update(self, product_id, kode_barang, nama_barang, kategori_id,
               harga_beli, harga_jual, stok, stok_minimum):
        """Update data produk."""
        data = {
            "kode_barang": kode_barang, "nama_barang": nama_barang,
            "harga_beli": harga_beli, "harga_jual": harga_jual,
            "stok": stok
        }
        self.validate(data)
        return self._execute(
            """UPDATE products 
               SET kode_barang=?, nama_barang=?, kategori_id=?,
                   harga_beli=?, harga_jual=?, stok=?, stok_minimum=?
               WHERE id=?""",
            (kode_barang.strip(), nama_barang.strip(), kategori_id,
             float(harga_beli), float(harga_jual), int(stok), 
             int(stok_minimum), product_id)
        )

    def update_stock(self, product_id, new_stock):
        """Update stok produk secara langsung."""
        if int(new_stock) < 0:
            raise ValueError("Stok tidak boleh negatif")
        return self._execute(
            "UPDATE products SET stok = ? WHERE id = ?",
            (int(new_stock), product_id)
        )

    def get_low_stock(self):
        """Ambil produk dengan stok di bawah stok_minimum."""
        return self._fetch_all("""
            SELECT p.*, c.nama_kategori 
            FROM products p
            LEFT JOIN categories c ON p.kategori_id = c.id
            WHERE p.stok < p.stok_minimum
            ORDER BY p.stok ASC
        """)

    def check_kode_unique(self, kode_barang, exclude_id=None):
        """Cek apakah kode barang sudah dipakai produk lain."""
        if exclude_id:
            row = self._fetch_one(
                "SELECT id FROM products WHERE kode_barang = ? AND id != ?",
                (kode_barang, exclude_id)
            )
        else:
            row = self._fetch_one(
                "SELECT id FROM products WHERE kode_barang = ?",
                (kode_barang,)
            )
        return row is None  # True jika unik
