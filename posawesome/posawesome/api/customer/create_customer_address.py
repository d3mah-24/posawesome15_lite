# -*- coding: utf-8 -*-
"""
Create Customer Address API
Handles creating new customer addresses
"""

from __future__ import unicode_literals

import frappe
from frappe import _


@frappe.whitelist()
def create_customer_address(args):
    """
    Create a new address for a customer.
    
    Args:
        args (str): JSON string containing address details
        
    Returns:
        dict: Created address document
    """
    try:
        import json
        args = json.loads(args) if isinstance(args, str) else args
        
        if not args.get("customer"):
            frappe.throw(_("Customer is required"))
            
        address = frappe.get_doc({
            "doctype": "Address",
            "address_title": args.get("name") or args.get("address_title"),
            "address_line1": args.get("address_line1"),
            "address_line2": args.get("address_line2"),
            "city": args.get("city"),
            "state": args.get("state"),
            "pincode": args.get("pincode"),
            "country": args.get("country"),
            "address_type": args.get("address_type", "Shipping"),
            "links": [{
                "link_doctype": args.get("doctype", "Customer"),
                "link_name": args.get("customer")
            }],
        }).insert()

        return address.as_dict()
        
    except Exception as e:
        frappe.logger().error(f"Error in create_customer_address: {str(e)}")
        frappe.throw(_("Error creating address: {0}").format(str(e)))