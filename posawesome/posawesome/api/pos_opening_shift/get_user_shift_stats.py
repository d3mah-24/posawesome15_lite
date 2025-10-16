# -*- coding: utf-8 -*-
"""
Get User Shift Stats Function
Handles getting user shift statistics
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def get_user_shift_stats(pos_profile, pos_opening_shift):
    """
    GET - Get user shift statistics
    """
    try:
        # Get total sales amount
        total_sales = frappe.db.sql("""
            SELECT SUM(grand_total) as total
            FROM `tabSales Invoice`
            WHERE posa_pos_opening_shift = %s
            AND docstatus = 1
        """, (pos_opening_shift,), as_dict=True)
        
        # Get invoice count
        invoice_count = frappe.db.count("Sales Invoice", {
            "posa_pos_opening_shift": pos_opening_shift,
            "docstatus": 1
        })
        
        total_amount = total_sales[0].total or 0
        result = {
            "total_sales": total_amount,
            "invoice_count": invoice_count,
            "shift_name": pos_opening_shift
        }
        return result
        
    except Exception as e:
        return {
            "total_sales": 0,
            "invoice_count": 0,
            "shift_name": pos_opening_shift
        }
