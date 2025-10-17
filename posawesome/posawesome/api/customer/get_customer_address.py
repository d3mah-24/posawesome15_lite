# -*- coding: utf-8 -*-
"""
Get Customer Address API
Handles retrieving single customer address
"""

from __future__ import unicode_literals

import frappe
from frappe import _


@frappe.whitelist()
def get_customer_address(name):
    """
    Get a single customer address by name.
    
    Args:
        name (str): Address name/ID
        
    Returns:
        dict: Address document
    """
    try:
        if not name:
            frappe.throw(_("Address name is required"))
            
        address = frappe.get_doc("Address", name)
        
        if not address:
            frappe.throw(_("Address not found"))
            
        return address.as_dict()
        
    except Exception as e:
        frappe.logger().error(f"Error in get_customer_address: {str(e)}")
        frappe.throw(_("Error retrieving address: {0}").format(str(e)))