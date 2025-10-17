# -*- coding: utf-8 -*-
"""
Create Invoice Function - ERPNext Natural Operations
Handles new invoice creation using ERPNext's standard patterns
"""

from __future__ import unicode_literals

import json
import frappe
from frappe import _


@frappe.whitelist()
def add_item_to_invoice(item_code, qty=1, customer=None, pos_profile=None):
    """
    Smart item addition - prevents creating 1000 invoices when clicking item 1000 times!
    1. Finds existing draft invoice for current user
    2. If item exists: increment quantity 
    3. If item doesn't exist: add new item
    4. If no draft: create new invoice
    """
    try:
        if not item_code:
            frappe.throw(_("Item code is required"))
        
        qty = float(qty) if qty else 1.0
        
        # Find existing draft
        existing_draft = _find_existing_draft(customer, pos_profile)
        
        if existing_draft:
            return _add_item_to_existing_invoice(existing_draft, item_code, qty)
        else:
            return _create_new_invoice_with_item(item_code, qty, customer, pos_profile)
            
    except Exception as e:
        frappe.log_error(f"Add item error: {str(e)[:100]}", "Add Item Error")
        raise


@frappe.whitelist()
def create_invoice(data, force_new=False):
    """
    POST - Create new invoice using ERPNext's natural operations
    
    Args:
        data: Invoice data
        force_new: If True, always create new invoice (ignore existing drafts)
    
    Smart Logic:
    - If force_new=False: Check for existing draft and add items to it
    - If force_new=True: Always create new invoice
    - Prevents creating 1000 invoices when adding items rapidly
    """
    try:
        # Parse input data
        data = json.loads(data) if isinstance(data, str) else data
    except (json.JSONDecodeError, ValueError) as e:
        frappe.throw(_("Invalid JSON data: {0}").format(str(e)))

    try:
        # Validate input
        if data.get("name"):
            frappe.throw(_("Use update_invoice for existing invoices"))

        # Smart invoice creation - check for existing draft unless forced
        if not force_new:
            existing_draft = _find_existing_draft(data.get("customer"), data.get("pos_profile"))
            if existing_draft:
                # Add items to existing draft instead of creating new invoice
                return _merge_items_to_existing_draft(existing_draft, data)

        # Create new invoice
        if not data.get("items"):
            frappe.throw(_("Cannot create invoice without items"))

        doc = frappe.new_doc("Sales Invoice")
        doc.update(data)
        
        doc.set_missing_values() 
        doc.save(ignore_version=True)  # Optimized save for better concurrency
        frappe.db.commit()             # Immediate commit for lock release
        
        from .invoice_response import get_minimal_invoice_response
        return get_minimal_invoice_response(doc)
        
    except Exception as e:
        frappe.log_error(f"Error in create_invoice: {str(e)}")
        raise


def _find_existing_draft(customer=None, pos_profile=None):
    """
    Find existing draft invoice for current user to prevent creating duplicates.
    """
    try:
        filters = {
            "docstatus": 0,  # Draft only
            "owner": frappe.session.user,
        }
        
        if customer:
            filters["customer"] = customer
        if pos_profile:
            filters["pos_profile"] = pos_profile
            
        draft_invoices = frappe.get_all(
            "Sales Invoice",
            filters=filters,
            fields=["name"],
            order_by="creation desc",
            limit=1
        )
        
        return draft_invoices[0].name if draft_invoices else None
        
    except Exception:
        return None


def _merge_items_to_existing_draft(invoice_name, new_data):
    """
    Merge items from new data into existing draft invoice using direct database operations.
    This completely bypasses ERPNext's timestamp validation for auto-clicker scenarios.
    """
    try:
        # Get the item to add
        new_item = new_data.get("items", [{}])[0]
        item_code = new_item.get("item_code")
        new_qty = float(new_item.get("qty", 1))
        
        if not item_code:
            frappe.throw(_("Item code is required"))
        
        # Use atomic database operations with locking
        frappe.db.sql("START TRANSACTION")
        
        # Lock the invoice
        frappe.db.sql("""
            SELECT name FROM `tabSales Invoice` 
            WHERE name = %s FOR UPDATE
        """, (invoice_name,))
        
        # Check if item already exists in this invoice
        existing_item = frappe.db.sql("""
            SELECT name, qty FROM `tabSales Invoice Item`
            WHERE parent = %s AND item_code = %s
        """, (invoice_name, item_code), as_dict=True)
        
        if existing_item:
            # Item exists - increment quantity directly in database
            new_total_qty = existing_item[0].qty + new_qty
            frappe.db.sql("""
                UPDATE `tabSales Invoice Item`
                SET qty = %s, amount = rate * %s, 
                    modified = NOW(), modified_by = %s
                WHERE name = %s
            """, (new_total_qty, new_total_qty, frappe.session.user, existing_item[0].name))
            
            frappe.log_error(f"DB Direct: Incremented {item_code} qty to {new_total_qty}", "Item DB Increment")
        else:
            # Item doesn't exist - add new item directly to database
            from frappe.model.naming import make_autoname
            
            # Get item details
            item_doc = frappe.get_doc("Item", item_code)
            
            # Generate unique name for the item row
            item_row_name = make_autoname("hash", "Sales Invoice Item")
            
            # Insert new item row directly
            frappe.db.sql("""
                INSERT INTO `tabSales Invoice Item` 
                (name, parent, parenttype, parentfield, item_code, item_name, qty, rate, amount, uom, idx, 
                 creation, modified, owner, modified_by, docstatus)
                VALUES (%s, %s, 'Sales Invoice', 'items', %s, %s, %s, %s, %s, %s, 
                        (SELECT COALESCE(MAX(idx), 0) + 1 FROM `tabSales Invoice Item` si WHERE si.parent = %s),
                        NOW(), NOW(), %s, %s, 0)
            """, (item_row_name, invoice_name, item_code, item_doc.item_name, new_qty, 
                  item_doc.standard_rate or 0, (item_doc.standard_rate or 0) * new_qty, 
                  item_doc.stock_uom, invoice_name, frappe.session.user, frappe.session.user))
            
            frappe.log_error(f"DB Direct: Added new item {item_code} with qty {new_qty}", "Item DB Add")
        
        # Update the main invoice's modified timestamp
        frappe.db.sql("""
            UPDATE `tabSales Invoice`
            SET modified = NOW(), modified_by = %s
            WHERE name = %s
        """, (frappe.session.user, invoice_name))
        
        # Commit the transaction
        frappe.db.sql("COMMIT")
        
        # Return updated invoice data
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        from .invoice_response import get_minimal_invoice_response
        return get_minimal_invoice_response(doc)
        
    except Exception as e:
        frappe.db.sql("ROLLBACK")
        frappe.log_error(f"DB merge error: {str(e)[:100]}", "DB Merge Error")
        frappe.throw(_("Could not merge items. Please try again."))


def _add_item_to_existing_invoice(invoice_name, item_code, qty):
    """
    Add item to existing invoice. If item exists, increment quantity.
    Uses database locking for auto-clicker scenarios.
    """
    try:
        # Database lock to prevent race conditions during rapid item addition
        frappe.db.sql("""
            SELECT name FROM `tabSales Invoice` 
            WHERE name = %s FOR UPDATE
        """, (invoice_name,))
        
        # Get fresh document after acquiring lock
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        
        # Check if item already exists
        existing_item = None
        for item in doc.items:
            if item.item_code == item_code:
                existing_item = item
                break
        
        if existing_item:
            # Item exists - increment quantity
            existing_item.qty += qty
            frappe.log_error(f"Incremented {item_code} qty to {existing_item.qty}", "Item Increment")
        else:
            # Item doesn't exist - add new item row
            item_doc = frappe.get_doc("Item", item_code)
            
            doc.append("items", {
                "item_code": item_code,
                "item_name": item_doc.item_name,
                "qty": qty,
                "uom": item_doc.stock_uom,
                "rate": item_doc.standard_rate or 0,
            })
            frappe.log_error(f"Added new item {item_code} with qty {qty}", "Item Add")
        
        doc.save(ignore_version=True)
        frappe.db.commit()  # Release lock immediately
        
        from .invoice_response import get_minimal_invoice_response
        return get_minimal_invoice_response(doc)
        
    except Exception as e:
        frappe.db.rollback()  # Release lock on error
        frappe.log_error(f"Add to existing error: {str(e)[:100]}", "Add To Existing Error")
        raise


def _create_new_invoice_with_item(item_code, qty, customer=None, pos_profile=None):
    """
    Create new invoice with specified item.
    """
    try:
        item_doc = frappe.get_doc("Item", item_code)
        
        doc = frappe.new_doc("Sales Invoice")
        
        if customer:
            doc.customer = customer
        if pos_profile:
            doc.pos_profile = pos_profile
            
        doc.append("items", {
            "item_code": item_code,
            "item_name": item_doc.item_name,
            "qty": qty,
            "uom": item_doc.stock_uom,
            "rate": item_doc.standard_rate or 0,
        })
        
        doc.set_missing_values()
        doc.save(ignore_version=True)
        frappe.db.commit()
        
        frappe.log_error(f"Created new invoice {doc.name} with item {item_code}", "New Invoice Created")
        
        from .invoice_response import get_minimal_invoice_response
        return get_minimal_invoice_response(doc)
        
    except Exception as e:
        frappe.log_error(f"Create new with item error: {str(e)[:100]}", "Create New With Item Error")
        raise