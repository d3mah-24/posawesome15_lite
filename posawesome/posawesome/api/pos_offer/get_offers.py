# -*- coding: utf-8 -*-
"""
Get Offers Function
Handles getting all offers for POS Profile
"""

from __future__ import unicode_literals

import frappe
from frappe.utils import nowdate


@frappe.whitelist()
def get_offers(profile):
    """
    GET - Get all offers for POS Profile (مطابق للنسخة القديمة)
    """
    try:
        pos_profile = frappe.get_doc("POS Profile", profile)
        company = pos_profile.company
        warehouse = pos_profile.warehouse
        date = nowdate()

        values = {
            "company": company,
            "pos_profile": profile,
            "warehouse": warehouse,
            "valid_from": date,
            "valid_upto": date,
        }

        # استخدام SQL مباشر مثل النسخة القديمة
        data = (
            frappe.db.sql(
                """
            SELECT *
            FROM `tabPOS Offer`
            WHERE
            disable = 0 AND
            company = %(company)s AND
            (pos_profile is NULL OR pos_profile = '' OR pos_profile = %(pos_profile)s) AND
            (warehouse is NULL OR warehouse = '' OR warehouse = %(warehouse)s) AND
            (valid_from is NULL OR valid_from = '' OR valid_from <= %(valid_from)s) AND
            (valid_upto is NULL OR valid_upto = '' OR valid_upto >= %(valid_upto)s)
        """,
                values=values,
                as_dict=1,
            )
            or []
        )

        return data

    except Exception as e:
        frappe.log_error(f"[ERROR] get_offers exception: {str(e)}\nProfile: {profile}", "Offers Debug - Exception")
        return []
