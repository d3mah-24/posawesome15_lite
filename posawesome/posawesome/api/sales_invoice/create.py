# -*- coding: utf-8 -*-
"""
Create Invoice Function
Handles new invoice creation only
"""

from __future__ import unicode_literals

import json
import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def create_invoice(data):
    """
    POST - Create new invoice (first item scenario)
    
    This function is called ONLY when creating a new invoice with the first item.
    For subsequent updates, use update_invoice instead.
    
    Features:
    - Creates new Sales Invoice document
    - Sets up initial values from POS Profile
    - Handles first item addition
    - Returns minimal invoice response
    """
    try:
        data = json.loads(data) if isinstance(data, str) else data
    except (json.JSONDecodeError, ValueError) as e:
        frappe.throw(_("Invalid JSON data: {0}").format(str(e)))

    try:
        # Ensure we're not trying to update existing invoice
        if data.get("name"):
            frappe.throw(_("Use update_invoice for existing invoices"))

        # Create new invoice document
        invoice_doc = frappe.new_doc("Sales Invoice")
        invoice_doc.update(data)

        # Check if invoice has items
        if not invoice_doc.items:
            frappe.throw(_("Cannot create invoice without items"))

        # Let ERPNext handle all calculations
        invoice_doc.set_missing_values()

        # Basic business rules
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

        # Calculate taxes and totals
        invoice_doc.calculate_taxes_and_totals()

        # Save the new invoice
        invoice_doc.flags.ignore_permissions = True
        frappe.flags.ignore_account_permission = True
        invoice_doc.docstatus = 0
        invoice_doc.save(ignore_version=True)
        
        # Commit immediately
        frappe.db.commit()

        # Apply automatic offers if enabled
        try:
            posa_auto_fetch_offers = frappe.get_cached_value(
                "POS Profile",
                invoice_doc.pos_profile,
                "posa_auto_fetch_offers"
            )
            
            if posa_auto_fetch_offers:
                from posawesome.posawesome.api.pos_offer.get_applicable_offers import get_applicable_offers
                
                applicable_offers = get_applicable_offers(invoice_doc.name)
                
                if applicable_offers:
                    for offer in applicable_offers:
                        # Check if offer already exists
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
                            invoice_doc.additional_discount_percentage = offer.discount_percentage
                            invoice_doc.discount_amount = (invoice_doc.grand_total * offer.discount_percentage) / 100
                    
                    invoice_doc.flags.ignore_permissions = True
                    frappe.flags.ignore_account_permission = True
                    invoice_doc.save(ignore_version=True)
                    frappe.db.commit()
                    
                    invoice_doc = frappe.get_doc("Sales Invoice", invoice_doc.name)
            
        except Exception as e:
            frappe.logger().error(f"Error applying offers during create: {str(e)}")

        from .invoice_response import get_minimal_invoice_response
        result = get_minimal_invoice_response(invoice_doc)
        return result
        
    except Exception as e:
        frappe.logger().error(f"Error in create_invoice: {str(e)}")
        frappe.logger().error(frappe.get_traceback())
        raise