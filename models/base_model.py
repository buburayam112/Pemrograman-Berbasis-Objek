"""
base_model.py — Kelas abstrak BaseModel untuk CRUD generik.

Menerapkan prinsip DRY: semua query SQL berulang (SELECT, INSERT, UPDATE, DELETE)
melewati method generik di sini, tidak ditulis ulang di setiap model turunan.

Menerapkan prinsip Encapsulation: koneksi database (_conn) bersifat private,
hanya bisa diakses lewat method publik.
"""

import sqlite3
from database import Database


class BaseModel:
    """
    Kelas dasar untuk semua model.
    
    Menyediakan method CRUD generik yang di-inherit oleh model turunan.
    Setiap model turunan wajib meng-override method validate() sesuai
    aturan bisnis masing-masing entitas (Polymorphism).
    
    Attributes:
        _conn: Koneksi SQLite (private/protected)
        _table_name: Nama tabel database yang dikelola model ini
    """

    def __init__(self, table_name):
        """
        Inisialisasi BaseModel.
        
        Args:
            table_name: Nama tabel di database yang dikelola model ini
        """
        self._conn = Database().get_connection()
        self._table_name = table_name

    def _execute(self, query, params=None):
        """
        Eksekusi query INSERT/UPDATE/DELETE dengan exception handling.
        
        Menerapkan pola try-except-finally dengan rollback saat error.
        
        Args:
            query: String SQL query
            params: Tuple parameter untuk query (opsional)
            
        Returns:
            int: lastrowid dari operasi INSERT, atau rowcount untuk UPDATE/DELETE
            
        Raises:
            Exception: Jika terjadi error database
        """
        cursor = self._conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self._conn.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
        except sqlite3.Error as e:
            self._conn.rollback()
            raise Exception(f"Gagal memproses data: {e}")
        finally:
            cursor.close()

    def _fetch_all(self, query, params=None):
        """
        Ambil semua baris hasil query SELECT.
        
        Args:
            query: String SQL SELECT query
            params: Tuple parameter untuk query (opsional)
            
        Returns:
            list[sqlite3.Row]: Daftar baris hasil query
            
        Raises:
            Exception: Jika terjadi error database
        """
        cursor = self._conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except sqlite3.Error as e:
            raise Exception(f"Gagal mengambil data: {e}")
        finally:
            cursor.close()

    def _fetch_one(self, query, params=None):
        """
        Ambil satu baris hasil query SELECT.
        
        Args:
            query: String SQL SELECT query
            params: Tuple parameter untuk query (opsional)
            
        Returns:
            sqlite3.Row or None: Satu baris hasil query, atau None jika tidak ditemukan
            
        Raises:
            Exception: Jika terjadi error database
        """
        cursor = self._conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
        except sqlite3.Error as e:
            raise Exception(f"Gagal mengambil data: {e}")
        finally:
            cursor.close()

    def get_all(self):
        """Ambil semua data dari tabel."""
        return self._fetch_all(f"SELECT * FROM {self._table_name}")

    def get_by_id(self, record_id):
        """Ambil satu data berdasarkan ID."""
        return self._fetch_one(
            f"SELECT * FROM {self._table_name} WHERE id = ?", (record_id,)
        )

    def delete(self, record_id):
        """
        Hapus data berdasarkan ID.
        
        Args:
            record_id: ID record yang akan dihapus
            
        Returns:
            int: Jumlah baris yang terhapus
        """
        return self._execute(
            f"DELETE FROM {self._table_name} WHERE id = ?", (record_id,)
        )

    def count(self):
        """Hitung jumlah total record di tabel."""
        result = self._fetch_one(f"SELECT COUNT(*) as total FROM {self._table_name}")
        return result["total"] if result else 0

    def validate(self, data):
        """
        Validasi data sebelum disimpan — WAJIB di-override oleh subclass.
        
        Menerapkan prinsip Polymorphism: setiap model memiliki aturan
        validasi bisnis yang berbeda.
        
        Args:
            data: dict berisi data yang akan divalidasi
            
        Raises:
            ValueError: Jika data tidak valid
        """
        raise NotImplementedError("Subclass harus mengimplementasikan validate()")
