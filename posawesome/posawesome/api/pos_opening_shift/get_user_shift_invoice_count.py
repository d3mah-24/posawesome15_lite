# -*- coding: utf-8 -*-
"""
Get User Shift Invoice Count Function
Handles getting user shift invoice count
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def get_user_shift_invoice_count(pos_profile, pos_opening_shift):
    """
    GET - Get user shift invoice count
    """
    try:
        count = frappe.db.count("Sales Invoice", {
            "posa_pos_opening_shift": pos_opening_shift,
            "docstatus": 1
        })
        return count
        
    except Exception as e:
        return 0
