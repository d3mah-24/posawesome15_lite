# -*- coding: utf-8 -*-
"""
Update Customer Address API
Handles updating customer addresses
"""

from __future__ import unicode_literals

import frappe
from frappe import _


@frappe.whitelist()
def update_customer_address(address_id, args):
    """
    Update an existing customer address.
    
    Args:
        address_id (str): Address ID to update
        args (str): JSON string containing address details to update
        
    Returns:
        dict: Updated address document
    """
    try:
        import json
        args = json.loads(args) if isinstance(args, str) else args
        
        if not address_id:
            frappe.throw(_("Address ID is required"))
            
        if not frappe.db.exists("Address", address_id):
            frappe.throw(_("Address not found"))
            
        address = frappe.get_doc("Address", address_id)
        
        # Update fields if provided
        if args.get("address_title"):
            address.address_title = args.get("address_title")
        if args.get("address_line1"):
            address.address_line1 = args.get("address_line1")
        if args.get("address_line2") is not None:
            address.address_line2 = args.get("address_line2")
        if args.get("city"):
            address.city = args.get("city")
        if args.get("state"):
            address.state = args.get("state")
        if args.get("pincode"):
            address.pincode = args.get("pincode")
        if args.get("country"):
            address.country = args.get("country")
        if args.get("address_type"):
            address.address_type = args.get("address_type")
        if args.get("phone") is not None:
            address.phone = args.get("phone")
        if args.get("email_id") is not None:
            address.email_id = args.get("email_id")
            
        address.save()
        
        return address.as_dict()
        
    except Exception as e:
        frappe.logger().error(f"Error in update_customer_address: {str(e)}")
        frappe.throw(_("Error updating address: {0}").format(str(e)))