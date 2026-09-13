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
# CONFIGURATION
# ------------------------------------------------------------

BARCODE_WIDTH_RATIO = 0.50   # Pourcentage de la largeur de la page (0.50 = 50%)
BARCODE_HEIGHT = 25 * mm     # Hauteur du code-barres
TEXT_SIZE = 14               # Taille du texte sous le code-barres
MARGIN = 20 * mm             # Marges de la page

# ------------------------------------------------------------
# FONCTIONS
# ------------------------------------------------------------

def generate_barcode_image(data: str, filename: str):
    """Génère un code-barres Code128 en PNG."""
    barcode = Code128(data, writer=ImageWriter())
    barcode.save(filename, {
        "module_height": BARCODE_HEIGHT / mm,
        "module_width": 0.30,   # largeur des barres (fixe, redimensionné ensuite)
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
        c.line(MARGIN, y + i * spacing, A4[0] - MARGIN, y + i * spacing)


def add_centered_barcode(c: canvas.Canvas, img_path: str, text: str):
    """Ajoute un code-barres centré verticalement et horizontalement."""

    img = Image.open(img_path)
    w, h = img.size

    # Largeur finale = % de la largeur de la page
    final_width = A4[0] * BARCODE_WIDTH_RATIO
    scale_factor = final_width / (w * 0.75)

    w_pt = w * 0.75 * scale_factor
    h_pt = h * 0.75 * scale_factor

    x = (A4[0] - w_pt) / 2
    y = (A4[1] - h_pt) / 2

    c.drawImage(img_path, x, y, width=w_pt, height=h_pt)

    c.setFont("Helvetica", TEXT_SIZE)
    c.drawCentredString(A4[0] / 2, y - 15, text)


# ------------------------------------------------------------
# PROGRAMME PRINCIPAL
# ------------------------------------------------------------

def main():
    print("=== Générateur de pages A4 avec code-barres ===")

    # Date du jour inversée
    today = datetime.date.today()
    default_date_inv = today.strftime("%Y%m%d")

    # Valeurs par défaut
    default_pages = 500
    default_start = 100

    # Demandes utilisateur avec valeurs par défaut
    date_inv = input(f"Introduire la date inversée [{default_date_inv}] : ").strip()
    if date_inv == "":
        date_inv = default_date_inv

    pages_input = input(f"Nombre de pages à générer [{default_pages}] : ").strip()
    pages = int(pages_input) if pages_input else default_pages

    start_input = input(f"Premier numéro de la série [{default_start:04d}] : ").strip()
    start_number = int(start_input) if start_input else default_start

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
        draw_delimiter(pdf, A4[1] - MARGIN)

        # Code-barres centré
        add_centered_barcode(pdf, img_path, text)

        # Délimiteur bas
        draw_delimiter(pdf, MARGIN)

        pdf.showPage()

        os.remove(img_path)

    pdf.save()
    print(f"PDF généré : {pdf_name}")


if __name__ == "__main__":
    main()
