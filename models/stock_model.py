"""
stock_model.py — Model untuk manajemen stok gudang.

Mengelola mutasi stok masuk (restock) dan keluar (retur/rusak)
serta menyinkronkan perubahan ke tabel products secara instan.
"""

from datetime import datetime
from models.base_model import BaseModel


class StockModel(BaseModel):
    """
    Model untuk operasi database tabel stock_log.
    
    Setiap perubahan stok wajib tercatat di stock_log dan 
    tersinkron ke tabel products.
    """

    def __init__(self):
        super().__init__("stock_log")

    def validate(self, data):
        """
        Validasi data mutasi stok.
        
        Args:
            data: dict berisi 'produk_id', 'jenis', 'jumlah'
            
        Raises:
            ValueError: Jika data tidak valid
        """
        if not data.get("produk_id"):
            raise ValueError("Produk harus dipilih")
        if data.get("jenis") not in ("masuk", "keluar"):
            raise ValueError("Jenis mutasi harus 'masuk' atau 'keluar'")
        if int(data.get("jumlah", 0)) <= 0:
            raise ValueError("Jumlah harus lebih dari 0")

    def add_stock(self, produk_id, jenis, jumlah, keterangan=""):
        """
        Catat mutasi stok dan update stok produk.
        
        Args:
            produk_id: ID produk
            jenis: 'masuk' atau 'keluar'
            jumlah: Jumlah unit
            keterangan: Catatan/alasan mutasi
            
        Returns:
            int: ID log yang baru dibuat
            
        Raises:
            ValueError: Jika validasi gagal atau stok keluar melebihi tersedia
        """
        self.validate({
            "produk_id": produk_id,
            "jenis": jenis,
            "jumlah": jumlah
        })

        import sqlite3
        
        # Ambil stok saat ini
        current = self._fetch_one(
            "SELECT stok FROM products WHERE id = ?", (produk_id,)
        )
        if not current:
            raise ValueError("Produk tidak ditemukan")

        current_stock = int(current["stok"])
        jumlah = int(jumlah)

        if jenis == "masuk":
            new_stock = current_stock + jumlah
        else:  # keluar
            if jumlah > current_stock:
                raise ValueError(
                    f"Stok keluar ({jumlah}) melebihi stok tersedia ({current_stock})"
                )
            new_stock = current_stock - jumlah

        tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Eksekusi atomik
        cursor = self._conn.cursor()
        try:
            # Catat log
            cursor.execute(
                """INSERT INTO stock_log 
                   (produk_id, jenis, jumlah, keterangan, tanggal)
                   VALUES (?, ?, ?, ?, ?)""",
                (produk_id, jenis, jumlah, keterangan.strip(), tanggal)
            )
            log_id = cursor.lastrowid

            # Update stok produk
            cursor.execute(
                "UPDATE products SET stok = ? WHERE id = ?",
                (new_stock, produk_id)
            )

            self._conn.commit()
            return log_id

        except sqlite3.Error as e:
            self._conn.rollback()
            raise Exception(f"Gagal memproses mutasi stok: {e}")
        finally:
            cursor.close()

    def get_log(self, jenis_filter=None):
        """
        Ambil riwayat mutasi stok.
        
        Args:
            jenis_filter: 'masuk', 'keluar', atau None (semua)
        """
        if jenis_filter and jenis_filter in ("masuk", "keluar"):
            return self._fetch_all("""
                SELECT sl.*, p.kode_barang, p.nama_barang
                FROM stock_log sl
                LEFT JOIN products p ON sl.produk_id = p.id
                WHERE sl.jenis = ?
                ORDER BY sl.id DESC
            """, (jenis_filter,))
        else:
            return self._fetch_all("""
                SELECT sl.*, p.kode_barang, p.nama_barang
                FROM stock_log sl
                LEFT JOIN products p ON sl.produk_id = p.id
                ORDER BY sl.id DESC
            """)
