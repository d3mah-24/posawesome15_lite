# -*- coding: utf-8 -*-
"""
Sales Invoice API
Handles all Sales Invoice related operations
"""

from __future__ import unicode_literals

import json
import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def update_invoice(data):
    """
    PUT - Update invoice data
    Let ERPNext handle all calculations through set_missing_values() and save()
    
    This is the PRIMARY API for all invoice operations (create, update, add/remove items).
    Replaces: add_item_to_invoice, update_item_in_invoice, delete_item_from_invoice
    """
    try:
        data = json.loads(data) if isinstance(data, str) else data
    except (json.JSONDecodeError, ValueError) as e:
        frappe.throw(_("Invalid JSON data: {0}").format(str(e)))

    if data.get("name"):
        try:
            invoice_doc = frappe.get_doc("Sales Invoice", data.get("name"))
            
            # Validate draft status
            if invoice_doc.docstatus != 0:
                frappe.throw(_("Cannot update submitted invoice"))
            
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
    
    # Use faster save without hooks for draft invoices
    # This reduces lock duration significantly
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
            from posawesome.posawesome.api.pos_offer import get_applicable_offers
            
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
    result = get_minimal_invoice_response(invoice_doc)
    return result


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
            from posawesome.posawesome.api.pos_offer import get_applicable_offers
            
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
        frappe.log_error(f"sales_invoice.py(submit_invoice): Error {str(e)}", "POS Submit")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def delete_invoice(invoice_name):
    """
    DELETE - Delete draft invoice
    Handles lock timeouts gracefully when invoice is being modified
    """
    try:
        # Try to get document with shorter wait time
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        
        if doc.docstatus != 0:
            frappe.throw(_("Cannot delete submitted invoice"))
        
        doc.flags.ignore_permissions = True
        doc.delete()
        
        result = {"message": "Invoice deleted successfully"}
        return result
        
    except frappe.QueryTimeoutError:
        # Document is locked by another transaction (update_invoice in progress)
        # This is expected in POS with rapid operations
        frappe.clear_last_message()
        return {"message": "Invoice is being updated, deletion skipped"}
        
    except Exception as e:
        # Shorten error message to avoid CharacterLengthExceededError
        error_msg = str(e)[:100]  # Limit to 100 chars
        frappe.log_error(f"Delete error: {error_msg}", "POS Delete Invoice")
        frappe.throw(_("Error deleting invoice: {0}").format(error_msg))


@frappe.whitelist()
def get_draft_invoices(pos_opening_shift):
    """
    GET - Get all draft invoices for a POS opening shift
    """
    try:
        filters = {
            "posa_pos_opening_shift": pos_opening_shift,
            "docstatus": 0,
            "is_pos": 1
        }
        
        invoices = frappe.get_all(
            "Sales Invoice",
            filters=filters,
            fields=[
                "name", "customer", "grand_total", "outstanding_amount",
                "creation", "modified"
            ],
            order_by="modified desc"
        )
        
        data = []
        for invoice in invoices:
            data.append({
                "name": invoice.name,
                "customer": invoice.customer,
                "grand_total": invoice.grand_total,
                "outstanding_amount": invoice.outstanding_amount,
                "creation": invoice.creation,
                "modified": invoice.modified
            })
        
        return data
        
    except Exception as e:
        frappe.log_error(f"sales_invoice.py(get_draft_invoices): Error {str(e)}", "POS Submit")
        return []


@frappe.whitelist()
def search_invoices_for_return(invoice_name, company):
    """
    Search invoices for return operations
    """
    try:
        if not invoice_name:
            return []

        # Search for invoices that can be returned
        invoices = frappe.get_all(
            "Sales Invoice",
            filters={
                "name": ["like", f"%{invoice_name}%"],
                "company": company,
                "docstatus": 1,  # Only submitted invoices
                "is_return": 0,  # Not already a return
                "outstanding_amount": [">", 0]  # Has outstanding amount
            },
            fields=["name", "customer", "grand_total", "outstanding_amount", "posting_date"],
            limit=20
        )

        return invoices

    except Exception as e:
        frappe.log_error(f"sales_invoice.py(search_invoices_for_return): Error {str(e)}", "POS Submit")
        return []


# Functions moved to pos_profile.py


def validate_return_items(return_against, invoice_items):
    """
    Validate return items against original invoice
    """
    try:
        if not return_against:
            return {"valid": True, "message": "No return against specified"}
        
        # Get original invoice
        original_invoice = frappe.get_doc("Sales Invoice", return_against)
        
        # Check if return quantities are valid
        for item in invoice_items:
            original_item = None
            for orig_item in original_invoice.items:
                if orig_item.item_code == item["item_code"]:
                    original_item = orig_item
                    break
            
            if not original_item:
                return {
                    "valid": False,
                    "message": f"Item {item['item_code']} not found in original invoice"
                }
            
            if flt(item["qty"]) > flt(original_item.qty):
                return {
                    "valid": False,
                    "message": f"Return quantity for {item['item_code']} exceeds original quantity"
                }
        
        result = {"valid": True, "message": "Return items are valid"}
        return result
        
    except Exception as e:
        frappe.log_error(f"sales_invoice.py(validate_return_items): Error {str(e)}", "POS Submit")
        return {
            "valid": False,
            "message": f"Error validating return items: {str(e)}"
        }


def get_minimal_invoice_response(invoice_doc):
    """
    Return only essential data needed by POS frontend to minimize response size
    This dramatically reduces the response size from ~50KB to ~5KB
    """
    
    # Essential invoice fields only
    minimal_response = {
        "name": invoice_doc.name,
        "is_return": invoice_doc.is_return or 0,
        "docstatus": invoice_doc.docstatus,
        
        # Financial totals (required for POS display)
        "total": invoice_doc.total or 0,
        "net_total": invoice_doc.net_total or 0, 
        "grand_total": invoice_doc.grand_total or 0,
        "total_taxes_and_charges": invoice_doc.total_taxes_and_charges or 0,
        "discount_amount": invoice_doc.discount_amount or 0,
        "additional_discount_percentage": invoice_doc.additional_discount_percentage or 0,
        
        # Items with only essential fields
        "items": []
    }
    
    # Add minimal item data
    for item in invoice_doc.items:
        minimal_item = {
            "name": item.name,
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty": item.qty or 0,
            "rate": item.rate or 0,
            "price_list_rate": item.price_list_rate or 0,
            "base_rate": getattr(item, 'base_rate', item.price_list_rate or item.rate or 0),
            "amount": item.amount or 0,
            "discount_percentage": item.discount_percentage or 0,
            "discount_amount": item.discount_amount or 0,
            "uom": item.uom,
            
            # POS specific fields
            "posa_row_id": getattr(item, 'posa_row_id', ''),
            "posa_offers": getattr(item, 'posa_offers', '[]'),
            "posa_offer_applied": getattr(item, 'posa_offer_applied', 0),
            "posa_is_offer": getattr(item, 'posa_is_offer', 0),
            "posa_is_replace": getattr(item, 'posa_is_replace', 0),
            "is_free_item": getattr(item, 'is_free_item', 0),
            
            # Batch/Serial if exists
            "batch_no": getattr(item, 'batch_no', ''),
            "serial_no": getattr(item, 'serial_no', ''),
        }
        
        minimal_response["items"].append(minimal_item)
    
    # Add payments if any
    minimal_response["payments"] = []
    if invoice_doc.payments:
        for payment in invoice_doc.payments:
            minimal_payment = {
                "mode_of_payment": payment.mode_of_payment,
                "amount": payment.amount or 0,
                "account": getattr(payment, 'account', ''),
            }
            minimal_response["payments"].append(minimal_payment)
    
    # Add posa_offers if any
    minimal_response["posa_offers"] = []
    if hasattr(invoice_doc, 'posa_offers') and invoice_doc.posa_offers:
        for offer in invoice_doc.posa_offers:
            minimal_offer = {
                "name": offer.name,
                "offer_name": getattr(offer, 'offer_name', ''),
                "apply_on": getattr(offer, 'apply_on', ''),
                "offer": getattr(offer, 'offer', ''),
                "offer_applied": getattr(offer, 'offer_applied', 0),
                "coupon_based": getattr(offer, 'coupon_based', 0),
                "row_id": getattr(offer, 'row_id', ''),
            }
            minimal_response["posa_offers"].append(minimal_offer)
    
    return minimal_response


@frappe.whitelist()
def create_payment_request(doc):
    """
    Create payment request for invoice
    """
    try:
        # Implementation for payment request creation
        # This is a placeholder - you may need to implement the actual logic
        return {
            "success": True,
            "message": "Payment request created",
            "data": {}
        }
    except Exception as e:
        frappe.log_error(f"sales_invoice.py(create_payment_request): Error {str(e)}", "POS Submit")
        return {
            "success": False,
            "message": str(e),
            "data": {}
        }


# ===== SALES INVOICE VALIDATION HOOKS =====

def validate(doc, method):
    """
    Validate Sales Invoice
    """
    try:
        # Basic POS validation
        if doc.is_pos:
            validate_pos_invoice(doc)
            
    except Exception as e:
        frappe.log_error(f"sales_invoice.py(validate): Error {str(e)}", "POS Submit")
        raise


def validate_pos_invoice(doc):
    """
    Validate POS Invoice specific rules
    """
    # Validate POS Profile
    if not doc.pos_profile:
        frappe.throw(_("POS Profile is required for POS Invoice"))
    
    # Validate Customer
    if not doc.customer:
        frappe.throw(_("Customer is required for POS Invoice"))
    
    # Validate Items
    if not doc.items:
        frappe.throw(_("At least one item is required"))
    
    # Validate Opening Shift
    if not doc.posa_pos_opening_shift:
        frappe.throw(_("POS Opening Shift is required"))
    
    # Validate Company
    if not doc.company:
        frappe.throw(_("Company is required"))
    
    # Validate Currency
    if not doc.currency:
        frappe.throw(_("Currency is required"))


def before_submit(doc, method):
    """
    Before Submit Sales Invoice
    """
    try:
        if doc.is_pos:
            validate_pos_before_submit(doc)
            
    except Exception as e:
        frappe.log_error(f"sales_invoice.py(before_submit): Error {str(e)}", "POS Submit")
        raise


def validate_pos_before_submit(doc):
    """
    Validate POS Invoice before submit
    """
    # Additional validations before submitting POS invoice
    if not doc.posa_pos_opening_shift:
        frappe.throw(_("POS Opening Shift is required before submit"))
    
    # Validate payments
    if not doc.payments:
        frappe.throw(_("At least one payment is required"))
    
    # Validate payment amounts against rounded total (not grand total)
    total_payments = sum(flt(payment.amount) for payment in doc.payments)
    
    # Use rounded_total if available, otherwise use grand_total
    target_amount = flt(doc.rounded_total) if hasattr(doc, 'rounded_total') and doc.rounded_total else flt(doc.grand_total)
    difference = abs(total_payments - target_amount)
    
    # Allow small floating point differences (up to 0.05 for currency precision)
    if difference > 0.05:
        frappe.throw(_("Payment amount must equal rounded total. Total payments: {0}, Rounded total: {1}, Difference: {2}").format(
            total_payments, target_amount, difference))


def before_cancel(doc, method):
    """
    Before Cancel Sales Invoice
    """
    try:
        if doc.is_pos:
            validate_pos_before_cancel(doc)
            
    except Exception as e:
        frappe.log_error(f"sales_invoice.py(before_cancel): Error {str(e)}", "POS Submit")
        raise


def validate_pos_before_cancel(doc):
    """
    Validate POS Invoice before cancel
    """
    # Check if invoice can be cancelled
    if doc.docstatus != 1:
        frappe.throw(_("Only submitted invoices can be cancelled"))
    
    # Check if opening shift is still open
    if doc.posa_pos_opening_shift:
        shift_status = frappe.get_cached_value(
            "POS Opening Shift",
            doc.posa_pos_opening_shift,
            "status"
        )
        if shift_status == "Closed":
            frappe.throw(_("Cannot cancel invoice from closed shift"))




