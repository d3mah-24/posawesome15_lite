import os
import csv
import frappe

from pathlib import Path

TRANSLATIONS_DIR = Path(__file__).resolve().parents[2] / "translations"


@frappe.whitelist(allow_guest=True)
def get_translations(lang: str = None):
    lang = (lang or "en").lower()
    supported = {"en": "en.csv", "ar": "ar.csv"}

    csv_file = os.path.join(TRANSLATIONS_DIR, supported.get(lang, "en.csv"))
    translations = {}
    if not os.path.exists(csv_file):
        return {"success": False, "error": f"No file for {lang}", "translations": {}}

    with open(csv_file, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            key = row.get("key")
            val = row.get("value", "")
            if key:
                translations[key.strip()] = val.strip()

    return {"success": True, "translations": translations, "lang": lang}
