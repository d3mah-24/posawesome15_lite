# -*- coding: utf-8 -*-
"""
Get Total Items Discount API
"""

from __future__ import unicode_literals

import frappe
from frappe.utils import flt


@frappe.whitelist()  # type: ignore
def get_total_items_discount(invoice_name):
    """
    Calculate total discount for all items in an invoice
    """
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        
        total_discount = 0
        for item in doc.items:
            if item.discount_percentage:
                discount_amount = flt(item.price_list_rate) * flt(item.discount_percentage) / 100
                total_discount += discount_amount
            elif item.discount_amount:
                total_discount += flt(item.discount_amount)
        
        return {
            "total_discount": total_discount,
            "grand_total": doc.grand_total,
            "net_total": doc.net_total
        }
        
    except Exception as e:
        frappe.log_error(f"Error calculating total discount: {str(e)}")
        return {"total_discount": 0, "grand_total": 0, "net_total": 0}
