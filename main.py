"""
main.py — Controller utama aplikasi POS Kasir & Stok Gudang.

Bertanggung jawab untuk:
1. Membuat root window (tk.Tk)
2. Menginisialisasi database dan semua model
3. Menginisialisasi semua frame (view)
4. Mengatur navigasi antar frame (.tkraise())
5. Membuat Menu Bar dengan role-based visibility
6. Menjembatani interaksi antara view dan model

Arsitektur: MVC (Model-View-Controller)
- Model: models/*.py (logika data & database)
- View: views/*.py (komponen visual)
- Controller: main.py (ini — penghubung & routing)
"""

import tkinter as tk
from tkinter import messagebox

# Inisialisasi database (harus pertama kali)
from database import Database

# Import models
from models.user_model import UserModel
from models.product_model import ProductModel, CategoryModel
from models.transaction_model import TransactionModel
from models.stock_model import StockModel

# Import views
from views.login_view import LoginFrame
from views.dashboard_view import DashboardFrame
from views.kasir_view import KasirFrame
from views.product_view import ProductFrame
from views.stock_view import StockFrame
from views.report_view import ReportFrame
from views.base_view import COLORS


class POSApp(tk.Tk):
    """
    Controller utama aplikasi POS.
    
    Menggunakan pola Single Page Application desktop:
    semua frame ditumpuk di satu container, navigasi
    menggunakan .tkraise() tanpa membuka window baru.
    
    Attributes:
        _current_user: Objek User yang sedang login (Admin/Kasir)
        _frames: Dictionary semua frame {nama: frame_object}
        _db: Instance Database singleton
    """

    def __init__(self):
        super().__init__()

        # ── Konfigurasi Window ──
        self.title("POS Kasir & Stok Gudang")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg=COLORS["bg_main"])

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1100 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"+{x}+{y}")

        # ── Inisialisasi ──
        self._current_user = None
        self._db = Database()
        self._frames = {}

        # ── Setup Container ──
        container = tk.Frame(self, bg=COLORS["bg_main"])
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # ── Buat semua frame ──
        frame_classes = {
            "login": LoginFrame,
            "dashboard": DashboardFrame,
            "kasir": KasirFrame,
            "produk": ProductFrame,
            "stok": StockFrame,
            "laporan": ReportFrame,
        }

        for name, FrameClass in frame_classes.items():
            frame = FrameClass(container, self)
            self._frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # ── Setup Menu Bar (hidden saat login) ──
        self._menubar = tk.Menu(self, font=("Segoe UI", 10))
        self._setup_menubar()

        # ── Tampilkan halaman login ──
        self.show_frame("login")
        self.config(menu=tk.Menu(self))  # Menu kosong saat login

        # Handle close window
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ══════════════════════════════════════════
    # NAVIGATION (Controller)
    # ══════════════════════════════════════════

    def show_frame(self, frame_name):
        """
        Tampilkan frame yang diminta menggunakan .tkraise().
        
        Memanggil refresh_data() pada frame yang ditampilkan
        agar data selalu up-to-date.
        
        Args:
            frame_name: Key frame di dictionary _frames
        """
        if frame_name in self._frames:
            frame = self._frames[frame_name]
            frame.tkraise()
            frame.refresh_data()

    @property
    def current_user(self):
        """Getter untuk user yang sedang login (Encapsulation)."""
        return self._current_user

    # ══════════════════════════════════════════
    # MENU BAR
    # ══════════════════════════════════════════

    def _setup_menubar(self):
        """Buat struktur Menu Bar lengkap."""
        self._menubar.delete(0, "end")

        # Menu File
        file_menu = tk.Menu(self._menubar, tearoff=0, font=("Segoe UI", 10))
        file_menu.add_command(label="Logout", command=self.handle_logout)
        file_menu.add_separator()
        file_menu.add_command(label="Keluar", command=self._on_close)
        self._menubar.add_cascade(label="File", menu=file_menu)

        # Menu Navigasi (akan di-populate sesuai role)
        self._nav_menu = tk.Menu(self._menubar, tearoff=0, font=("Segoe UI", 10))
        self._menubar.add_cascade(label="Navigasi", menu=self._nav_menu)

        # Menu Bantuan
        help_menu = tk.Menu(self._menubar, tearoff=0, font=("Segoe UI", 10))
        help_menu.add_command(label="ℹ Tentang Aplikasi", command=self._show_about)
        self._menubar.add_cascade(label="Bantuan", menu=help_menu)

    def _update_nav_menu(self):
        """
        Update menu Navigasi berdasarkan role user (Polymorphism).
        
        Menu yang ditampilkan ditentukan oleh method get_menu_items()
        pada objek Admin atau Kasir — hasil berbeda sesuai role.
        """
        self._nav_menu.delete(0, "end")

        if self._current_user:
            menu_items = self._current_user.get_menu_items()
            icons = {
                "dashboard": "📊",
                "kasir": "🛒",
                "produk": "📦",
                "stok": "📋",
                "laporan": "📈",
            }
            for label, frame_name in menu_items:
                icon = icons.get(frame_name, "")
                self._nav_menu.add_command(
                    label=f"{icon}  {label}",
                    command=lambda fn=frame_name: self.show_frame(fn)
                )

    def _show_about(self):
        """Tampilkan dialog Tentang Aplikasi."""
        messagebox.showinfo(
            "Tentang Aplikasi",
            "POS Kasir & Stok Gudang v1.0\n\n"
            "Aplikasi Point of Sale untuk manajemen\n"
            "toko dan gudang kecil-menengah.\n\n"
            "Arsitektur: MVC (Model-View-Controller)\n"
            "Tech: Python 3 + Tkinter + SQLite\n\n"
            "Dikembangkan untuk Tugas Akhir\n"
            "Mata Kuliah Pemrograman Berorientasi Objek"
        )

    # ══════════════════════════════════════════
    # AUTHENTICATION (Controller Bridge)
    # ══════════════════════════════════════════

    def handle_login(self, username, password):
        """
        Proses autentikasi login.
        
        Memanggil UserModel.authenticate() dan menentukan
        menu berdasarkan role (Polymorphism: Admin vs Kasir).
        
        Args:
            username: Username yang diinput
            password: Password yang diinput
        """
        try:
            user_model = UserModel()
            user = user_model.authenticate(username, password)

            if user:
                self._current_user = user
                self.title(f"POS Kasir & Stok Gudang — {user}")

                # Tampilkan Menu Bar sesuai role
                self._setup_menubar()
                self._update_nav_menu()
                self.config(menu=self._menubar)

                # Navigasi ke Dashboard
                self.show_frame("dashboard")
                
                messagebox.showinfo(
                    "Login Berhasil",
                    f"Selamat datang, {user.username}!\n"
                    f"Role: {user.role.upper()}"
                )
            else:
                self._frames["login"].show_error(
                    "Username atau password salah!"
                )

        except Exception as e:
            messagebox.showerror("Error Login", str(e))

    def handle_logout(self):
        """Logout: kembali ke halaman login, reset state."""
        if messagebox.askyesno("Konfirmasi Logout", "Yakin ingin logout?"):
            self._current_user = None
            self.title("POS Kasir & Stok Gudang")
            self.config(menu=tk.Menu(self))  # Sembunyikan menu

            # Clear login form
            self._frames["login"].clear_form()
            self.show_frame("login")

    # ══════════════════════════════════════════
    # CLOSE & CLEANUP
    # ══════════════════════════════════════════

    def _on_close(self):
        """Handle penutupan aplikasi dengan konfirmasi."""
        if messagebox.askyesno("Keluar", "Yakin ingin keluar dari aplikasi?"):
            self._db.close()
            self.destroy()


# ══════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════

if __name__ == "__main__":
    app = POSApp()
    app.mainloop()
