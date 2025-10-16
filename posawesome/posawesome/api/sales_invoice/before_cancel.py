# -*- coding: utf-8 -*-
"""
Before Cancel Hook Function
Handles Sales Invoice before cancel operations
"""

from __future__ import unicode_literals

import frappe
from frappe import _


def before_cancel(doc, method):
    """Block cancelling POS invoices when the linked shift is closed."""
    try:
        if not (doc.is_pos and doc.posa_pos_opening_shift):
            return

        shift_status = frappe.get_cached_value(
            "POS Opening Shift",
            doc.posa_pos_opening_shift,
            "status",
        )
        if shift_status == "Closed":
            frappe.throw(_("Cannot cancel invoice from closed shift"))
    except Exception as e:
        raise
