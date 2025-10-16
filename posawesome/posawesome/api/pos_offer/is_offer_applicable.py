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
        
        # Check apply_on field
        if offer.get('apply_on') == "Item Code" and offer.get('item'):
            # Check specific item
            for item in invoice_doc.items:
                if item.item_code == offer.item:
                    return True
            return False
        
        elif offer.get('apply_on') == "Item Group" and offer.get('item_group'):
            # Check item group
            for item in invoice_doc.items:
                if item.item_group == offer.item_group:
                    return True
            return False
        
        elif offer.get('apply_on') == "Brand" and offer.get('brand'):
            # Check brand
            for item in invoice_doc.items:
                if item.brand == offer.brand:
                    return True
            return False
        
        elif offer.get('apply_on') == "Transaction":
            # Check transaction-level conditions
            return True
        
        # Default: if no specific conditions, offer is applicable
        return True
        
    except Exception as e:
        return False
