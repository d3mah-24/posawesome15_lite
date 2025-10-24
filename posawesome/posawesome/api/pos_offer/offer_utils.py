# -*- coding: utf-8 -*-
"""
Is Offer Applicable Function
Handles checking if offer is applicable based on POS Offer fields
"""

from __future__ import unicode_literals

import frappe
from frappe.utils import getdate


def is_offer_applicable(offer, invoice_doc):
    """
    Helper function to check if offer is applicable based on POS Offer fields
    """
    try:
        offer_name = offer.get('name', 'Unknown')

        # Check company (if offer has specific company, it must match)
        if offer.get('company') and offer.company != invoice_doc.company:
            return False

        # Check date validity
        if offer.get('valid_from') and getdate(offer.valid_from) > getdate():
            return False

        if offer.get('valid_upto') and getdate(offer.valid_upto) < getdate():
            return False

        # Check minimum amount (using min_amt field)
        if offer.get('min_amt') and invoice_doc.grand_total < offer.min_amt:
            return False

        # Check maximum amount (using max_amt field)
        if offer.get('max_amt') and invoice_doc.grand_total > offer.max_amt:
            return False

        # Check minimum quantity (using min_qty field)
        if offer.get('min_qty'):
            total_qty = sum(item.qty for item in invoice_doc.items)
            if total_qty < offer.min_qty:
                return False

        # Check maximum quantity (using max_qty field)
        if offer.get('max_qty'):
            total_qty = sum(item.qty for item in invoice_doc.items)
            if total_qty > offer.max_qty:
                return False

        # Check offer_type field
        if offer.get('offer_type') == "item_code" and offer.get('item_code'):
            # Check specific item code
            invoice_items = [item.item_code for item in invoice_doc.items]
            for item in invoice_doc.items:
                if item.item_code == offer.item_code:
                    return True
            return False

        elif offer.get('offer_type') == "item_group" and offer.get('item_group'):
            # Check item group
            for item in invoice_doc.items:
                if item.item_group == offer.item_group:
                    return True
            return False

        elif offer.get('offer_type') == "brand" and offer.get('brand'):
            # Check brand
            for item in invoice_doc.items:
                if item.brand == offer.brand:
                    return True
            return False

        elif offer.get('offer_type') == "customer" and offer.get('customer'):
            # Check customer
            if invoice_doc.customer == offer.customer:
                return True
            return False

        elif offer.get('offer_type') == "customer_group" and offer.get('customer_group'):
            # Check customer group
            customer_doc = frappe.get_doc("Customer", invoice_doc.customer)
            if customer_doc.customer_group == offer.customer_group:
                return True
            return False

        elif offer.get('offer_type') == "grand_total" and offer.get('grand_total'):
            # Check grand total
            if invoice_doc.grand_total >= offer.grand_total:
                return True
            return False

        # Default: if no specific conditions, offer is applicable
        return True

    except Exception as e:
        frappe.log_error(f"[ERROR] is_offer_applicable exception for offer '{offer.get('name', 'Unknown')}': {str(e)}", "Offers Debug - Exception")
        return False
