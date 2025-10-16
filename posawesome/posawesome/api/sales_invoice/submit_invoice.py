# -*- coding: utf-8 -*-
"""
Submit Invoice Function
Handles invoice submission
"""

from __future__ import unicode_literals

import json
import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def submit_invoice(data=None, invoice=None, invoice_data=None, print_invoice=False):
    """
    POST - Submit invoice using ERPNext's built-in submit method
    """
    
    try:
        # Handle different parameter formats
        if invoice_data:
            invoice_data = json.loads(invoice_data) if isinstance(invoice_data, str) else invoice_data
        elif invoice:
            invoice_data = json.loads(invoice) if isinstance(invoice, str) else invoice
        elif data:
            invoice_data = json.loads(data) if isinstance(data, str) else data
        else:
            frappe.throw("No invoice data provided")
        
        if not invoice_data.get("name"):
            frappe.throw("Invoice name is required")
        
        # Get the invoice document
        doc = frappe.get_doc("Sales Invoice", invoice_data["name"])

        # Update the document with new data
        doc.update(invoice_data)
        
        # Apply offers before submission
        try:
            from posawesome.posawesome.api.pos_offer.get_applicable_offers import get_applicable_offers
            
            # Get applicable offers for this invoice
            applicable_offers = get_applicable_offers(doc.name)
            
            if applicable_offers:
                # Apply offers directly
                for offer in applicable_offers:
                    # فحص إذا كان العرض موجود بالفعل لتجنب التكرار
                    existing_offer = None
                    if hasattr(doc, 'posa_offers') and doc.posa_offers:
                        existing_offer = next(
                            (row for row in doc.posa_offers 
                             if row.offer_name == offer.name), 
                            None
                        )
                    
                    if existing_offer:
                        # تطبيق الخصم حتى لو كان العرض موجود
                        if offer.discount_type == "Discount Percentage":
                            doc.additional_discount_percentage = offer.discount_percentage
                            doc.discount_amount = (doc.grand_total * offer.discount_percentage) / 100
                        continue
                    
                    # Add offer to POS Offer Detail child table
                    doc.append("posa_offers", {
                        "offer_name": offer.name,
                        "apply_on": offer.apply_on or "Transaction",
                        "offer": offer.offer or "Grand Total",
                        "offer_applied": 1,
                        "coupon_based": offer.coupon_based or 0
                    })
                    
                    if offer.discount_type == "Discount Percentage":
                        # Apply discount to invoice
                        doc.additional_discount_percentage = offer.discount_percentage
                        doc.discount_amount = (doc.grand_total * offer.discount_percentage) / 100
                
        except Exception as e:
            # لا نوقف العملية إذا فشل تطبيق العروض
            pass
        
        # Recalculate totals after applying offers
        doc.calculate_taxes_and_totals()
        
        # Handle payments - let ERPNext handle the calculations
        if invoice_data.get("payments"):
            doc.payments = []
            total_payment_amount = 0
            
            # First pass: collect all non-zero payments
            valid_payments = []
            for payment in invoice_data["payments"]:
                payment_amount = flt(payment.get("amount", 0))
                if payment_amount > 0:
                    valid_payments.append({
                        "mode_of_payment": payment.get("mode_of_payment"),
                        "amount": payment_amount,
                        "account": payment.get("account", ""),
                        "default": payment.get("default", 0)
                    })
                    total_payment_amount += payment_amount
            
            # Second pass: adjust payments to match rounded total
            if valid_payments:
                # Use rounded_total if available, otherwise use grand_total
                target_amount = flt(doc.rounded_total) if hasattr(doc, 'rounded_total') and doc.rounded_total else flt(doc.grand_total)
                
                if total_payment_amount > target_amount:
                    # Distribute excess proportionally or adjust the largest payment
                    excess = total_payment_amount - target_amount
                    
                    # Find the largest payment to adjust
                    largest_payment = max(valid_payments, key=lambda p: p["amount"])
                    largest_payment["amount"] = flt(largest_payment["amount"]) - excess
                    
                    # Ensure no negative amounts
                    if largest_payment["amount"] < 0:
                        largest_payment["amount"] = 0
                
                # Add all valid payments
                for payment in valid_payments:
                    if flt(payment["amount"]) > 0:
                        doc.append("payments", payment)
            else:
                # No valid payments provided, add default payment from POS Profile
                default_payment = frappe.call("posawesome.posawesome.api.pos_profile.get_default_payment_from_pos_profile", 
                    doc.pos_profile, doc.company)
                if default_payment and default_payment.get("message"):
                    # Use rounded_total if available, otherwise use grand_total
                    target_amount = flt(doc.rounded_total) if hasattr(doc, 'rounded_total') and doc.rounded_total else flt(doc.grand_total)
                    doc.append("payments", {
                        "mode_of_payment": default_payment["message"]["mode_of_payment"],
                        "amount": target_amount,
                        "account": default_payment["message"]["account"],
                        "default": 1
                    })
        
        # Let ERPNext handle all calculations and submit
        
        # Handle rounding adjustment by adding it to write_off_amount
        if hasattr(doc, 'rounding_adjustment') and doc.rounding_adjustment:
            doc.write_off_amount = flt(doc.write_off_amount or 0) + flt(doc.rounding_adjustment)
        
        # Save the document first to ensure all data is persisted
        doc.flags.ignore_permissions = True
        frappe.flags.ignore_account_permission = True
        doc.save()
        
        # Now submit using ERPNext's original submit method
        doc.submit()

        result = {
            "success": True,
            "invoice": doc.as_dict(),
            "print_invoice": print_invoice
        }
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
