# -*- coding: utf-8 -*-
"""
Customer Addresses Functions
Handles customer addresses operations
"""

from __future__ import unicode_literals

import json
import frappe
from frappe import _


@frappe.whitelist()
def get_customer_addresses(customer):
    """
    Get customer addresses using Frappe ORM
    """
    if not customer:
        frappe.throw(_("Customer parameter is required"))
    
    try:
        # First get the address names linked to this customer
        dynamic_links = frappe.get_all(
            "Dynamic Link",
            filters={
                "link_doctype": "Customer",
                "link_name": customer
            },
            fields=["parent"]
        )
        
        # Extract address names
        address_names = [link.parent for link in dynamic_links]
        
        if not address_names:
            return []
        
        # Get the actual address details
        addresses = frappe.get_all(
            "Address",
            filters={
                "name": ["in", address_names],
                "disabled": 0
            },
            fields=[
                "name",
                "address_line1", 
                "address_line2",
                "address_title",
                "city",
                "state", 
                "country",
                "address_type"
            ],
            order_by="name"
        )
        
        return addresses
        
    except Exception as e:
        return []


@frappe.whitelist()
def make_address(args):
    args = json.loads(args)
    address = frappe.get_doc(
        {
            "doctype": "Address",
            "address_title": args.get("name"),
            "address_line1": args.get("address_line1"),
            "address_line2": args.get("address_line2"),
            "city": args.get("city"),
            "state": args.get("state"),
            "pincode": args.get("pincode"),
            "country": args.get("country"),
            "address_type": "Shipping",
            "links": [
                {"link_doctype": args.get("doctype"), "link_name": args.get("customer")}
            ],
        }
    ).insert()

    return address
