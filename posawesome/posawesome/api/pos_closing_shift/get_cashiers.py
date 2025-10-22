# -*- coding: utf-8 -*-
# Copyright (c) 2024, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


@frappe.whitelist()
def get_cashiers(doctype, txt, searchfield, start, page_len, filters):
    """
    GET - Get cashiers list for POS Profile
    """
    try:
        cashiers_list = frappe.get_all("POS Profile User", filters=filters, fields=["user"])
        result = []
        for cashier in cashiers_list:
            user_email = frappe.get_value("User", cashier.user, "email")
            if user_email:
                # Return list of tuples in format (value, label) where value is user ID and label shows both ID and email
                result.append([cashier.user, f"{cashier.user} ({user_email})"])
        return result
        
    except Exception as e:
        frappe.log_error(f"[get_cashiers.py][get_cashiers] Error: {str(e)}")
        return []
