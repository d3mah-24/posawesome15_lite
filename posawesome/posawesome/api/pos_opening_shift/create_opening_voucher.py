# -*- coding: utf-8 -*-
"""
Create Opening Voucher Function
Handles creating new POS Opening Shift
"""

from __future__ import unicode_literals

import json
import frappe
from .update_opening_shift_data import update_opening_shift_data


@frappe.whitelist()
def create_opening_voucher(pos_profile, company, balance_details):
    """
    POST - Create new POS Opening Shift
    """
    try:
        balance_details = json.loads(balance_details)

        new_pos_opening = frappe.get_doc(
            {
                "doctype": "POS Opening Shift",
                "period_start_date": frappe.utils.get_datetime(),
                "posting_date": frappe.utils.getdate(),
                "user": frappe.session.user,
                "pos_profile": pos_profile,
                "company": company,
                "docstatus": 1,
            }
        )
        new_pos_opening.set("balance_details", balance_details)
        new_pos_opening.insert(ignore_permissions=True)

        data = {}
        data["pos_opening_shift"] = new_pos_opening.as_dict()
        update_opening_shift_data(data, new_pos_opening.pos_profile)
        return data
        
    except Exception as e:
        frappe.throw(f"Error creating opening voucher: {str(e)}")
