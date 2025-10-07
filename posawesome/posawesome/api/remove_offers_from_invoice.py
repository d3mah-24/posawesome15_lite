# -*- coding: utf-8 -*-
"""
Remove Offers From Invoice API
"""

from __future__ import unicode_literals

import json

import frappe


@frappe.whitelist()  # type: ignore
def remove_offers_from_invoice(invoice_name, offer_names):
    """
    DELETE - Remove specific offers from an invoice
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

        # Remove each offer
        for offer_name in offer_names:
            try:
                _remove_single_offer(doc, offer_name)
            except Exception as e:
                frappe.log_error(
                    f"Error removing offer {offer_name}: {str(e)}"
                )
                continue

        # Let ERPNext handle all calculations
        doc.set_missing_values()
        doc.calculate_taxes_and_totals()
        doc.save()

        return doc.as_dict()
    except Exception as e:
        frappe.log_error(
            f"Error in remove_offers_from_invoice: {str(e)}"
        )
        raise


def _remove_single_offer(doc, offer_name):
    """Remove a single offer from the invoice"""
    try:
        offer = frappe.get_doc("POS Offer", offer_name)
        
        if offer.offer_type == "Item Discount":
            # Remove item-level discount
            for item in doc.items:
                if offer.discount_percentage > 0:
                    item.discount_percentage = 0
                elif offer.discount_amount > 0:
                    item.discount_amount = 0
        
        elif offer.offer_type == "Invoice Discount":
            # Remove invoice-level discount
            if offer.discount_percentage > 0:
                doc.additional_discount_percentage = 0
            elif offer.discount_amount > 0:
                doc.discount_amount = 0
        
    except Exception as e:
        frappe.log_error(f"Error removing offer {offer_name}: {str(e)}")