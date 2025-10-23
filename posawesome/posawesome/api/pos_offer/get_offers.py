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
        frappe.log_error(f"[DEBUG] get_offers called with profile: {profile}", "Offers Debug - Get Offers Start")
        
        pos_profile = frappe.get_doc("POS Profile", profile)
        company = pos_profile.company
        warehouse = pos_profile.warehouse
        date = nowdate()

        frappe.log_error(f"[DEBUG] POS Profile details - Company: {company}, Warehouse: {warehouse}, Date: {date}", "Offers Debug - Profile Details")

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
        
        frappe.log_error(f"[DEBUG] Query returned {len(data)} offers. Offer names: {[o.get('name') for o in data]}", "Offers Debug - Query Results")
        
        return data
        
    except Exception as e:
        frappe.log_error(f"[ERROR] get_offers exception: {str(e)}\nProfile: {profile}", "Offers Debug - Exception")
        return []
