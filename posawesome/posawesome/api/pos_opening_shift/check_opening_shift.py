# -*- coding: utf-8 -*-
"""
Check Opening Shift Function
Handles checking if user has open shift
"""

from __future__ import unicode_literals

import frappe
from .update_opening_shift_data import update_opening_shift_data


@frappe.whitelist()
def check_opening_shift(user=None, **kwargs):
    """
    GET - Check if user has open shift
    """
    try:
        if not user:
            user = kwargs.get('user')
        if not user:
            return {"error": "Missing required argument: user"}
            
        open_vouchers = frappe.db.get_all(
            "POS Opening Shift",
            filters={
                "user": user,
                "pos_closing_shift": ["in", ["", None]],
                "docstatus": 1,
                "status": "Open",
            },
            fields=["name", "pos_profile"],
            order_by="period_start_date desc",
        )
        
        data = ""
        if len(open_vouchers) > 0:
            data = {}
            data["pos_opening_shift"] = frappe.get_doc(
                "POS Opening Shift", open_vouchers[0]["name"]
            )
            update_opening_shift_data(data, open_vouchers[0]["pos_profile"])
            
        return data
        
    except Exception as e:
        return {"error": f"Error checking opening shift: {str(e)}"}
