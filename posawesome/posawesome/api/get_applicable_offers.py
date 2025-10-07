# -*- coding: utf-8 -*-
"""
Get Applicable Offers API
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()  # type: ignore
def get_applicable_offers(invoice_name):
    """
    GET - Get all applicable offers for an invoice
    """
    try:
        if not invoice_name:
            return []

        doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
        
        # Get all active offers
        offers = frappe.get_all(
            "POS Offer",
            filters={"disabled": 0},
            fields=["name", "offer_name", "offer_type", "discount_percentage", "discount_amount"]
        )
        
        applicable_offers = []
        
        for offer in offers:
            # Check if offer is applicable
            if _is_offer_applicable(doc, offer):
                applicable_offers.append(offer)
        
        return applicable_offers
        
    except Exception as e:
        frappe.log_error(f"Error getting applicable offers: {str(e)}")
        return []


def _is_offer_applicable(doc, offer):
    """Check if an offer is applicable to the invoice"""
    try:
        # Check minimum quantity
        total_qty = sum(frappe.utils.flt(item.qty) for item in doc.items)
        if offer.get("min_qty", 0) > 0 and total_qty < offer.min_qty:
            return False
        
        # Check minimum amount
        if offer.get("min_amount", 0) > 0 and frappe.utils.flt(doc.grand_total) < offer.min_amount:
            return False
        
        return True
        
    except Exception:
        return False
