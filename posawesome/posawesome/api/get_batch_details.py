# -*- coding: utf-8 -*-
"""
Get Batch Details API
"""

from __future__ import unicode_literals

import frappe


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
