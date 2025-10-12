# -*- coding: utf-8 -*-
"""
POS Opening Shift API
Handles all POS Opening Shift related operations
"""

from __future__ import unicode_literals

import frappe

# POS Opening Shift API - Simplified logging


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
        frappe.log_error(f"pos_opening_shift.py(get_current_shift_name): Error {str(e)}", "POS Opening Shift")
        return {
            "success": False,
            "message": f"Error getting current shift: {str(e)}",
            "data": None,
        }


@frappe.whitelist()
def create_opening_voucher(pos_profile, company, balance_details):
    """
    POST - Create new POS Opening Shift
    """
    try:
        import json
        balance_details = json.loads(balance_details)

        new_pos_opening = frappe.get_doc(
            {
                "doctype": "POS Opening Shift",
                "period_start_date": frappe.utils.get_datetime(),
                "posting_date": frappe.utils.getdate(),
                "user": frappe.session.user,
                "pos_profile": pos_profile,
                "company": company,
                "docstatus": 1,
            }
        )
        new_pos_opening.set("balance_details", balance_details)
        new_pos_opening.insert(ignore_permissions=True)

        data = {}
        data["pos_opening_shift"] = new_pos_opening.as_dict()
        update_opening_shift_data(data, new_pos_opening.pos_profile)
        return data
        
    except Exception as e:
        frappe.log_error(f"pos_opening_shift.py(create_opening_voucher): Error {str(e)}", "POS Opening Shift")
        frappe.throw(f"Error creating opening voucher: {str(e)}")


@frappe.whitelist()
def check_opening_shift(user=None, **kwargs):
    """
    GET - Check if user has open shift
    """
    try:
        if not user:
            user = kwargs.get('user')
        if not user:
            frappe.log_error(f"pos_opening_shift.py(check_opening_shift): Missing user argument", "POS Opening Shift")
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
        frappe.log_error(f"pos_opening_shift.py(check_opening_shift): Error {str(e)}", "POS Opening Shift")
        return {"error": f"Error checking opening shift: {str(e)}"}


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
        frappe.log_error(f"pos_opening_shift.py(get_user_shift_invoice_count): Error {str(e)}", "POS Opening Shift")
        return 0


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
        frappe.log_error(f"pos_opening_shift.py(get_user_shift_stats): Error {str(e)}", "POS Opening Shift")
        return {
            "total_sales": 0,
            "invoice_count": 0,
            "shift_name": pos_opening_shift
        }


def update_opening_shift_data(data, pos_profile):
    """
    Helper function to update opening shift data
    """
    try:
        data["pos_profile"] = frappe.get_doc("POS Profile", pos_profile)
        data["company"] = frappe.get_doc("Company", data["pos_profile"].company)
        allow_negative_stock = frappe.get_value(
            "Stock Settings", None, "allow_negative_stock"
        )
        data["stock_settings"] = {}
        data["stock_settings"].update({"allow_negative_stock": allow_negative_stock})
    except Exception as e:
        frappe.log_error(f"pos_opening_shift.py(update_opening_shift_data): Error {str(e)}", "POS Opening Shift")


# POS Opening Shift API - Simplified logging completed
