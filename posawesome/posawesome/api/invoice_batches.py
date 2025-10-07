# -*- coding: utf-8 -*-
"""
POS Invoice Batch Management API

This module handles all batch-related operations for POS invoices:
- Batch selection and validation
- Batch quantity calculations
- Optimal batch selection
"""

from __future__ import unicode_literals

import json

import frappe
from frappe import _
from frappe.utils import flt

from erpnext.stock.doctype.batch.batch import (
    get_batch_no,
    get_batch_qty,
)


@frappe.whitelist()  # type: ignore
def calculate_batch_quantities(
    item_code, warehouse, qty, uom=None, conversion_factor=1
):
    """
    Calculate available batch quantities for an item
    """
    try:
        if isinstance(qty, str):
            qty = flt(qty)
        if isinstance(conversion_factor, str):
            conversion_factor = flt(conversion_factor)
        
        # Get all batches for the item in the warehouse
        batches = frappe.get_all(
            "Batch",
            filters={"item": item_code},
            fields=["name", "batch_id", "expiry_date"]
        )
        
        batch_data = []
        
        for batch in batches:
            # Get available quantity for this batch
            available_qty = get_batch_qty(batch.name, warehouse)
            
            if available_qty > 0:
                batch_data.append({
                    "batch_no": batch.name,
                    "batch_id": batch.batch_id,
                    "available_qty": available_qty,
                    "expiry_date": batch.expiry_date,
                    "conversion_factor": conversion_factor
                })
        
        # Sort by expiry date (FIFO)
        batch_data.sort(key=lambda x: x.get("expiry_date") or "9999-12-31")
        
        return batch_data
        
    except Exception as e:
        frappe.throw(_("Error calculating batch quantities: {0}").format(str(e)))


@frappe.whitelist()  # type: ignore
def select_optimal_batch(batch_data, preferred_batch_no=None):
    """
    Select the optimal batch for an item based on FIFO/LIFO rules
    """
    try:
        if isinstance(batch_data, str):
            batch_data = json.loads(batch_data)
        
        if not batch_data:
            return None
        
        # If preferred batch is specified, try to use it
        if preferred_batch_no:
            for batch in batch_data:
                if batch["batch_no"] == preferred_batch_no:
                    return batch
        
        # Otherwise, use FIFO (first batch with available quantity)
        for batch in batch_data:
            if batch["available_qty"] > 0:
                return batch
        
        return None
        
    except Exception as e:
        frappe.log_error(f"Error selecting optimal batch: {str(e)}")
        return None


@frappe.whitelist()  # type: ignore
def process_batch_selection(
    invoice_name, item_code, qty, warehouse, uom=None, conversion_factor=1
):
    """
    Process batch selection for an item in an invoice
    """
    try:
        if isinstance(qty, str):
            qty = flt(qty)
        if isinstance(conversion_factor, str):
            conversion_factor = flt(conversion_factor)
        
        # Calculate required quantity in stock UOM
        required_qty = qty * conversion_factor
        
        # Get available batches
        batch_data = calculate_batch_quantities(
            item_code, warehouse, required_qty, uom, conversion_factor
        )
        
        if not batch_data:
            return {
                "success": False,
                "message": f"No batches available for item {item_code}",
                "batches": []
            }
        
        # Select optimal batch
        selected_batch = select_optimal_batch(batch_data)
        
        if not selected_batch:
            return {
                "success": False,
                "message": f"No suitable batch found for item {item_code}",
                "batches": batch_data
            }
        
        # Check if selected batch has enough quantity
        if selected_batch["available_qty"] < required_qty:
            return {
                "success": False,
                "message": f"Insufficient quantity in batch {selected_batch['batch_no']}",
                "batches": batch_data,
                "selected_batch": selected_batch
            }
        
        return {
            "success": True,
            "message": "Batch selected successfully",
            "selected_batch": selected_batch,
            "batches": batch_data
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing batch selection: {str(e)}",
            "batches": []
        }


@frappe.whitelist()  # type: ignore
def validate_batch_availability(item_code, batch_no, warehouse, qty):
    """
    Validate if a batch has sufficient quantity
    """
    try:
        if isinstance(qty, str):
            qty = flt(qty)
        
        available_qty = get_batch_qty(batch_no, warehouse)
        
        if available_qty < qty:
            return {
                "valid": False,
                "message": f"Insufficient quantity in batch {batch_no}. Available: {available_qty}, Required: {qty}",
                "available_qty": available_qty,
                "required_qty": qty
            }
        
        return {
            "valid": True,
            "message": "Batch has sufficient quantity",
            "available_qty": available_qty,
            "required_qty": qty
        }
        
    except Exception as e:
        return {
            "valid": False,
            "message": f"Error validating batch: {str(e)}",
            "available_qty": 0,
            "required_qty": qty
        }


@frappe.whitelist()  # type: ignore
def get_batch_details(batch_no):
    """
    Get detailed information about a batch
    """
    try:
        batch_doc = frappe.get_doc("Batch", batch_no)
        
        return {
            "batch_no": batch_doc.name,
            "batch_id": batch_doc.batch_id,
            "item": batch_doc.item,
            "expiry_date": batch_doc.expiry_date,
            "manufacturing_date": batch_doc.manufacturing_date,
            "supplier": batch_doc.supplier,
            "reference_doctype": batch_doc.reference_doctype,
            "reference_name": batch_doc.reference_name
        }
        
    except frappe.DoesNotExistError:
        return {
            "error": f"Batch {batch_no} does not exist"
        }
    except Exception as e:
        return {
            "error": f"Error getting batch details: {str(e)}"
        }

