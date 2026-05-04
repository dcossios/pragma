"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: OCR extraction service for invoices and certificates
"""

import logging
import os
import re
import tempfile
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import fitz
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)


INVOICE_NUMBER_PATTERNS = [
    r"(?:factura|invoice|no\.?\s*factura|n[uú]mero\s*de\s*factura|serie)\s*[:#-]?\s*([A-Z0-9\-]+)",
    r"\b(FAC[-\s]?\d{3,})\b",
    r"\b([A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12})\b",  # UUID for electronic invoices
]
NIT_PATTERNS = [
    r"(?:nit|n\.?i\.?t\.?|identificaci[oó]n\s*tributaria)\s*[:#-]?\s*([0-9\-A-Za-z]+)",
    r"\b(\d{5,}-\d|[A-Z\d]{5,})\b",  # Generic ID-like pattern
]
AMOUNT_PATTERNS = [
    r"(?:total|monto|importe|total\s*a\s*pagar|gran\s*total|valor\s*total|neto\s*a\s*pagar|total\s*factura)\s*[:$Q\s]*([0-9][0-9,.\s]*)",
    r"\b(?:total|monto|importe|total\s*a\s*pagar|gran\s*total)\b.*?\b([0-9][0-9,.\s]*)\b", # Any number following a label
    r"\bQ\s*([0-9][0-9,.\s]*)",
    r"\$\s*([0-9][0-9,.\s]*)",
]
DATE_PATTERNS = [
    r"(?:fecha|date|fecha\s*de\s*emisi[oó]n|emisi[oó]n|fec\.\s*emisi[oó]n)\s*[:\-]?\s*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4})",
    r"(?:fecha|date|fecha\s*de\s*emisi[oó]n|emisi[oó]n|fec\.\s*emisi[oó]n)\s*[:\-]?\s*([0-9]{4}[\/\-][0-9]{1,2}[\/\-][0-9]{1,2})",
    r"\b([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4})\b",
    r"\b([0-9]{4}[\/\-][0-9]{1,2}[\/\-][0-9]{1,2})\b",
    r"\b([0-9]{1,2}\s+(?:ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)[a-z]*\s+[0-9]{2,4})\b", # Dates with month names
    r"\b([0-9]{1,2}\s+de\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+de\s+[0-9]{4})\b", # Long Spanish dates
]
SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def _normalize_number(raw_value):
    cleaned = raw_value.strip().replace(" ", "")
    if cleaned.count(",") > 0 and cleaned.count(".") > 0:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    else:
        cleaned = cleaned.replace(",", ".")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _parse_date(raw_value):
    value = raw_value.strip().lower()
    months_es = {
        "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
        "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
        "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12",
        "ene": "01", "feb": "02", "mar": "03", "abr": "04",
        "may": "05", "jun": "06", "jul": "07", "ago": "08",
        "sep": "09", "oct": "10", "nov": "11", "dic": "12",
    }
    
    # Check for "de" and replace month names
    if " de " in value or any(m in value for m in months_es):
        for name, num in months_es.items():
            if name in value:
                value = value.replace(name, num).replace(" de ", "/")
                break
    
    # Remove extra spaces and clean
    value = re.sub(r"\s+", "/", value).replace("-", "/").replace("//", "/")
    
    accepted_formats = ["%d/%m/%Y", "%d/%m/%y", "%Y/%m/%d", "%m/%d/%Y"]
    for fmt in accepted_formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _extract_first_match(patterns, text):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as document:
        text = "\n".join(page.get_text() for page in document)
    
    # If the PDF is scanned (little to no text extracted), fallback to OCR on each page
    if len(text.strip()) < 50:
        ocr_text = []
        with fitz.open(file_path) as document:
            for page in document:
                # Render page to image (pixmap)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Scale for better OCR
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                ocr_text.append(pytesseract.image_to_string(img, lang="eng+spa"))
        text = "\n".join(ocr_text)
    
    return text


def _extract_text_from_image(file_path):
    with Image.open(file_path) as image:
        # Preprocessing: convert to grayscale
        processed_img = image.convert("L")
        return pytesseract.image_to_string(processed_img, lang="eng+spa")


def _extract_text_from_path(file_path):
    extension = Path(file_path).suffix.lower()
    if extension == ".pdf":
        return _extract_text_from_pdf(file_path)
    if extension in SUPPORTED_IMAGE_EXTENSIONS:
        return _extract_text_from_image(file_path)
    raise ValueError(f"Formato no soportado para OCR: {extension}")


def extract_invoice_data(file_object):
    original_name = getattr(file_object, "name", "")
    extension = Path(original_name).suffix.lower()
    if hasattr(file_object, "seek"):
        file_object.seek(0)
    file_bytes = file_object.read()
    if hasattr(file_object, "seek"):
        file_object.seek(0)

    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tmp_file:
        tmp_file.write(file_bytes)
        temp_path = tmp_file.name

    try:
        text = _extract_text_from_path(temp_path)
        logger.info(f"Extracted Text (first 200 chars): {text[:200]}")
        return parse_invoice_text(text)
    except ValueError as e:
        return {
            "numero_factura": None,
            "cliente_nit": None,
            "monto": None,
            "fecha": None,
            "errors": [str(e)],
            "raw_text": "",
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def parse_invoice_text(text):
    invoice_number = _extract_first_match(INVOICE_NUMBER_PATTERNS, text)
    nit = _extract_first_match(NIT_PATTERNS, text)
    raw_amount = _extract_first_match(AMOUNT_PATTERNS, text)
    raw_date = _extract_first_match(DATE_PATTERNS, text)

    amount = _normalize_number(raw_amount) if raw_amount else None
    parsed_date = _parse_date(raw_date) if raw_date else None

    errors = []
    if not invoice_number:
        errors.append("No se encontró número de factura en el documento.")
    if not nit:
        errors.append("No se encontró NIT en el documento.")
    if raw_amount and amount is None:
        errors.append("El monto extraído no tiene un formato válido.")
    if not raw_amount:
        errors.append("No se encontró monto en el documento.")
    if raw_date and parsed_date is None:
        errors.append("La fecha extraída no tiene un formato válido.")
    if not raw_date:
        errors.append("No se encontró fecha en el documento.")

    return {
        "numero_factura": invoice_number,
        "cliente_nit": nit,
        "monto": amount,
        "fecha": parsed_date,
        "errors": errors,
        "raw_text": text[:5000],
    }
