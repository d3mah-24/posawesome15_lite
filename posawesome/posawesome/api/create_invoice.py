# -*- coding: utf-8 -*-
"""
Create Invoice API
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()  # type: ignore
def create_invoice(customer, pos_profile, pos_opening_shift):
    """
    POST - Create new invoice
    """
    doc = frappe.new_doc("Sales Invoice")
    doc.customer = customer
    doc.pos_profile = pos_profile
    doc.posa_pos_opening_shift = pos_opening_shift
    doc.is_pos = 1
    doc.save()
    return doc.as_dict()
