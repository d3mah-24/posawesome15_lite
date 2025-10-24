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
        offer_type = offer.get('offer_type')

        if not offer_type:
            # No offer_type specified - this is a general offer
            return True

        # If offer_type is specified, the corresponding field MUST have a value
        if offer_type == "item_code":
            if not offer.get('item_code'):
                return False  # Field is required but empty
            # Check if item exists in invoice
            for item in invoice_doc.items:
                if item.item_code == offer.item_code:
                    return True
            return False

        elif offer_type == "item_group":
            if not offer.get('item_group'):
                return False
            # Check item group
            for item in invoice_doc.items:
                if item.item_group == offer.item_group:
                    return True
            return False

        elif offer_type == "brand":
            if not offer.get('brand'):
                return False
            # Check brand
            for item in invoice_doc.items:
                if item.brand == offer.brand:
                    return True
            return False

        elif offer_type == "customer":
            if not offer.get('customer'):
                return False
            # Check customer
            if invoice_doc.customer == offer.customer:
                return True
            return False

        elif offer_type == "customer_group":
            if not offer.get('customer_group'):
                return False
            # Check customer group
            customer_doc = frappe.get_doc("Customer", invoice_doc.customer)
            if customer_doc.customer_group == offer.customer_group:
                return True
            return False

        elif offer_type == "grand_total":
            # For grand_total offers, check min_amt and max_amt conditions
            # These are already checked above in the general validation
            # If we reach here, it means the offer is applicable
            return True

        # If offer_type is not recognized, reject the offer
        return False

    except Exception as e:
        frappe.log_error(f"[ERROR] is_offer_applicable exception for offer '{offer.get('name', 'Unknown')}': {str(e)}", "Offers Debug - Exception")
        return False
