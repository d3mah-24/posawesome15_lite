# -*- coding: utf-8 -*-
# Copyright (c) 2020, future-support and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe.utils import nowdate, flt, cstr, getdate
from frappe import _
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from erpnext.accounts.doctype.pos_profile.pos_profile import get_item_groups
from frappe.utils.background_jobs import enqueue
from erpnext.accounts.party import get_party_bank_account
from erpnext.stock.doctype.batch.batch import (
    get_batch_no,
    get_batch_qty,
)
from erpnext.accounts.doctype.payment_request.payment_request import (
    get_dummy_message,
    get_existing_payment_request_amount,
)

from erpnext.accounts.doctype.loyalty_program.loyalty_program import (
    get_loyalty_program_details_with_points,
)
from posawesome.posawesome.doctype.pos_coupon.pos_coupon import check_coupon_code
from posawesome.posawesome.doctype.delivery_charges.delivery_charges import (
    get_applicable_delivery_charges as _get_applicable_delivery_charges,
)




@frappe.whitelist()
def create_payment_request(doc):
    doc = json.loads(doc)
    for pay in doc.get("payments"):
        if pay.get("type") == "Phone":
            if pay.get("amount") <= 0:
                frappe.throw(_("Payment amount cannot be less than or equal to 0"))

            if not doc.get("contact_mobile"):
                frappe.throw(_("Please enter the phone number first"))

            # Return success message only without creating Payment Request
            return {
                "message": f"Payment request sent to customer {doc.get('contact_mobile')} successfully",
                "amount": pay.get("amount"),
                "currency": doc.get("currency", "LYD"),
                "customer": doc.get("customer"),
                "invoice": doc.get("name")
            }

def get_amount(ref_doc, payment_account=None):
    """get amount based on doctype"""
    grand_total = 0
    for pay in ref_doc.payments:
        if pay.type == "Phone" and pay.account == payment_account:
            grand_total = pay.amount
            break

    if grand_total > 0:
        return grand_total

    else:
        frappe.throw(
            _("Payment Entry is already created or payment account is not matched")
        )

@frappe.whitelist()
def get_applicable_delivery_charges(
    company, pos_profile, customer, shipping_address_name=None
):
    return _get_applicable_delivery_charges(
        company, pos_profile, customer, shipping_address_name
    )