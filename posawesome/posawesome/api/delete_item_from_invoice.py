# -*- coding: utf-8 -*-
"""
Delete Item From Invoice API
"""

from __future__ import unicode_literals

import time
import frappe
from frappe import _


@frappe.whitelist()  # type: ignore
def delete_item_from_invoice(invoice_name, item_idx):
    """
    DELETE - Remove item from invoice with sequential execution
    """
    # Execute with delay but return document data
    return _delete_item_from_invoice_with_delay(invoice_name, item_idx, delay_seconds=0.3)


def delete_item_from_invoice_sequential(invoice_name, item_idx):
    """
    DELETE - Remove item from invoice with sequential execution and delays
    """
    # Use queue with sequential processing
    frappe.enqueue(
        method="posawesome.posawesome.api.delete_item_from_invoice._delete_item_from_invoice_with_delay",
        queue="short",
        timeout=300,
        invoice_name=invoice_name,
        item_idx=item_idx,
        delay_seconds=0.5  # نصف ثانية تأخير
    )
    
    return {"status": "queued", "message": "Item deletion queued with sequential processing"}


def _delete_item_from_invoice_with_delay(invoice_name, item_idx, delay_seconds=0.5):
    """
    Synchronous method to delete item from invoice with delay
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

        doc.items.pop(item_idx)
        
        # Save with additional delay
        doc.save()
        time.sleep(0.1)  # Reduced delay after save
        
        # Log success
        frappe.logger().info(f"Successfully deleted item {item_idx} from invoice {invoice_name} with delay {delay_seconds}s")
        
        return doc.as_dict()
    except ValueError:
        frappe.throw(_("Invalid item index format"))
    except Exception as e:
        # Log error
        frappe.logger().error(f"Error deleting item {item_idx} from invoice {invoice_name}: {str(e)}")
        frappe.throw(_("Error deleting item: {0}").format(str(e)))


def delete_item_from_invoice_direct(invoice_name, item_idx):
    """
    DELETE - Remove item from invoice (direct execution without queue)
    """
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
        # Convert item_idx to integer since it comes as string from frontend
        item_idx = int(item_idx)

        if item_idx < 0 or item_idx >= len(doc.items):
            frappe.throw(_("Invalid item index: {0}").format(item_idx))

        doc.items.pop(item_idx)
        doc.save()
        
        # Log success
        frappe.logger().info(f"Successfully deleted item {item_idx} from invoice {invoice_name} (direct)")
        
        return doc.as_dict()
    except ValueError:
        frappe.throw(_("Invalid item index format"))
    except Exception as e:
        # Log error
        frappe.logger().error(f"Error deleting item {item_idx} from invoice {invoice_name}: {str(e)}")
        frappe.throw(_("Error deleting item: {0}").format(str(e)))


def delete_item_from_invoice_queued(invoice_name, item_idx):
    """
    DELETE - Remove item from invoice (queued version)
    """
    # Use queue to ensure sequential execution
    frappe.enqueue(
        method="posawesome.posawesome.api.delete_item_from_invoice._delete_item_from_invoice_sync",
        queue="short",
        timeout=300,
        invoice_name=invoice_name,
        item_idx=item_idx
    )
    
    return {"status": "queued", "message": "Item deletion queued successfully"}


def _delete_item_from_invoice_sync(invoice_name, item_idx):
    """
    Synchronous method to delete item from invoice
    """
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)  # type: ignore
        # Convert item_idx to integer since it comes as string from frontend
        item_idx = int(item_idx)

        if item_idx < 0 or item_idx >= len(doc.items):
            frappe.throw(_("Invalid item index: {0}").format(item_idx))

        doc.items.pop(item_idx)
        doc.save()
        
        # Log success
        frappe.logger().info(f"Successfully deleted item {item_idx} from invoice {invoice_name}")
        
        return doc.as_dict()
    except ValueError:
        frappe.throw(_("Invalid item index format"))
    except Exception as e:
        # Log error
        frappe.logger().error(f"Error deleting item {item_idx} from invoice {invoice_name}: {str(e)}")
        frappe.throw(_("Error deleting item: {0}").format(str(e)))
