"""
user_model.py — Model untuk autentikasi dan manajemen role pengguna.

Menerapkan prinsip Inheritance: User sebagai kelas induk, diturunkan
menjadi Admin dan Kasir dengan hak akses berbeda.

Menerapkan prinsip Polymorphism: method get_permissions() dan 
get_menu_items() mengembalikan hasil berbeda pada Admin vs Kasir.
"""

from models.base_model import BaseModel


class User:
    """
    Kelas induk untuk representasi pengguna.
    
    Attributes:
        _id: ID pengguna (private)
        _username: Username pengguna (private)
        _role: Role pengguna — 'admin' atau 'kasir' (private)
    """

    def __init__(self, user_id, username, role):
        self._id = user_id
        self._username = username
        self._role = role

    @property
    def id(self):
        """Getter untuk ID pengguna."""
        return self._id

    @property
    def username(self):
        """Getter untuk username."""
        return self._username

    @property
    def role(self):
        """Getter untuk role."""
        return self._role

    def get_permissions(self):
        """
        Mengembalikan daftar permission pengguna.
        Di-override oleh subclass (Polymorphism).
        """
        return []

    def get_menu_items(self):
        """
        Mengembalikan daftar menu yang bisa diakses.
        Di-override oleh subclass (Polymorphism).
        """
        return []

    def __str__(self):
        return f"{self._username} ({self._role})"


class Admin(User):
    """
    Kelas Admin — turunan dari User.
    Admin memiliki akses penuh ke semua fitur aplikasi.
    """

    def __init__(self, user_id, username):
        super().__init__(user_id, username, "admin")

    def get_permissions(self):
        """Admin bisa mengakses semua fitur."""
        return [
            "dashboard", "kasir", "produk", "stok", "laporan",
            "manajemen_user"
        ]

    def get_menu_items(self):
        """Admin melihat semua menu navigasi."""
        return [
            ("Dashboard", "dashboard"),
            ("Kasir", "kasir"),
            ("Manajemen Produk", "produk"),
            ("Manajemen Stok", "stok"),
            ("Laporan", "laporan"),
        ]


class Kasir(User):
    """
    Kelas Kasir — turunan dari User.
    Kasir hanya bisa mengakses halaman Kasir dan Dashboard.
    """

    def __init__(self, user_id, username):
        super().__init__(user_id, username, "kasir")

    def get_permissions(self):
        """Kasir hanya bisa akses dashboard dan kasir."""
        return ["dashboard", "kasir"]

    def get_menu_items(self):
        """Kasir hanya melihat menu Dashboard dan Kasir."""
        return [
            ("Dashboard", "dashboard"),
            ("Kasir", "kasir"),
        ]


class UserModel(BaseModel):
    """
    Model untuk operasi database tabel users.
    
    Menyediakan autentikasi login dan CRUD user.
    """

    def __init__(self):
        super().__init__("users")

    def validate(self, data):
        """
        Validasi data user.
        
        Args:
            data: dict dengan keys 'username', 'password', 'role'
            
        Raises:
            ValueError: Jika data tidak valid
        """
        if not data.get("username", "").strip():
            raise ValueError("Username tidak boleh kosong")
        if not data.get("password", "").strip():
            raise ValueError("Password tidak boleh kosong")
        if data.get("role") not in ("admin", "kasir"):
            raise ValueError("Role harus 'admin' atau 'kasir'")

    def authenticate(self, username, password):
        """
        Autentikasi pengguna berdasarkan username dan password.
        
        Args:
            username: Username yang diinput
            password: Password yang diinput
            
        Returns:
            User (Admin atau Kasir): Objek user sesuai role jika berhasil
            None: Jika autentikasi gagal
        """
        row = self._fetch_one(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        if row:
            if row["role"] == "admin":
                return Admin(row["id"], row["username"])
            else:
                return Kasir(row["id"], row["username"])
        return None

    def add(self, username, password, role):
        """Tambah user baru."""
        data = {"username": username, "password": password, "role": role}
        self.validate(data)
        return self._execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role)
        )
