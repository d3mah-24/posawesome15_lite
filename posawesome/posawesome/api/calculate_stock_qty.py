# -*- coding: utf-8 -*-
"""
Calculate Stock Qty API
"""

from __future__ import unicode_literals

import frappe
from frappe.utils import flt


@frappe.whitelist()  # type: ignore
def calculate_stock_qty(qty, conversion_factor):
    """
    Calculate stock quantity from sales quantity
    """
    return flt(qty) * flt(conversion_factor)
