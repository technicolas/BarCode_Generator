#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BUT DU PROGRAMMME ------------------------------------------
# Programme créé pour le service "Archives" dans le
# but de solutionner le problème de Sept 2026
# (solution de contournement à utiliser en cas de besoin)
# Moi - 12 septembre 2026
# ------------------------------------------------------------

import os
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image

# Bibliothèques à installer: ---------------------------------
# python.exe -m pip install --upgrade pip
# pip install pillow reportlab python-barcode
# pip install pyinstaller (pour transformer le .py en .exe)
# pyinstaller --noconsole --onefile --add-data "barcode.conf;." barcode_gui.py --icon=icone.ico (transforme le .py en .exe)
# ------------------------------------------------------------

# INFORMATIONS PROGRAMME -------------------------------------
# ------------------------------------------------------------
PROGRAM_VERSION = "1.00"
PROGRAM_CODE_NAME = "Le sauveur"
PROGRAM_DATE = "12/09/2026"
PROGRAM_AUTHOR = "Moi"
PROGRAM_AUTHOR_MAIL = "a@a.com"
INFO_GOAL = "The program was created for DVZOE's FIDES department to resolve the issue from September 2026 (a workaround to be used if necessary)."

CONFIG_FILE = "barcode.conf"
# STRUCTURE DU FICHIER "barcode.conf" ------------------------
# # Configuration par défaut
#   pages=1000
#   start=0001
#   barcode_width_ratio=0.50
# ------------------------------------------------------------

# CHARGEMENT CONFIGURATION -----------------------------------
# ------------------------------------------------------------

def load_config():
    pages = 100
    start = 1
    ratio = 0.50

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

# FONCTIONS CODE-BARRES --------------------------------------
# ------------------------------------------------------------
def generate_barcode_image(data: str, filename: str):
    barcode = Code128(data, writer=ImageWriter())
    barcode.save(filename, {
        "module_height": 25,
        "module_width": 0.30,
        "quiet_zone": 2.0,
        "font_size": 0,
        "text_distance": 1,})
    return filename + ".png"

def draw_delimiter(c: canvas.Canvas, y: float):
    line_width = 4
    spacing = 6
    margin = 20 * mm

    c.setLineWidth(line_width)
    for i in range(4):
        c.line(margin, y + i * spacing, A4[0] - margin, y + i * spacing)

def add_centered_barcode(c: canvas.Canvas, img_path: str, text: str, ratio: float):
    img = Image.open(img_path)
    w, h = img.size
    final_width = A4[0] * ratio
    scale_factor = final_width / (w * 0.75)
    w_pt = w * 0.75 * scale_factor
    h_pt = h * 0.75 * scale_factor
    x = (A4[0] - w_pt) / 2
    y = (A4[1] - h_pt) / 2

    c.drawImage(img_path, x, y, width=w_pt, height=h_pt)
    c.setFont("Helvetica", 20)
    c.drawCentredString(A4[0] / 2, y - 15, text)

# GÉNÉRATION PDF AVEC BARRE DE PROGRESSION -------------------
# ------------------------------------------------------------
def generate_pdf(date_inv, pages, start_number, ratio, progress_bar, status_label, root):
    first_num = f"{start_number:04d}"
    last_num = f"{start_number + pages - 1:04d}"
    pdf_name = f"CodeBar_{date_inv}_[{first_num}-{last_num}].pdf"
    pdf = canvas.Canvas(pdf_name, pagesize=A4)

    progress_bar["maximum"] = pages
    progress_bar["value"] = 0

    for i in range(pages):
        num = f"{start_number + i:04d}"
        text = f"{date_inv} / {num}"
        img_path = generate_barcode_image(text, f"barcode_{num}")

        draw_delimiter(pdf, A4[1] - 20 * mm)
        add_centered_barcode(pdf, img_path, text, ratio)
        draw_delimiter(pdf, 20 * mm)

        pdf.showPage()
        os.remove(img_path)

        progress_bar["value"] = i + 1
        root.update_idletasks()

    pdf.save()
    status_label.config(text=f"Generated PDF : {pdf_name}")

# FENÊTRE "À propos" -----------------------------------------
# ------------------------------------------------------------
def show_about():
    messagebox.showinfo(
        "About",
        f"A4 Barcode Generator\n\n"
        f"Version : {PROGRAM_VERSION}\n"
        f"Code name : {PROGRAM_CODE_NAME}\n"
        f"Date : {PROGRAM_DATE}\n\n"
        f"Author : {PROGRAM_AUTHOR}\n"
        f"Mail : {PROGRAM_AUTHOR_MAIL}")

def show_goal():
    messagebox.showinfo(
        "Goal",
        f"{INFO_GOAL}\n")

# INTERFACE TKINTER ------------------------------------------
# ------------------------------------------------------------
def main_gui():
    pages_default, start_default, ratio_default = load_config()
    today = datetime.date.today()
    default_date_inv = today.strftime("%Y%m%d")
    root = tk.Tk()
    root.title("FIDES - A4 barcode generator")
    # root.configure(bg="#1E3A8A")

    # Menu ---------------------------------------------------
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    menu_info = tk.Menu(menubar, tearoff=0)
    menu_info.add_command(label="Goal", command=show_goal)
    menu_info.add_command(label="About", command=show_about)
    menubar.add_cascade(label="Informations", menu=menu_info)
    frame = ttk.Frame(root, padding=20)
    #frame = tk.Frame(root, bg="#E0F1A1", padx=20, pady=20)
    frame.grid()

    # Champs -------------------------------------------------
    ttk.Label(frame, text="Reversed date :").grid(column=0, row=0, sticky="w")
    date_entry = ttk.Entry(frame)
    date_entry.insert(0, default_date_inv)
    date_entry.grid(column=1, row=0)

    ttk.Label(frame, text="Number of pages :").grid(column=0, row=1, sticky="w")
    pages_entry = ttk.Entry(frame)
    pages_entry.insert(0, str(pages_default))
    pages_entry.grid(column=1, row=1)

    ttk.Label(frame, text="Start number :").grid(column=0, row=2, sticky="w")
    start_entry = ttk.Entry(frame)
    start_entry.insert(0, f"{start_default:04d}")
    start_entry.grid(column=1, row=2)

    # Barre de progression -----------------------------------
    progress_bar = ttk.Progressbar(frame, length=250)
    progress_bar.grid(column=0, row=4, columnspan=2, pady=10)

    status_label = ttk.Label(frame, text="", foreground="green")
    status_label.grid(column=0, row=5, columnspan=2, pady=10)

    def on_generate():
        try:
            date_inv = date_entry.get().strip()
            pages = int(pages_entry.get().strip())
            start_number = int(start_entry.get().strip())
            ratio = ratio_default
            generate_pdf(date_inv, pages, start_number, ratio, progress_bar, status_label, root)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Bouton Générer PDF -------------------------------------
    generate_button = tk.Button(
        frame,
        text="Generate PDF",
        bg="#F5F900",
        fg="black",
        activebackground="#1E40AF",
        activeforeground="white",
        command=on_generate)
    generate_button.grid(column=0, row=3, columnspan=2, pady=10)

    # Bouton Sortir ------------------------------------------
    exit_button = tk.Button(
        frame,
        text=" >> Exit << ",
        bg="#EF5A5A",        # rouge
        fg="black",
        activebackground="#B91C1C",
        activeforeground="white",
        command=root.destroy)
    exit_button.grid(column=0, row=6, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main_gui()
