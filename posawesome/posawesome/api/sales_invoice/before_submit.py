# -*- coding: utf-8 -*-
"""
Before Submit Hook - Enhanced ERPNext Natural Operations
Handles automatic offers and pre-submission business logic
"""

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils import flt


def before_submit(doc, method):
    """
    ERPNext Hook - Called automatically before submit()
    
    ERPNext Natural Approach:
    - Business logic moved here from submit.py
    - No save() calls needed - ERPNext handles the lifecycle
    - Just modify the document, ERPNext saves automatically
    - Clean separation of concerns
    """
    if not doc.is_pos:
        return
    
    # Apply automatic offers if enabled in POS Profile
    apply_automatic_offers(doc)
    
    # Handle payments and rounding
    handle_pos_payments(doc)
    
    # Call loyalty and coupon functions
    handle_loyalty_and_coupons(doc)
    
    # Final pre-submission validations
    final_pre_submit_validations(doc)


def apply_automatic_offers(doc):
    """
    Apply automatic offers based on POS Profile settings
    ERPNext Natural: Modify document, no save() needed
    (Moved from submit.py to proper hook location)
    """
    try:
        # Check if auto-fetch offers is enabled
        if not doc.pos_profile:
            return
            
        auto_fetch_offers = frappe.get_cached_value(
            "POS Profile",
            doc.pos_profile,
            "posa_auto_fetch_offers"
        )
        
        if not auto_fetch_offers:
            return
        
        # Get applicable offers
        from posawesome.posawesome.api.pos_offer.get_applicable_offers import get_applicable_offers
        applicable_offers = get_applicable_offers(doc.name)
        
        if not applicable_offers:
            return
        
        # Apply offers to document (ERPNext will save automatically)
        for offer in applicable_offers:
            # Check if offer already exists
            existing_offer = None
            if hasattr(doc, 'posa_offers') and doc.posa_offers:
                existing_offer = next(
                    (row for row in doc.posa_offers if row.offer_name == offer.name), 
                    None
                )
            
            if existing_offer:
                continue
            
            # Add offer to document
            doc.append("posa_offers", {
                "offer_name": offer.name,
                "apply_on": offer.apply_on or "Transaction",
                "offer": offer.offer or "Grand Total", 
                "offer_applied": 1,
                "coupon_based": offer.coupon_based or 0
            })
            
            # Apply discount if percentage-based
            if offer.discount_type == "Discount Percentage":
                doc.additional_discount_percentage = offer.discount_percentage
                # Let ERPNext calculate discount_amount automatically
        
        # ERPNext will recalculate taxes and totals automatically
        
    except Exception as e:
        # Log error but don't fail submission
        frappe.log_error(f"Error applying automatic offers: {str(e)}")


def handle_pos_payments(doc):
    """
    Handle POS payments and rounding adjustments
    ERPNext Natural: Modify document, ERPNext handles validation
    """
    if not doc.payments:
        frappe.throw(_("At least one payment is required for POS Invoice"))
    
    # Payment validation with auto-adjustment for rounding
    total_payments = sum(flt(payment.amount) for payment in doc.payments)
    target_amount = flt(doc.rounded_total) if hasattr(doc, 'rounded_total') and doc.rounded_total else flt(doc.grand_total)
    difference = abs(total_payments - target_amount)

    # Auto-adjust payment if difference is small (rounding issue)
    if 0.01 <= difference <= 1.0:
        if doc.payments:
            adjustment = total_payments - target_amount
            doc.payments[0].amount = flt(doc.payments[0].amount) - adjustment
            # Recalculate after adjustment
            total_payments = sum(flt(payment.amount) for payment in doc.payments)
            difference = abs(total_payments - target_amount)

    # Final validation with tolerance
    if difference > 0.05:
        frappe.throw(_(
            "Payment amount must equal total. Total payments: {0}, Invoice total: {1}"
        ).format(total_payments, target_amount))


def handle_loyalty_and_coupons(doc):
    """
    Handle loyalty points and coupons
    ERPNext Natural: Call existing functions if available
    """
    try:
        from posawesome.posawesome.api.add_loyalty_point import add_loyalty_point
        from posawesome.posawesome.api.update_coupon import update_coupon
        
        add_loyalty_point(doc)
        update_coupon(doc, "used")
    except ImportError:
        # Functions might not exist, continue without them
        pass
    except Exception as e:
        # Log but don't fail submission
        frappe.log_error(f"Error handling loyalty/coupons: {str(e)}")


def final_pre_submit_validations(doc):
    """
    Final validations before submission
    ERPNext Natural: Use frappe.throw() for validation errors
    """
    # Ensure grand total is positive
    if doc.grand_total <= 0:
        frappe.throw(_("Grand Total must be greater than zero"))
    
    # Basic required field check (redundant with validate hook, but safe)
    if not doc.customer:
        frappe.throw(_("Customer is required"))
    
    if not doc.items:
        frappe.throw(_("At least one item is required"))
