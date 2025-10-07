# -*- coding: utf-8 -*-
"""
Apply Offers To Invoice API
"""

from __future__ import unicode_literals

import json

import frappe


@frappe.whitelist()  # type: ignore
def apply_offers_to_invoice(invoice_name, offer_names):
    """
    POST - Apply specific offers to an invoice
    """
    try:
        if not invoice_name or not offer_names:
            return None

        # Handle both string and list inputs
        if isinstance(offer_names, str):
            try:
                offer_names = json.loads(offer_names)
            except (json.JSONDecodeError, ValueError):
                offer_names = [offer_names]

        if not isinstance(offer_names, list):
            offer_names = [offer_names]

        doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore

        # Apply each offer
        for offer_name in offer_names:
            try:
                _apply_single_offer(doc, offer_name)
            except Exception as e:
                frappe.log_error(
                    f"Error applying offer {offer_name}: {str(e)}"
                )
                continue

        # Let ERPNext handle all calculations
        doc.set_missing_values()
        doc.calculate_taxes_and_totals()
        doc.save()

        return doc.as_dict()
    except Exception as e:
        frappe.log_error(
            f"Error in apply_offers_to_invoice: {str(e)}"
        )
        raise


def _apply_single_offer(doc, offer_name):
    """Apply a single offer to the invoice"""
    try:
        offer = frappe.get_doc("POS Offer", offer_name)
        
        if offer.offer_type == "Item Discount":
            # Apply item-level discount
            for item in doc.items:
                if offer.discount_percentage > 0:
                    item.discount_percentage = offer.discount_percentage
                elif offer.discount_amount > 0:
                    item.discount_amount = offer.discount_amount
        
        elif offer.offer_type == "Invoice Discount":
            # Apply invoice-level discount
            if offer.discount_percentage > 0:
                doc.additional_discount_percentage = offer.discount_percentage
            elif offer.discount_amount > 0:
                doc.discount_amount = offer.discount_amount
        
    except Exception as e:
        frappe.log_error(f"Error applying offer {offer_name}: {str(e)}")