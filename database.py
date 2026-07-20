"""
database.py — Singleton koneksi SQLite untuk aplikasi POS.

Menggunakan pola Singleton agar hanya ada satu koneksi database
di seluruh aplikasi, mencegah konflik akses dan resource leak.
"""

import sqlite3
import os


class Database:
    """
    Singleton class untuk mengelola koneksi SQLite.
    
    Hanya membuat satu instance koneksi selama aplikasi berjalan.
    Menyediakan method untuk inisialisasi tabel dan seed data default.
    """

    _instance = None
    _conn = None

    def __new__(cls):
        """Implementasi Singleton — hanya satu instance Database."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Buka koneksi ke file database lokal."""
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pos_database.db")
        self._conn = sqlite3.connect(db_path)
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.row_factory = sqlite3.Row
        self.initialize_tables()
        self.seed_default_data()

    def get_connection(self):
        """Mengembalikan koneksi SQLite yang aktif."""
        return self._conn

    def initialize_tables(self):
        """Membuat semua tabel yang dibutuhkan jika belum ada."""
        cursor = self._conn.cursor()
        try:
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT CHECK(role IN ('admin','kasir')) NOT NULL
                );

                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama_kategori TEXT UNIQUE NOT NULL
                );

                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kode_barang TEXT UNIQUE NOT NULL,
                    nama_barang TEXT NOT NULL,
                    kategori_id INTEGER,
                    harga_beli REAL NOT NULL,
                    harga_jual REAL NOT NULL,
                    stok INTEGER NOT NULL DEFAULT 0,
                    stok_minimum INTEGER DEFAULT 5,
                    FOREIGN KEY(kategori_id) REFERENCES categories(id)
                );

                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    no_transaksi TEXT UNIQUE NOT NULL,
                    tanggal TEXT NOT NULL,
                    kasir_id INTEGER,
                    total_belanja REAL NOT NULL,
                    bayar REAL NOT NULL,
                    kembalian REAL NOT NULL,
                    FOREIGN KEY(kasir_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS transaction_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaksi_id INTEGER,
                    produk_id INTEGER,
                    qty INTEGER NOT NULL,
                    harga_satuan REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY(transaksi_id) REFERENCES transactions(id),
                    FOREIGN KEY(produk_id) REFERENCES products(id)
                );

                CREATE TABLE IF NOT EXISTS stock_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    produk_id INTEGER,
                    jenis TEXT CHECK(jenis IN ('masuk','keluar')) NOT NULL,
                    jumlah INTEGER NOT NULL,
                    keterangan TEXT,
                    tanggal TEXT NOT NULL,
                    FOREIGN KEY(produk_id) REFERENCES products(id)
                );
            """)
            self._conn.commit()
        except sqlite3.Error as e:
            self._conn.rollback()
            raise Exception(f"Gagal membuat tabel: {e}")
        finally:
            cursor.close()

    def seed_default_data(self):
        """
        Insert data default jika tabel masih kosong.
        
        Menyediakan:
        - 2 user (admin & kasir)
        - 5 kategori
        - 12 produk sample dengan stok beragam
        """
        cursor = self._conn.cursor()
        try:
            # Cek apakah sudah ada data user
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] > 0:
                return  # Data sudah ada, skip seeding

            # --- Users ---
            users = [
                ("admin", "admin123", "admin"),
                ("kasir", "kasir123", "kasir"),
            ]
            cursor.executemany(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                users
            )

            # --- Kategori ---
            categories = [
                ("Makanan",),
                ("Minuman",),
                ("Snack",),
                ("Alat Tulis",),
                ("Elektronik",),
            ]
            cursor.executemany(
                "INSERT INTO categories (nama_kategori) VALUES (?)",
                categories
            )

            # --- Produk ---
            products = [
                ("MKN001", "Nasi Goreng Instan", 1, 5000, 8000, 25, 5),
                ("MKN002", "Mie Instan Goreng", 1, 2500, 4000, 50, 10),
                ("MKN003", "Sarden Kaleng", 1, 12000, 16000, 3, 5),    # stok di bawah minimum
                ("MNM001", "Air Mineral 600ml", 2, 2000, 3500, 100, 20),
                ("MNM002", "Teh Kotak 250ml", 2, 3000, 5000, 30, 10),
                ("MNM003", "Kopi Sachet", 2, 1500, 3000, 4, 10),       # stok di bawah minimum
                ("SNK001", "Keripik Kentang", 3, 5000, 8500, 20, 5),
                ("SNK002", "Coklat Batangan", 3, 8000, 12000, 15, 5),
                ("ATK001", "Pulpen Hitam", 4, 1500, 3000, 60, 10),
                ("ATK002", "Buku Tulis A5", 4, 4000, 6500, 40, 10),
                ("ELK001", "Baterai AA (2pcs)", 5, 8000, 12000, 2, 5), # stok di bawah minimum
                ("ELK002", "Kabel USB Type-C", 5, 15000, 25000, 10, 5),
            ]
            cursor.executemany(
                """INSERT INTO products 
                   (kode_barang, nama_barang, kategori_id, harga_beli, harga_jual, stok, stok_minimum) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                products
            )

            self._conn.commit()
        except sqlite3.Error as e:
            self._conn.rollback()
            raise Exception(f"Gagal seed data: {e}")
        finally:
            cursor.close()

    def close(self):
        """Tutup koneksi database."""
        if self._conn:
            self._conn.close()
            Database._instance = None
            Database._conn = None
