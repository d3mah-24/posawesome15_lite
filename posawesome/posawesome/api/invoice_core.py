# -*- coding: utf-8 -*-
"""
POS Core Invoice Management API

This module handles core invoice operations:
- Create new invoices
- Update invoice data
- Submit invoices
- Delete invoices
- Invoice validation
"""

from __future__ import unicode_literals

import json

import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()  # type: ignore
def create_invoice(customer, pos_profile, pos_opening_shift):
    """
    POST - Create new invoice
    """
    doc = frappe.new_doc("Sales Invoice")
    doc.customer = customer
    doc.pos_profile = pos_profile
    doc.posa_pos_opening_shift = pos_opening_shift
    doc.is_pos = 1
    doc.save()
    return doc.as_dict()


@frappe.whitelist()  # type: ignore
def get_invoice(invoice_name):
    """
    GET - Get invoice with all data
    """
    if not invoice_name:
        return None

    doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
    return doc.as_dict()


@frappe.whitelist()  # type: ignore
def update_invoice(data):
    """
    PUT - Update invoice data
    Let ERPNext handle all calculations through set_missing_values() and save()
    """
    data = json.loads(data)

    if data.get("name"):
        try:
            invoice_doc = frappe.get_doc("Sales Invoice", data.get("name"))  # type: ignore
            invoice_doc.update(data)
        except frappe.DoesNotExistError:
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
    invoice_doc.save()

    # Return ERPNext calculated data as-is
    return invoice_doc.as_dict()


@frappe.whitelist()  # type: ignore
def submit_invoice_simple(invoice_name):
    """
    POST - Submit invoice (simple version)
    """
    doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
    doc.submit()
    return doc.as_dict()


@frappe.whitelist()  # type: ignore
def delete_invoice(invoice_name):
    """
    DELETE - Delete invoice
    """
    frappe.delete_doc("Sales Invoice", invoice_name)
    return {"message": "Invoice deleted successfully"}


@frappe.whitelist()  # type: ignore
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
        frappe.log_error(f"Error getting draft invoices: {str(e)}")
        return []


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
        
        return {"valid": True, "message": "Return items are valid"}
        
    except Exception as e:
        return {
            "valid": False,
            "message": f"Error validating return items: {str(e)}"
        }
