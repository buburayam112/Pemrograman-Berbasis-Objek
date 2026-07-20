"""
base_view.py — Kerangka umum untuk semua frame aplikasi POS.

Menerapkan prinsip DRY: konstanta warna, font, dan method helper
didefinisikan sekali di sini, digunakan ulang oleh semua view turunan.

Menerapkan prinsip Inheritance: semua frame mewarisi BaseFrame.
"""

import tkinter as tk
from tkinter import ttk


# ── Konstanta Warna (DRY — didefinisikan sekali, dipakai di mana-mana) ──
COLORS = {
    "primary":      "#2C3E50",    # Biru tua gelap
    "secondary":    "#34495E",    # Abu-abu biru
    "accent":       "#3498DB",    # Biru cerah
    "accent_hover": "#2980B9",    # Biru hover
    "success":      "#27AE60",    # Hijau
    "warning":      "#F39C12",    # Kuning/oranye
    "danger":       "#E74C3C",    # Merah
    "bg_main":      "#ECF0F1",    # Abu-abu terang (background utama)
    "bg_card":      "#FFFFFF",    # Putih (card/panel)
    "bg_header":    "#2C3E50",    # Header background
    "text_dark":    "#2C3E50",    # Teks gelap
    "text_light":   "#FFFFFF",    # Teks terang
    "text_muted":   "#7F8C8D",    # Teks abu-abu
    "border":       "#BDC3C7",    # Border abu-abu
    "row_alt":      "#F8F9FA",    # Baris tabel alternatif
    "low_stock":    "#FADBD8",    # Background stok rendah (merah muda)
}

# ── Konstanta Font (DRY) ──
FONTS = {
    "title":        ("Segoe UI", 18, "bold"),
    "subtitle":     ("Segoe UI", 14, "bold"),
    "heading":      ("Segoe UI", 12, "bold"),
    "body":         ("Segoe UI", 10),
    "body_bold":    ("Segoe UI", 10, "bold"),
    "small":        ("Segoe UI", 9),
    "mono":         ("Consolas", 10),
    "button":       ("Segoe UI", 10, "bold"),
    "treeview":     ("Segoe UI", 10),
    "treeview_head":("Segoe UI", 10, "bold"),
}


class BaseFrame(tk.Frame):
    """
    Kelas dasar untuk semua frame di aplikasi POS.
    
    Menyediakan:
    - Kerangka layout standar (header + content area)
    - Method helper untuk membuat widget umum
    - Akses ke konstanta warna & font
    
    Semua view turunan mewarisi kelas ini (Inheritance).
    """

    def __init__(self, parent, controller, title=""):
        """
        Inisialisasi BaseFrame.
        
        Args:
            parent: Widget parent (container)
            controller: Referensi ke POSApp (main.py) untuk navigasi & akses model
            title: Judul halaman yang ditampilkan di header
        """
        super().__init__(parent, bg=COLORS["bg_main"])
        self._controller = controller
        self._title = title
        
        # Setup grid agar frame mengisi seluruh container
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Buat header
        if title:
            self._create_header(title)

    def _create_header(self, title):
        """
        Buat header bar di bagian atas frame.
        
        Args:
            title: Teks judul yang ditampilkan
        """
        header = tk.Frame(self, bg=COLORS["bg_header"], height=60)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)

        lbl = tk.Label(
            header, text=title,
            font=FONTS["title"],
            bg=COLORS["bg_header"],
            fg=COLORS["text_light"],
            anchor="w", padx=20
        )
        lbl.grid(row=0, column=0, sticky="w", pady=10)

    def _create_content_frame(self, padding=20):
        """
        Buat frame konten utama di bawah header.
        
        Returns:
            tk.Frame: Frame konten yang bisa diisi widget
        """
        content = tk.Frame(self, bg=COLORS["bg_main"], padx=padding, pady=padding)
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)
        return content

    def _create_card(self, parent, title=None, row=0, column=0, 
                     sticky="nsew", padx=5, pady=5, colspan=1, rowspan=1):
        """
        Buat panel card dengan border dan shadow efek.
        
        Args:
            parent: Widget parent
            title: Judul card (opsional)
            
        Returns:
            tk.Frame: Frame card yang bisa diisi widget
        """
        card = tk.Frame(
            parent, bg=COLORS["bg_card"],
            relief="solid", bd=1,
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )
        card.grid(row=row, column=column, sticky=sticky,
                  padx=padx, pady=pady, columnspan=colspan, rowspan=rowspan)

        if title:
            title_lbl = tk.Label(
                card, text=title,
                font=FONTS["subtitle"],
                bg=COLORS["bg_card"],
                fg=COLORS["text_dark"],
                anchor="w"
            )
            title_lbl.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5),
                           columnspan=10)
            
            sep = ttk.Separator(card, orient="horizontal")
            sep.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10),
                     columnspan=10)

        return card

    def _create_label_entry(self, parent, label_text, row, column=0,
                            entry_width=25, state="normal"):
        """
        Buat pasangan Label + Entry field.
        
        Returns:
            tuple: (Label widget, Entry widget)
        """
        lbl = tk.Label(
            parent, text=label_text,
            font=FONTS["body_bold"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_dark"],
            anchor="w"
        )
        lbl.grid(row=row, column=column, sticky="w", padx=(15, 5), pady=3)

        entry = tk.Entry(
            parent, font=FONTS["body"],
            width=entry_width, state=state,
            relief="solid", bd=1
        )
        entry.grid(row=row, column=column + 1, sticky="ew", padx=(5, 15), pady=3)

        return lbl, entry

    def _create_button(self, parent, text, command, style="primary",
                       row=0, column=0, padx=5, pady=5, sticky="ew", width=None):
        """
        Buat tombol dengan style konsisten.
        
        Args:
            style: 'primary', 'success', 'danger', 'warning', atau 'secondary'
        """
        color_map = {
            "primary":   (COLORS["accent"], COLORS["accent_hover"]),
            "success":   (COLORS["success"], "#229954"),
            "danger":    (COLORS["danger"], "#C0392B"),
            "warning":   (COLORS["warning"], "#E67E22"),
            "secondary": (COLORS["secondary"], COLORS["primary"]),
        }
        bg, active_bg = color_map.get(style, color_map["primary"])

        btn = tk.Button(
            parent, text=text, command=command,
            font=FONTS["button"],
            bg=bg, fg=COLORS["text_light"],
            activebackground=active_bg,
            activeforeground=COLORS["text_light"],
            relief="flat", cursor="hand2",
            padx=15, pady=6
        )
        if width:
            btn.config(width=width)
        btn.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)

        # Hover effects
        btn.bind("<Enter>", lambda e, b=btn, c=active_bg: b.config(bg=c))
        btn.bind("<Leave>", lambda e, b=btn, c=bg: b.config(bg=c))

        return btn

    def _create_treeview(self, parent, columns, column_widths=None, 
                         height=15, show_scrollbar=True):
        """
        Buat ttk.Treeview dengan scrollbar dan styling.
        
        Args:
            parent: Widget parent
            columns: list of tuples [(col_id, heading_text), ...]
            column_widths: dict {col_id: width} (opsional)
            height: Jumlah baris visible
            show_scrollbar: Tampilkan scrollbar vertikal
            
        Returns:
            ttk.Treeview: Treeview yang sudah dikonfigurasi
        """
        # Styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        font=FONTS["treeview"],
                        rowheight=28,
                        background=COLORS["bg_card"],
                        fieldbackground=COLORS["bg_card"],
                        foreground=COLORS["text_dark"])
        style.configure("Custom.Treeview.Heading",
                        font=FONTS["treeview_head"],
                        background=COLORS["primary"],
                        foreground=COLORS["text_light"],
                        relief="flat")
        style.map("Custom.Treeview.Heading",
                  background=[("active", COLORS["accent"])])
        style.map("Custom.Treeview",
                  background=[("selected", COLORS["accent"])],
                  foreground=[("selected", COLORS["text_light"])])

        # Container
        tree_frame = tk.Frame(parent, bg=COLORS["bg_card"])
        tree_frame.grid(sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        col_ids = [c[0] for c in columns]
        tree = ttk.Treeview(
            tree_frame, columns=col_ids,
            show="headings", height=height,
            style="Custom.Treeview"
        )

        for col_id, heading in columns:
            tree.heading(col_id, text=heading, anchor="center")
            width = (column_widths or {}).get(col_id, 120)
            tree.column(col_id, width=width, anchor="center", minwidth=50)

        tree.grid(row=0, column=0, sticky="nsew")

        # Tag untuk baris stok rendah
        tree.tag_configure("low_stock", background=COLORS["low_stock"],
                           foreground=COLORS["danger"])
        tree.tag_configure("alt_row", background=COLORS["row_alt"])

        if show_scrollbar:
            scrollbar = ttk.Scrollbar(tree_frame, orient="vertical",
                                      command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.grid(row=0, column=1, sticky="ns")

        return tree

    def _format_currency(self, value):
        """Format angka ke format rupiah: Rp 1.234.567."""
        try:
            return f"Rp {int(float(value)):,.0f}".replace(",", ".")
        except (ValueError, TypeError):
            return "Rp 0"

    def refresh_data(self):
        """
        Method placeholder untuk refresh data di frame.
        Di-override oleh subclass sesuai kebutuhan.
        """
        pass
