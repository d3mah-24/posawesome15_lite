# -*- coding: utf-8 -*-
"""
Update Item In Invoice API
"""

from __future__ import unicode_literals

import time
import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()  # type: ignore
def update_item_in_invoice(
    invoice_name, item_idx, qty=None, rate=None, discount_percentage=None
):
    """
    PUT - Update item in invoice with sequential execution
    """
    # Execute with delay but return document data
    return _update_item_in_invoice_with_delay(invoice_name, item_idx, qty, rate, discount_percentage, delay_seconds=0.3)


def update_item_in_invoice_sequential(
    invoice_name, item_idx, qty=None, rate=None, discount_percentage=None
):
    """
    PUT - Update item in invoice with sequential execution and delays
    """
    # Use queue with sequential processing
    frappe.enqueue(
        method="posawesome.posawesome.api.update_item_in_invoice._update_item_in_invoice_with_delay",
        queue="short",
        timeout=300,
        invoice_name=invoice_name,
        item_idx=item_idx,
        qty=qty,
        rate=rate,
        discount_percentage=discount_percentage,
        delay_seconds=0.5  # نصف ثانية تأخير
    )
    
    return {"status": "queued", "message": "Item update queued with sequential processing"}


def _update_item_in_invoice_with_delay(
    invoice_name, item_idx, qty=None, rate=None, discount_percentage=None, delay_seconds=0.5
):
    """
    Synchronous method to update item in invoice with delay
    """
    try:
        # Add delay to prevent concurrent modifications
        time.sleep(delay_seconds)
        
        # Get document with reload to ensure latest version
        doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
        doc.reload()
        
        # Convert item_idx to integer since it comes as string from frontend
        item_idx = int(item_idx)

        if item_idx < 0 or item_idx >= len(doc.items):
            frappe.throw(_("Invalid item index: {0}").format(item_idx))

        item = doc.items[item_idx]

        if qty is not None:
            item.qty = flt(qty)
        if rate is not None:
            item.rate = flt(rate)
        if discount_percentage is not None:
            item.discount_percentage = flt(discount_percentage)

        doc.flags.ignore_version = True

        # Save with additional delay
        doc.save()
        time.sleep(0.1)  # Reduced delay after save
        
        # Log success
        frappe.logger().info(f"Successfully updated item {item_idx} in invoice {invoice_name} with delay {delay_seconds}s")
        
        return doc.as_dict()
    except ValueError:
        frappe.throw(_("Invalid item index format"))
    except Exception as e:
        # Log error
        frappe.logger().error(f"Error updating item {item_idx} in invoice {invoice_name}: {str(e)}")
        frappe.throw(_("Error updating item: {0}").format(str(e)))


def update_item_in_invoice_direct(
    invoice_name, item_idx, qty=None, rate=None, discount_percentage=None
):
    """
    PUT - Update item in invoice (direct execution without queue)
    """
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
        # Convert item_idx to integer since it comes as string from frontend
        item_idx = int(item_idx)

        if item_idx < 0 or item_idx >= len(doc.items):
            frappe.throw(_("Invalid item index: {0}").format(item_idx))

        item = doc.items[item_idx]

        if qty is not None:
            item.qty = flt(qty)
        if rate is not None:
            item.rate = flt(rate)
        if discount_percentage is not None:
            item.discount_percentage = flt(discount_percentage)

        doc.flags.ignore_version = True

        doc.save()
        
        # Log success
        frappe.logger().info(f"Successfully updated item {item_idx} in invoice {invoice_name} (direct)")
        
        return doc.as_dict()
    except ValueError:
        frappe.throw(_("Invalid item index format"))
    except Exception as e:
        # Log error
        frappe.logger().error(f"Error updating item {item_idx} in invoice {invoice_name}: {str(e)}")
        frappe.throw(_("Error updating item: {0}").format(str(e)))


def update_item_in_invoice_queued(
    invoice_name, item_idx, qty=None, rate=None, discount_percentage=None
):
    """
    PUT - Update item in invoice (queued version)
    """
    # Use queue to ensure sequential execution
    frappe.enqueue(
        method="posawesome.posawesome.api.update_item_in_invoice._update_item_in_invoice_sync",
        queue="short",
        timeout=300,
        invoice_name=invoice_name,
        item_idx=item_idx,
        qty=qty,
        rate=rate,
        discount_percentage=discount_percentage
    )
    
    return {"status": "queued", "message": "Item update queued successfully"}


def _update_item_in_invoice_sync(
    invoice_name, item_idx, qty=None, rate=None, discount_percentage=None
):
    """
    Synchronous method to update item in invoice
    """
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
        # Convert item_idx to integer since it comes as string from frontend
        item_idx = int(item_idx)

        if item_idx < 0 or item_idx >= len(doc.items):
            frappe.throw(_("Invalid item index: {0}").format(item_idx))

        item = doc.items[item_idx]

        if qty is not None:
            item.qty = flt(qty)
        if rate is not None:
            item.rate = flt(rate)
        if discount_percentage is not None:
            item.discount_percentage = flt(discount_percentage)

        doc.flags.ignore_version = True

        doc.save()
        
        # Log success
        frappe.logger().info(f"Successfully updated item {item_idx} in invoice {invoice_name}")
        
        return doc.as_dict()
    except ValueError:
        frappe.throw(_("Invalid item index format"))
    except Exception as e:
        # Log error
        frappe.logger().error(f"Error updating item {item_idx} in invoice {invoice_name}: {str(e)}")
        frappe.throw(_("Error updating item: {0}").format(str(e)))
