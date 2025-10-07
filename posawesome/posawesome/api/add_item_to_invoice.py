# -*- coding: utf-8 -*-
"""
Add Item To Invoice API
"""

from __future__ import unicode_literals

import frappe
from frappe.exceptions import TimestampMismatchError
from frappe.utils import flt


@frappe.whitelist()  # type: ignore
def add_item_to_invoice(invoice_name, item_code, qty, rate, uom):
    """POST - Add item to invoice immediately (no delay)."""
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
        doc.append("items", {
            "item_code": item_code,
            "qty": flt(qty),
            "rate": flt(rate),
            "uom": uom
        })

        # Skip optimistic locking because POS frequently edits the same draft
        doc.flags.ignore_version = True

        doc.save()

        return doc.as_dict()
    except TimestampMismatchError as e:
        frappe.throw(f"Error adding item: {str(e)}")
    except Exception as e:
        frappe.throw(f"Error adding item: {str(e)}")


def add_item_to_invoice_queued(invoice_name, item_code, qty, rate, uom):
    """
    POST - Add item to invoice (queued version)
    """
    # Use queue to ensure sequential execution
    frappe.enqueue(
        method="posawesome.posawesome.api.add_item_to_invoice.add_item_to_invoice",
        queue="short",
        timeout=300,
        invoice_name=invoice_name,
        item_code=item_code,
        qty=qty,
        rate=rate,
        uom=uom
    )
    
    return {"status": "queued", "message": "Item addition queued successfully"}

