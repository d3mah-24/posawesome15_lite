# -*- coding: utf-8 -*-
"""
Update Invoice Function
Handles invoice creation and updates
"""

from __future__ import unicode_literals

import json
import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def update_invoice(data):
    """
    PUT - Update invoice data (Simplified POSNext-style approach)
    Let ERPNext handle all calculations and concurrency naturally
    
    This is the PRIMARY API for all invoice operations (create, update, add/remove items).
    Replaces: add_item_to_invoice, update_item_in_invoice, delete_item_from_invoice
    
    Features:
    - Simplified concurrency handling (no Redis locking)
    - Natural ERPNext document lifecycle
    - Optimized for reliability over complexity
    """
    try:
        data = json.loads(data) if isinstance(data, str) else data
    except (json.JSONDecodeError, ValueError) as e:
        frappe.throw(_("Invalid JSON data: {0}").format(str(e)))

    # Simplified approach following POSNext pattern - no Redis locking needed
    # ERPNext framework handles concurrency at document level

    try:
        if data.get("name"):
            try:
                invoice_doc = frappe.get_doc("Sales Invoice", data.get("name"))
                
                # Validate draft status
                if invoice_doc.docstatus != 0:
                    frappe.throw(_("Cannot update submitted invoice"))
                
                # Clean customer-related fields if customer changed
                if data.get("customer") and data.get("customer") != invoice_doc.customer:
                    # Clear fields that belong to previous customer
                    invoice_doc.contact_person = None
                    invoice_doc.customer_address = None
                    invoice_doc.address_display = None
                    invoice_doc.contact_display = None
                    invoice_doc.contact_mobile = None
                    invoice_doc.contact_email = None
                
                invoice_doc.update(data)
            except frappe.DoesNotExistError:
                # Invoice was deleted, create new one
                invoice_doc = frappe.new_doc("Sales Invoice")
                invoice_doc.update(data)
        else:
            invoice_doc = frappe.new_doc("Sales Invoice")
            invoice_doc.update(data)

        # Basic validation for return invoices
        is_return_invoice = (
            data.get("is_return") or invoice_doc.is_return
        )
        if is_return_invoice and invoice_doc.get("return_against"):
            from .validate_return_items_utils import validate_return_items
            invoice_items = [d.as_dict() for d in invoice_doc.items]
            validation = validate_return_items(
                invoice_doc.return_against, invoice_items
            )
            if not validation.get("valid"):
                frappe.throw(validation.get("message"))

        # Check if invoice has items before processing
        if not invoice_doc.items:
            # If no items, delete the invoice if it exists
            if invoice_doc.name:
                frappe.delete_doc("Sales Invoice", invoice_doc.name, ignore_permissions=True)
                frappe.db.commit()
            return None

        # Let ERPNext handle all calculations
        invoice_doc.set_missing_values()

        # Basic business rules (not calculations)
        allow_zero_rated_items = frappe.get_cached_value(
            "POS Profile",
            invoice_doc.pos_profile,
            "posa_allow_zero_rated_items"
        )
        for item in invoice_doc.items:
            if not item.rate or item.rate == 0:
                if allow_zero_rated_items:
                    item.is_free_item = 1
                else:
                    msg = _("Rate cannot be zero for item {0}")
                    frappe.throw(msg.format(item.item_code))
            else:
                item.is_free_item = 0

        # CRITICAL: Calculate taxes and totals to apply item discounts and invoice discounts
        # Without this, discount_percentage and additional_discount_percentage won't be applied
        invoice_doc.calculate_taxes_and_totals()

        # Save and let ERPNext calculate everything
        invoice_doc.flags.ignore_permissions = True
        frappe.flags.ignore_account_permission = True
        invoice_doc.docstatus = 0
        
        # Save the invoice - let ERPNext handle conflicts naturally
        invoice_doc.flags.ignore_permissions = True
        frappe.flags.ignore_account_permission = True
        invoice_doc.docstatus = 0
        invoice_doc.save(ignore_version=True)
        
        # Commit immediately to release locks
        frappe.db.commit()

        # Apply automatic offers ONLY if posa_auto_fetch_offers is enabled
        try:
            # Check POS Profile setting for auto-fetch offers
            posa_auto_fetch_offers = frappe.get_cached_value(
                "POS Profile",
                invoice_doc.pos_profile,
                "posa_auto_fetch_offers"
            )
            
            # Only apply offers automatically if enabled in POS Profile
            if posa_auto_fetch_offers:
                from posawesome.posawesome.api.pos_offer.get_applicable_offers import get_applicable_offers
                
                # Get applicable offers for this invoice
                applicable_offers = get_applicable_offers(invoice_doc.name)
                
                if applicable_offers:
                    # Apply offers directly in sales_invoice.py
                    for offer in applicable_offers:
                        # فحص إذا كان العرض موجود بالفعل لتجنب التكرار
                        existing_offer = None
                        if hasattr(invoice_doc, 'posa_offers') and invoice_doc.posa_offers:
                            existing_offer = next(
                                (row for row in invoice_doc.posa_offers 
                                 if row.offer_name == offer.name), 
                                None
                            )
                        
                        if existing_offer:
                            continue
                        
                        # Add offer to POS Offer Detail child table
                        invoice_doc.append("posa_offers", {
                            "offer_name": offer.name,
                            "apply_on": offer.apply_on or "Transaction",
                            "offer": offer.offer or "Grand Total",
                            "offer_applied": 1,
                            "coupon_based": offer.coupon_based or 0
                        })
                        
                        if offer.discount_type == "Discount Percentage":
                            # Apply discount to invoice
                            invoice_doc.additional_discount_percentage = offer.discount_percentage
                            invoice_doc.discount_amount = (invoice_doc.grand_total * offer.discount_percentage) / 100
                    
                    # Save the invoice with applied offers
                    invoice_doc.flags.ignore_permissions = True
                    frappe.flags.ignore_account_permission = True
                    invoice_doc.save(ignore_version=True)
                    
                    # Commit immediately to release locks
                    frappe.db.commit()
                    
                    # Reload the invoice to get updated totals
                    invoice_doc = frappe.get_doc("Sales Invoice", invoice_doc.name)
            
        except Exception as e:
            # Don't fail the invoice creation if offers fail
            pass

        # Return only essential data needed by POS frontend
        from .invoice_response_utils import get_minimal_invoice_response
        result = get_minimal_invoice_response(invoice_doc)
        return result
        
    except Exception as e:
        frappe.logger().error(f"Error in update_invoice: {str(e)}")
        frappe.logger().error(frappe.get_traceback())
        raise
