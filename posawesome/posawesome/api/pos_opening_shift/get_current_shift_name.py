# -*- coding: utf-8 -*-
"""
Get Current Shift Name Function
Handles getting current user's open POS Opening Shift basic info
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def get_current_shift_name():
    """
    GET - Get current user's open POS Opening Shift basic info
    """
    try:
        user = frappe.session.user

        # Find latest open shift for this user
        rows = frappe.get_all(
            "POS Opening Shift",
            filters={
                "user": user,
                "docstatus": 1,
                "status": "Open",
            },
            fields=["name", "company", "period_start_date", "pos_profile", "user"],
            order_by="period_start_date desc",
            limit=1,
        )

        if not rows:
            return {
                "success": False,
                "message": "No active shift found",
                "data": None,
            }

        row = rows[0]
        # Ensure period_start_date is serializable
        if row.get("period_start_date"):
            row["period_start_date"] = str(row["period_start_date"])

        result = {
            "success": True,
            "data": row,
        }
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting current shift: {str(e)}",
            "data": None,
        }
