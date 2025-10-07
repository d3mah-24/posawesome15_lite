# -*- coding: utf-8 -*-
"""
Select Optimal Batch API
"""

from __future__ import unicode_literals

import json

import frappe


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
