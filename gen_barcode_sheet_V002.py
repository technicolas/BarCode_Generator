#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dépendances :
    pip install pillow reportlab python-barcode
"""

import os
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image

# ------------------------------------------------------------
# CHARGEMENT DU FICHIER DE CONFIGURATION
# ------------------------------------------------------------

CONFIG_FILE = "config.conf"

DEFAULT_PAGES = 500
DEFAULT_START = 100
DEFAULT_RATIO = 0.50

def load_config():
    """Charge les valeurs par défaut depuis config.conf."""
    pages = DEFAULT_PAGES
    start = DEFAULT_START
    ratio = DEFAULT_RATIO

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    if key == "pages":
                        pages = int(value)
                    elif key == "start":
                        start = int(value)
                    elif key == "barcode_width_ratio":
                        ratio = float(value)

    return pages, start, ratio


# ------------------------------------------------------------
# FONCTIONS
# ------------------------------------------------------------

def generate_barcode_image(data: str, filename: str):
    """Génère un code-barres Code128 en PNG."""
    barcode = Code128(data, writer=ImageWriter())
    barcode.save(filename, {
        "module_height": 25,
        "module_width": 0.30,
        "quiet_zone": 2.0,
        "font_size": 0,
        "text_distance": 1,
    })
    return filename + ".png"


def draw_delimiter(c: canvas.Canvas, y: float):
    """Dessine le symbole délimiteur composé de 4 lignes épaisses."""
    line_width = 4
    spacing = 6

    c.setLineWidth(line_width)

    for i in range(4):
        c.line(20 * mm, y + i * spacing, A4[0] - 20 * mm, y + i * spacing)


def add_centered_barcode(c: canvas.Canvas, img_path: str, text: str, ratio: float):
    """Ajoute un code-barres centré verticalement et horizontalement."""

    img = Image.open(img_path)
    w, h = img.size

    final_width = A4[0] * ratio
    scale_factor = final_width / (w * 0.75)

    w_pt = w * 0.75 * scale_factor
    h_pt = h * 0.75 * scale_factor

    x = (A4[0] - w_pt) / 2
    y = (A4[1] - h_pt) / 2

    c.drawImage(img_path, x, y, width=w_pt, height=h_pt)

    c.setFont("Helvetica", 14)
    c.drawCentredString(A4[0] / 2, y - 15, text)


# ------------------------------------------------------------
# PROGRAMME PRINCIPAL
# ------------------------------------------------------------

def main():
    print("=== Générateur de pages A4 avec code-barres ===")

    # Charger config.conf
    conf_pages, conf_start, conf_ratio = load_config()

    # Date du jour inversée
    today = datetime.date.today()
    default_date_inv = today.strftime("%Y%m%d")

    # Demandes utilisateur avec valeurs par défaut
    date_inv = input(f"Introduire la date inversée [{default_date_inv}] : ").strip()
    if date_inv == "":
        date_inv = default_date_inv

    pages_input = input(f"Nombre de pages à générer [{conf_pages}] : ").strip()
    pages = int(pages_input) if pages_input else conf_pages

    start_input = input(f"Premier numéro de la série [{conf_start:04d}] : ").strip()
    start_number = int(start_input) if start_input else conf_start

    # Nom du fichier PDF
    first_num = f"{start_number:04d}"
    last_num = f"{start_number + pages - 1:04d}"
    pdf_name = f"CodeBar_{date_inv}_[{first_num}-{last_num}].pdf"

    pdf = canvas.Canvas(pdf_name, pagesize=A4)

    for i in range(pages):
        num = f"{start_number + i:04d}"
        text = f"{date_inv} / {num}"

        img_path = generate_barcode_image(text, f"barcode_{num}")

        # Délimiteur haut
        draw_delimiter(pdf, A4[1] - 20 * mm)

        # Code-barres centré
        add_centered_barcode(pdf, img_path, text, conf_ratio)

        # Délimiteur bas
        draw_delimiter(pdf, 20 * mm)

        pdf.showPage()

        os.remove(img_path)

    pdf.save()
    print(f"PDF généré : {pdf_name}")


if __name__ == "__main__":
    main()
