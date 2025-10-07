# -*- coding: utf-8 -*-
"""
Calculate Batch Quantities API
"""

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils import flt

from erpnext.stock.doctype.batch.batch import (
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
