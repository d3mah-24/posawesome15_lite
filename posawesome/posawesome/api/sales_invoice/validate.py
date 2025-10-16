# -*- coding: utf-8 -*-
"""
Validate Hook Function
Handles Sales Invoice validation
"""

from __future__ import unicode_literals

import frappe
from frappe import _


def validate(doc, method):
    """
    Validate Sales Invoice
    """
    try:
        if not doc.is_pos:
            return
            
        # Basic validations
        if not doc.pos_profile:
            frappe.throw(_("POS Profile is required for POS Invoice"))
        if not doc.customer:
            frappe.throw(_("Customer is required for POS Invoice"))
        if not doc.items:
            frappe.throw(_("At least one item is required"))
        if not doc.posa_pos_opening_shift:
            frappe.throw(_("POS Opening Shift is required"))
        if not doc.company:
            frappe.throw(_("Company is required"))
        if not doc.currency:
            frappe.throw(_("Currency is required"))
            
    except Exception as e:
        raise
