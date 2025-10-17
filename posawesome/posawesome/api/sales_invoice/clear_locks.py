# -*- coding: utf-8 -*-
"""
Clear Redis Locks Utility
Handles clearing stale Redis locks for POS operations
"""

from __future__ import unicode_literals

import frappe
from frappe import _


@frappe.whitelist()
def clear_stale_invoice_locks():
    """
    Clear all stale invoice locks from Redis cache
    This is useful when locks get stuck due to unexpected errors
    """
    try:
        # Get all cache keys
        cache_keys = frappe.cache().get_keys("update_invoice_*")
        cleared_count = 0
        
        for key in cache_keys:
            try:
                frappe.cache().delete_value(key)
                cleared_count += 1
            except:
                continue
        
        frappe.logger().info(f"Cleared {cleared_count} stale invoice locks")
        return {"success": True, "cleared_count": cleared_count}
        
    except Exception as e:
        frappe.logger().error(f"Error clearing stale locks: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist() 
def clear_specific_invoice_lock(invoice_name):
    """
    Clear lock for a specific invoice
    """
    try:
        if not invoice_name:
            return {"success": False, "error": "Invoice name required"}
            
        lock_key = f"update_invoice_{invoice_name}"
        frappe.cache().delete_value(lock_key)
        
        return {"success": True, "message": f"Lock cleared for invoice {invoice_name}"}
        
    except Exception as e:
        frappe.logger().error(f"Error clearing invoice lock: {str(e)}")
        return {"success": False, "error": str(e)}