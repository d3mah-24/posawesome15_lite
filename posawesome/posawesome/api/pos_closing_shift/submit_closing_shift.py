# -*- coding: utf-8 -*-
# Copyright (c) 2024, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json


@frappe.whitelist()
def submit_closing_shift(closing_shift):
    """
    POST - Submit closing shift
    """
    try:
        closing_shift = json.loads(closing_shift)
        doc = frappe.get_doc("POS Closing Shift", closing_shift.get("name"))
        doc.submit()
        
        frappe.log_error(f"[submit_closing_shift.py][submit_closing_shift] Successfully submitted shift: {doc.name}")
        return doc
        
    except Exception as e:
        frappe.log_error(f"[submit_closing_shift.py][submit_closing_shift] Error: {str(e)}")
        frappe.throw(f"Error submitting closing shift: {str(e)}")
