# -*- coding: utf-8 -*-
"""
Search Invoices for Return Function
Handles searching invoices for return operations
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def get_invoices_for_return(invoice_name, company):
    """
    Search invoices for return operations
    """
    frappe.logger().info(f"get_invoices_for_return called with invoice_name: '{invoice_name}', company: '{company}'")
    
    try:
        # Search for invoices that can be returned
        filters = {
            "company": company,
            "docstatus": 1,  # Only submitted invoices
            "is_return": 0,  # Not already a return
        }
        
        if invoice_name:
            filters["name"] = ["like", f"%{invoice_name}%"]
            
        frappe.logger().info(f"Searching for invoices with filters: {filters}")
        
        invoices = frappe.get_all(
            "Sales Invoice",
            filters=filters,
            fields=["name", "customer", "grand_total", "outstanding_amount", "posting_date", "currency"],
            order_by="posting_date desc",
            limit=50  # Increased limit
        )
        
        frappe.logger().info(f"Found {len(invoices)} invoices for return")
        
        # Get items data for each invoice with essential fields
        for invoice in invoices:
            frappe.logger().debug(f"Processing invoice: {invoice['name']}")
            items = frappe.get_all(
                "Sales Invoice Item",
                filters={"parent": invoice["name"]},
                fields=[
                    "name", "item_code", "item_name", "qty", "rate", "amount", "stock_qty",
                    "discount_percentage", "discount_amount", "uom", "warehouse", 
                    "price_list_rate", "conversion_factor"
                ]
            )
            invoice["items"] = items
            frappe.logger().debug(f"Invoice {invoice['name']} has {len(items)} items")

        frappe.logger().info(f"Returning {len(invoices)} invoices with items data")
        return invoices

    except Exception as e:
        frappe.logger().error(f"Error in get_invoices_for_return: {str(e)}")
        frappe.logger().error(f"Exception type: {type(e).__name__}")
        import traceback
        frappe.logger().error(f"Traceback: {traceback.format_exc()}")
        return []
