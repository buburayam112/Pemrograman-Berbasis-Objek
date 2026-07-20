"""
transaction_model.py — Model untuk transaksi penjualan kasir.

Mengelola operasi atomik: menyimpan transaksi header + items,
mengurangi stok produk, dan mencatat log stok keluar secara bersamaan.
"""

from datetime import datetime
from models.base_model import BaseModel


class TransactionModel(BaseModel):
    """
    Model untuk operasi database tabel transactions dan transaction_items.
    
    Transaksi bersifat atomik: jika salah satu operasi gagal,
    seluruh perubahan di-rollback.
    """

    def __init__(self):
        super().__init__("transactions")

    def validate(self, data):
        """
        Validasi data transaksi.
        
        Aturan bisnis:
        - Harus ada minimal 1 item di keranjang
        - Jumlah bayar harus >= total belanja
        - Setiap item harus memiliki qty > 0
        
        Args:
            data: dict berisi 'items' (list), 'bayar' (float), 'total' (float)
            
        Raises:
            ValueError: Jika data tidak valid
        """
        if not data.get("items"):
            raise ValueError("Keranjang belanja kosong")
        if float(data.get("bayar", 0)) < float(data.get("total", 0)):
            raise ValueError("Jumlah bayar kurang dari total belanja")
        for item in data["items"]:
            if int(item.get("qty", 0)) <= 0:
                raise ValueError(f"Qty harus lebih dari 0 untuk {item.get('nama', 'item')}")

    def _generate_no_transaksi(self):
        """
        Generate nomor transaksi unik: TRX-YYYYMMDD-XXXX.
        
        Returns:
            str: Nomor transaksi unik
        """
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"TRX-{today}-"
        
        row = self._fetch_one(
            "SELECT no_transaksi FROM transactions WHERE no_transaksi LIKE ? ORDER BY id DESC LIMIT 1",
            (f"{prefix}%",)
        )
        
        if row:
            last_num = int(row["no_transaksi"].split("-")[-1])
            next_num = last_num + 1
        else:
            next_num = 1
        
        return f"{prefix}{next_num:04d}"

    def create_transaction(self, kasir_id, items, bayar):
        """
        Buat transaksi baru secara atomik.
        
        Proses:
        1. Insert header transaksi
        2. Insert setiap item transaksi
        3. Kurangi stok produk
        4. Catat stock_log (jenis: keluar)
        
        Args:
            kasir_id: ID kasir yang memproses
            items: list of dict [{produk_id, nama, qty, harga_satuan, subtotal, stok_tersedia}, ...]
            bayar: Jumlah uang yang dibayarkan
            
        Returns:
            dict: Informasi transaksi yang berhasil dibuat
            
        Raises:
            ValueError: Jika validasi gagal
            Exception: Jika operasi database gagal
        """
        # Hitung total
        total = sum(item["subtotal"] for item in items)
        kembalian = float(bayar) - total
        
        # Validasi
        self.validate({"items": items, "bayar": bayar, "total": total})
        
        # Validasi stok cukup
        for item in items:
            if int(item["qty"]) > int(item["stok_tersedia"]):
                raise ValueError(
                    f"Stok {item['nama']} tidak cukup! "
                    f"Tersedia: {item['stok_tersedia']}, diminta: {item['qty']}"
                )
        
        # Eksekusi atomik
        import sqlite3
        cursor = self._conn.cursor()
        try:
            no_trx = self._generate_no_transaksi()
            tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 1. Insert header transaksi
            cursor.execute(
                """INSERT INTO transactions 
                   (no_transaksi, tanggal, kasir_id, total_belanja, bayar, kembalian)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (no_trx, tanggal, kasir_id, total, float(bayar), kembalian)
            )
            transaksi_id = cursor.lastrowid
            
            for item in items:
                # 2. Insert item transaksi
                cursor.execute(
                    """INSERT INTO transaction_items 
                       (transaksi_id, produk_id, qty, harga_satuan, subtotal)
                       VALUES (?, ?, ?, ?, ?)""",
                    (transaksi_id, item["produk_id"], item["qty"],
                     item["harga_satuan"], item["subtotal"])
                )
                
                # 3. Kurangi stok produk
                new_stock = int(item["stok_tersedia"]) - int(item["qty"])
                cursor.execute(
                    "UPDATE products SET stok = ? WHERE id = ?",
                    (new_stock, item["produk_id"])
                )
                
                # 4. Catat stock_log
                cursor.execute(
                    """INSERT INTO stock_log 
                       (produk_id, jenis, jumlah, keterangan, tanggal)
                       VALUES (?, 'keluar', ?, ?, ?)""",
                    (item["produk_id"], item["qty"],
                     f"Penjualan {no_trx}", tanggal)
                )
            
            self._conn.commit()
            
            return {
                "no_transaksi": no_trx,
                "tanggal": tanggal,
                "total": total,
                "bayar": float(bayar),
                "kembalian": kembalian,
                "jumlah_item": len(items)
            }
            
        except sqlite3.Error as e:
            self._conn.rollback()
            raise Exception(f"Gagal menyimpan transaksi: {e}")
        finally:
            cursor.close()

    def get_all(self):
        """Ambil semua transaksi dengan nama kasir."""
        return self._fetch_all("""
            SELECT t.*, u.username as kasir_name
            FROM transactions t
            LEFT JOIN users u ON t.kasir_id = u.id
            ORDER BY t.id DESC
        """)

    def get_by_date_range(self, date_from, date_to):
        """
        Ambil transaksi berdasarkan range tanggal.
        
        Args:
            date_from: Tanggal awal (format YYYY-MM-DD)
            date_to: Tanggal akhir (format YYYY-MM-DD)
        """
        return self._fetch_all("""
            SELECT t.*, u.username as kasir_name
            FROM transactions t
            LEFT JOIN users u ON t.kasir_id = u.id
            WHERE DATE(t.tanggal) BETWEEN ? AND ?
            ORDER BY t.tanggal DESC
        """, (date_from, date_to))

    def get_today_summary(self):
        """Ambil ringkasan transaksi hari ini."""
        today = datetime.now().strftime("%Y-%m-%d")
        row = self._fetch_one("""
            SELECT COUNT(*) as total_trx, COALESCE(SUM(total_belanja), 0) as total_omzet
            FROM transactions
            WHERE DATE(tanggal) = ?
        """, (today,))
        return {
            "total_trx": row["total_trx"] if row else 0,
            "total_omzet": row["total_omzet"] if row else 0
        }

    def get_items_by_transaction(self, transaksi_id):
        """Ambil detail item dari satu transaksi."""
        return self._fetch_all("""
            SELECT ti.*, p.kode_barang, p.nama_barang
            FROM transaction_items ti
            LEFT JOIN products p ON ti.produk_id = p.id
            WHERE ti.transaksi_id = ?
        """, (transaksi_id,))
