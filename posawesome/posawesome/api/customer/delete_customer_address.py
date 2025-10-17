# -*- coding: utf-8 -*-
"""
Delete Customer Address API
Handles deleting customer addresses
"""

from __future__ import unicode_literals

import frappe
from frappe import _


@frappe.whitelist()
def delete_customer_address(address_id):
    """
    Delete a customer address.
    
    Args:
        address_id (str): Address ID to delete
        
    Returns:
        dict: Success message
    """
    try:
        if not address_id:
            frappe.throw(_("Address ID is required"))
            
        if not frappe.db.exists("Address", address_id):
            frappe.throw(_("Address not found"))
            
        frappe.delete_doc("Address", address_id)
        
        return {"message": _("Address deleted successfully")}
        
    except Exception as e:
        frappe.logger().error(f"Error in delete_customer_address: {str(e)}")
        frappe.throw(_("Error deleting address: {0}").format(str(e)))