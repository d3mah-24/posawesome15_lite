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
            frappe.log_error(f"[DEBUG] Offer '{offer_name}' rejected: Company mismatch (Offer: {offer.company}, Invoice: {invoice_doc.company})", "Offers Debug - Company Check")
            return False
        
        # Check date validity
        if offer.get('valid_from') and getdate(offer.valid_from) > getdate():
            frappe.log_error(f"[DEBUG] Offer '{offer_name}' rejected: Not yet valid (Valid from: {offer.valid_from}, Today: {getdate()})", "Offers Debug - Date Check")
            return False
        
        if offer.get('valid_upto') and getdate(offer.valid_upto) < getdate():
            frappe.log_error(f"[DEBUG] Offer '{offer_name}' rejected: Expired (Valid upto: {offer.valid_upto}, Today: {getdate()})", "Offers Debug - Date Check")
            return False
        
        # Check minimum amount (using min_amt field)
        if offer.get('min_amt') and invoice_doc.grand_total < offer.min_amt:
            frappe.log_error(f"[DEBUG] Offer '{offer_name}' rejected: Min amount not met (Required: {offer.min_amt}, Invoice: {invoice_doc.grand_total})", "Offers Debug - Amount Check")
            return False
        
        # Check maximum amount (using max_amt field)
        if offer.get('max_amt') and invoice_doc.grand_total > offer.max_amt:
            frappe.log_error(f"[DEBUG] Offer '{offer_name}' rejected: Max amount exceeded (Max: {offer.max_amt}, Invoice: {invoice_doc.grand_total})", "Offers Debug - Amount Check")
            return False
        
        # Check minimum quantity (using min_qty field)
        if offer.get('min_qty'):
            total_qty = sum(item.qty for item in invoice_doc.items)
            if total_qty < offer.min_qty:
                frappe.log_error(f"[DEBUG] Offer '{offer_name}' rejected: Min qty not met (Required: {offer.min_qty}, Invoice: {total_qty})", "Offers Debug - Qty Check")
                return False
        
        # Check maximum quantity (using max_qty field)
        if offer.get('max_qty'):
            total_qty = sum(item.qty for item in invoice_doc.items)
            if total_qty > offer.max_qty:
                frappe.log_error(f"[DEBUG] Offer '{offer_name}' rejected: Max qty exceeded (Max: {offer.max_qty}, Invoice: {total_qty})", "Offers Debug - Qty Check")
                return False
        
        # Check apply_on field
        if offer.get('apply_on') == "Item Code" and offer.get('item'):
            # Check specific item
            invoice_items = [item.item_code for item in invoice_doc.items]
            frappe.log_error(f"[DEBUG] Offer '{offer_name}' checking Item Code: {offer.item} in invoice items: {invoice_items}", "Offers Debug - Item Code Check")
            for item in invoice_doc.items:
                if item.item_code == offer.item:
                    frappe.log_error(f"[DEBUG] Offer '{offer_name}' ACCEPTED: Item Code matched", "Offers Debug - Item Code Match")
                    return True
            frappe.log_error(f"[DEBUG] Offer '{offer_name}' rejected: Item Code not found in invoice", "Offers Debug - Item Code Check")
            return False
        
        elif offer.get('apply_on') == "Item Group" and offer.get('item_group'):
            # Check item group
            invoice_groups = [item.item_group for item in invoice_doc.items]
            frappe.log_error(f"[DEBUG] Offer '{offer_name}' checking Item Group: {offer.item_group} in invoice groups: {invoice_groups}", "Offers Debug - Item Group Check")
            for item in invoice_doc.items:
                if item.item_group == offer.item_group:
                    frappe.log_error(f"[DEBUG] Offer '{offer_name}' ACCEPTED: Item Group matched", "Offers Debug - Item Group Match")
                    return True
            frappe.log_error(f"[DEBUG] Offer '{offer_name}' rejected: Item Group not found in invoice", "Offers Debug - Item Group Check")
            return False
        
        elif offer.get('apply_on') == "Brand" and offer.get('brand'):
            # Check brand
            invoice_brands = [item.brand for item in invoice_doc.items]
            frappe.log_error(f"[DEBUG] Offer '{offer_name}' checking Brand: {offer.brand} in invoice brands: {invoice_brands}", "Offers Debug - Brand Check")
            for item in invoice_doc.items:
                if item.brand == offer.brand:
                    frappe.log_error(f"[DEBUG] Offer '{offer_name}' ACCEPTED: Brand matched", "Offers Debug - Brand Match")
                    return True
            frappe.log_error(f"[DEBUG] Offer '{offer_name}' rejected: Brand not found in invoice", "Offers Debug - Brand Check")
            return False
        
        elif offer.get('apply_on') == "Transaction":
            # Check transaction-level conditions
            frappe.log_error(f"[DEBUG] Offer '{offer_name}' ACCEPTED: Transaction-level offer", "Offers Debug - Transaction Check")
            return True
        
        # Default: if no specific conditions, offer is applicable
        frappe.log_error(f"[DEBUG] Offer '{offer_name}' ACCEPTED: Default acceptance (no specific conditions)", "Offers Debug - Default Accept")
        return True
        
    except Exception as e:
        frappe.log_error(f"[ERROR] is_offer_applicable exception for offer '{offer.get('name', 'Unknown')}': {str(e)}", "Offers Debug - Exception")
        return False
