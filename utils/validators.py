"""
validators.py — Fungsi validasi input reusable (DRY).

Digunakan oleh view/controller untuk memvalidasi input pengguna
sebelum data dikirim ke model layer.
"""


def validate_not_empty(value, field_name):
    """
    Validasi bahwa nilai tidak kosong.
    
    Args:
        value: Nilai yang akan divalidasi
        field_name: Nama field untuk pesan error
        
    Returns:
        str: Nilai yang sudah di-strip
        
    Raises:
        ValueError: Jika nilai kosong
    """
    if not str(value).strip():
        raise ValueError(f"{field_name} tidak boleh kosong")
    return str(value).strip()


def validate_positive_number(value, field_name):
    """
    Validasi dan parse angka positif (float >= 0).
    
    Args:
        value: Nilai yang akan divalidasi
        field_name: Nama field untuk pesan error
        
    Returns:
        float: Nilai yang sudah diparse
        
    Raises:
        ValueError: Jika bukan angka atau negatif
    """
    try:
        num = float(value)
    except (ValueError, TypeError):
        raise ValueError(f"{field_name} harus berupa angka")
    if num < 0:
        raise ValueError(f"{field_name} tidak boleh negatif")
    return num


def validate_positive_integer(value, field_name):
    """
    Validasi dan parse integer positif (>= 0).
    
    Args:
        value: Nilai yang akan divalidasi
        field_name: Nama field untuk pesan error
        
    Returns:
        int: Nilai yang sudah diparse
        
    Raises:
        ValueError: Jika bukan integer atau negatif
    """
    try:
        num = int(value)
    except (ValueError, TypeError):
        raise ValueError(f"{field_name} harus berupa bilangan bulat")
    if num < 0:
        raise ValueError(f"{field_name} tidak boleh negatif")
    return num


def validate_date_format(value):
    """
    Validasi format tanggal YYYY-MM-DD.
    
    Args:
        value: String tanggal
        
    Returns:
        str: Tanggal yang sudah divalidasi
        
    Raises:
        ValueError: Jika format tidak valid
    """
    from datetime import datetime
    try:
        datetime.strptime(str(value).strip(), "%Y-%m-%d")
        return str(value).strip()
    except ValueError:
        raise ValueError("Format tanggal harus YYYY-MM-DD (contoh: 2025-12-31)")
