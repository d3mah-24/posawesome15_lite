# -*- coding: utf-8 -*-
"""
Before Submit Hook Function
Handles Sales Invoice before submit operations
"""

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils import flt


def before_submit(doc, method):
    """
    Before Submit Sales Invoice - Unified Function
    """
    try:
        if not doc.is_pos:
            return

        # Call loyalty and coupon functions first
        try:
            from posawesome.posawesome.api.add_loyalty_point import add_loyalty_point
            from posawesome.posawesome.api.update_coupon import update_coupon
            
            add_loyalty_point(doc)
            update_coupon(doc, "used")
        except ImportError:
            # Functions might not exist, continue without them
            pass
        except Exception as e:
            pass

        # Basic validations
        if not doc.pos_profile:
            frappe.throw(_("POS Profile is required for POS Invoice"))
        if not doc.customer:
            frappe.throw(_("Customer is required for POS Invoice"))
        if not doc.items:
            frappe.throw(_("At least one item is required"))
        if not doc.posa_pos_opening_shift:
            frappe.throw(_("POS Opening Shift is required"))
        if not doc.company:
            frappe.throw(_("Company is required"))
        if not doc.currency:
            frappe.throw(_("Currency is required"))
        if not doc.payments:
            frappe.throw(_("At least one payment is required"))

        # Enhanced payment validation with auto-adjustment
        total_payments = sum(flt(payment.amount) for payment in doc.payments)
        target_amount = flt(doc.rounded_total) if hasattr(doc, 'rounded_total') and doc.rounded_total else flt(doc.grand_total)
        difference = abs(total_payments - target_amount)

        # Auto-adjust payment if difference is small (rounding issue)
        if 0.01 <= difference <= 1.0:
            if doc.payments:
                adjustment = total_payments - target_amount
                doc.payments[0].amount = flt(doc.payments[0].amount) - adjustment
                frappe.msgprint(f"Payment adjusted by {adjustment} due to rounding")
                # Recalculate after adjustment
                total_payments = sum(flt(payment.amount) for payment in doc.payments)
                difference = abs(total_payments - target_amount)

        # Final validation with tolerance
        if difference > 0.05:
            frappe.throw(_(
                "Payment amount must equal rounded total. Total payments: {0}, Rounded total: {1}, Difference: {2}"
            ).format(total_payments, target_amount, difference))

    except Exception as e:
        raise
