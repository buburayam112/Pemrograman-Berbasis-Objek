"""
login_view.py — Halaman login aplikasi POS.

Menampilkan form login centered dengan username & password.
Callback autentikasi diberikan oleh controller (main.py).
"""

import tkinter as tk
from views.base_view import BaseFrame, COLORS, FONTS


class LoginFrame(BaseFrame):
    """
    Frame halaman login.
    
    Menampilkan form login di tengah layar dengan branding aplikasi.
    Setelah login berhasil, controller akan menampilkan frame sesuai role.
    """

    def __init__(self, parent, controller):
        # Tidak pakai header default, login punya desain sendiri
        super().__init__(parent, controller, title="")
        self._build_ui()

    def _build_ui(self):
        """Bangun seluruh komponen UI login."""
        # Container utama — centered
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        center = tk.Frame(self, bg=COLORS["bg_main"])
        center.grid(row=0, column=0)

        # ── Logo / Branding Area ──
        brand_frame = tk.Frame(center, bg=COLORS["primary"], padx=40, pady=20)
        brand_frame.grid(row=0, column=0, sticky="ew")

        tk.Label(
            brand_frame, text="🏪",
            font=("Segoe UI", 40),
            bg=COLORS["primary"], fg=COLORS["text_light"]
        ).grid(row=0, column=0, pady=(10, 0))

        tk.Label(
            brand_frame, text="POS KASIR & STOK",
            font=("Segoe UI", 20, "bold"),
            bg=COLORS["primary"], fg=COLORS["text_light"]
        ).grid(row=1, column=0, pady=(0, 2))

        tk.Label(
            brand_frame, text="Sistem Manajemen Toko & Gudang",
            font=FONTS["body"],
            bg=COLORS["primary"], fg="#BDC3C7"
        ).grid(row=2, column=0, pady=(0, 10))

        # ── Form Login ──
        form_frame = tk.Frame(center, bg=COLORS["bg_card"], padx=40, pady=30,
                              relief="solid", bd=1,
                              highlightbackground=COLORS["border"],
                              highlightthickness=1)
        form_frame.grid(row=1, column=0, sticky="ew")

        tk.Label(
            form_frame, text="Silakan Login",
            font=FONTS["subtitle"],
            bg=COLORS["bg_card"], fg=COLORS["text_dark"]
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Username
        tk.Label(
            form_frame, text="👤  Username",
            font=FONTS["body_bold"],
            bg=COLORS["bg_card"], fg=COLORS["text_dark"], anchor="w"
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 3))

        self._entry_username = tk.Entry(
            form_frame, font=FONTS["body"], width=30,
            relief="solid", bd=1
        )
        self._entry_username.grid(row=2, column=0, columnspan=2, 
                                   sticky="ew", pady=(0, 15), ipady=5)

        # Password
        tk.Label(
            form_frame, text="🔒  Password",
            font=FONTS["body_bold"],
            bg=COLORS["bg_card"], fg=COLORS["text_dark"], anchor="w"
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 3))

        self._entry_password = tk.Entry(
            form_frame, font=FONTS["body"], width=30,
            show="●", relief="solid", bd=1
        )
        self._entry_password.grid(row=4, column=0, columnspan=2,
                                   sticky="ew", pady=(0, 20), ipady=5)

        # Tombol Login
        btn_login = tk.Button(
            form_frame, text="LOGIN",
            font=FONTS["button"],
            bg=COLORS["accent"], fg=COLORS["text_light"],
            activebackground=COLORS["accent_hover"],
            activeforeground=COLORS["text_light"],
            relief="flat", cursor="hand2",
            padx=20, pady=8,
            command=self._on_login
        )
        btn_login.grid(row=5, column=0, columnspan=2, sticky="ew", ipady=3)
        btn_login.bind("<Enter>", lambda e: btn_login.config(bg=COLORS["accent_hover"]))
        btn_login.bind("<Leave>", lambda e: btn_login.config(bg=COLORS["accent"]))

        # Pesan error
        self._lbl_error = tk.Label(
            form_frame, text="",
            font=FONTS["small"],
            bg=COLORS["bg_card"], fg=COLORS["danger"]
        )
        self._lbl_error.grid(row=6, column=0, columnspan=2, pady=(10, 0))

        # ── Footer ──
        footer = tk.Frame(center, bg=COLORS["bg_main"])
        footer.grid(row=2, column=0, pady=15)

        tk.Label(
            footer, text="Default: admin/admin123 atau kasir/kasir123",
            font=FONTS["small"],
            bg=COLORS["bg_main"], fg=COLORS["text_muted"]
        ).grid(row=0, column=0)

        # Bind Enter key
        self._entry_username.bind("<Return>", lambda e: self._entry_password.focus())
        self._entry_password.bind("<Return>", lambda e: self._on_login())

    def _on_login(self):
        """Handler tombol Login — panggil controller untuk autentikasi."""
        username = self._entry_username.get().strip()
        password = self._entry_password.get().strip()

        if not username or not password:
            self._lbl_error.config(text="Username dan password harus diisi!")
            return

        self._lbl_error.config(text="")
        # Panggil controller
        self._controller.handle_login(username, password)

    def show_error(self, message):
        """Tampilkan pesan error di form login."""
        self._lbl_error.config(text=message)

    def clear_form(self):
        """Bersihkan form login."""
        self._entry_username.delete(0, tk.END)
        self._entry_password.delete(0, tk.END)
        self._lbl_error.config(text="")
        self._entry_username.focus()
