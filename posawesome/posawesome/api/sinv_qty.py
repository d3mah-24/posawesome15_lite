# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def get_user_shift_invoice_count(pos_profile, pos_opening_shift):
    """
    Get total count of invoices for current shift filtered by current user
    Based on: POS Profile User.user = Sales Invoice.owner AND docstatus=1
    """
    if not pos_profile or not pos_opening_shift:
        return 0

    # Get current user from session
    current_user = frappe.session.user

    try:
        # Check if current user is in POS Profile Users
        pos_profile_user = frappe.db.exists("POS Profile User", {
            "parent": pos_profile,
            "user": current_user
        })

        if not pos_profile_user:
            # If user not in POS Profile Users, return 0
            return 0

        # Count invoices for current user
        count = frappe.db.count("Sales Invoice", {
            "pos_profile": pos_profile,
            "is_pos": 1,
            "posa_pos_opening_shift": pos_opening_shift,
            "docstatus": 1,  # Only submitted invoices
            "owner": current_user  # Filter by current user
        })
        return count
    except Exception as e:
        frappe.log_error(f"Error getting user shift invoice count: {str(e)}")
        return 0


@frappe.whitelist()
def get_user_shift_stats(pos_profile, pos_opening_shift):
    """
    Get comprehensive stats for current shift filtered by current user
    Based on: POS Profile User.user = Sales Invoice.owner AND docstatus=1
    """
    if not pos_profile or not pos_opening_shift:
        return {
            "invoice_count": 0,
            "total_amount": 0,
            "total_items": 0
        }

    # Get current user from session
    current_user = frappe.session.user

    try:
        # Check if current user is in POS Profile Users
        pos_profile_user = frappe.db.exists("POS Profile User", {
            "parent": pos_profile,
            "user": current_user
        })

        if not pos_profile_user:
            # If user not in POS Profile Users, return empty stats
            return {
                "invoice_count": 0,
                "total_amount": 0,
                "total_items": 0
            }

        # Get invoice count
        invoice_count = frappe.db.count("Sales Invoice", {
            "pos_profile": pos_profile,
            "is_pos": 1,
            "posa_pos_opening_shift": pos_opening_shift,
            "docstatus": 1,  # Only submitted invoices
            "owner": current_user  # Filter by current user
        })

        # Get total amount
        total_amount_result = frappe.db.sql("""
            SELECT SUM(grand_total) as total_amount
            FROM `tabSales Invoice`
            WHERE pos_profile = %s
            AND is_pos = 1
            AND posa_pos_opening_shift = %s
            AND docstatus = 1
            AND owner = %s
        """, (pos_profile, pos_opening_shift, current_user))

        total_amount = total_amount_result[0][0] if total_amount_result and total_amount_result[0][0] else 0

        # Get total items count
        total_items_result = frappe.db.sql("""
            SELECT SUM(qty) as total_items
            FROM `tabSales Invoice Item` sii
            INNER JOIN `tabSales Invoice` si ON sii.parent = si.name
            WHERE si.pos_profile = %s
            AND si.is_pos = 1
            AND si.posa_pos_opening_shift = %s
            AND si.docstatus = 1
            AND si.owner = %s
        """, (pos_profile, pos_opening_shift, current_user))

        total_items = total_items_result[0][0] if total_items_result and total_items_result[0][0] else 0

        return {
            "invoice_count": invoice_count,
            "total_amount": total_amount,
            "total_items": total_items,
            "user": current_user
        }

    except Exception as e:
        frappe.log_error(f"Error getting user shift stats: {str(e)}")
        return {
            "invoice_count": 0,
            "total_amount": 0,
            "total_items": 0,
            "user": current_user
        }
