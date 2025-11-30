#!/usr/bin/env python3
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from config import REPORTS_DIR

class PDFReport:
    def __init__(self, title="LN-DIDS Scan Report"):
        self.title = title
        os.makedirs(REPORTS_DIR, exist_ok=True)

    def generate_from_txt(self, txt_path):
        """
        Generate a PDF report from a given text file.
        Returns the path of the generated PDF.
        """
        if not os.path.exists(txt_path):
            raise FileNotFoundError(f"Text file not found: {txt_path}")

        filename = os.path.basename(txt_path).replace(".txt", ".pdf")
        pdf_path = os.path.join(REPORTS_DIR, filename)

        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, self.title)
        c.setFont("Helvetica", 10)

        y = height - 80
        with open(txt_path, "r") as f:
            for line in f:
                if y < 50:
                    c.showPage()
                    y = height - 50
                c.drawString(50, y, line.strip())
                y -= 15

        c.save()
        return pdf_path
