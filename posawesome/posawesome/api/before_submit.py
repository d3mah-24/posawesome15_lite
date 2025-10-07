# -*- coding: utf-8 -*-
"""
Before Submit Hook for Sales Invoice
"""

from __future__ import unicode_literals

import frappe

from posawesome.posawesome.api.add_loyalty_point import add_loyalty_point
from posawesome.posawesome.api.update_coupon import update_coupon


def before_submit(doc, method):
    """
    Before submit hook for Sales Invoice
    """
    # Call all pre-submit functions
    add_loyalty_point(doc)
    update_coupon(doc, "used")
    
    # Additional validation before submitting POS invoices
    if doc.is_pos:
        # Ensure POS opening shift is set
        if not doc.posa_pos_opening_shift:
            frappe.throw("POS Opening Shift is required for POS invoices")
        
        # Validate payments for POS invoices
        if not doc.payments:
            frappe.throw("At least one payment is required for POS invoices")
        
        # Check if total payments match grand total (with tolerance for rounding)
        total_payments = sum(frappe.utils.flt(p.amount) for p in doc.payments)
        grand_total = frappe.utils.flt(doc.grand_total)
        difference = abs(total_payments - grand_total)
        
        # Allow small differences due to rounding (up to 1 SAR)
        if difference > 1.0:
            frappe.throw(
                f"Total payments ({total_payments}) must equal grand total ({grand_total}). "
                f"Difference: {difference}"
            )
        
        # Auto-adjust payment if difference is small (rounding issue)
        if 0.01 <= difference <= 1.0:
            # Adjust the first payment to match grand total
            if doc.payments:
                doc.payments[0].amount = frappe.utils.flt(doc.payments[0].amount) - (total_payments - grand_total)
                frappe.msgprint(f"Payment adjusted by {total_payments - grand_total} due to rounding")
