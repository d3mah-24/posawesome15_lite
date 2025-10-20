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
    try:
        # Search for invoices that can be returned
        filters = {
            "company": company,
            "docstatus": 1,  # Only submitted invoices
            "is_return": 0,  # Not already a return
        }
        
        if invoice_name:
            filters["name"] = ["like", f"%{invoice_name}%"]
        
        invoices = frappe.get_all(
            "Sales Invoice",
            filters=filters,
            fields=["name", "customer", "grand_total", "outstanding_amount", "posting_date", "currency"],
            order_by="posting_date desc",
            limit=50  # Increased limit
        )
        
        # Get items data for each invoice with essential fields
        for invoice in invoices:
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

        return invoices

    except Exception as e:
        frappe.logger().error(f"Error in get_invoices_for_return: {str(e)}")
        return []
