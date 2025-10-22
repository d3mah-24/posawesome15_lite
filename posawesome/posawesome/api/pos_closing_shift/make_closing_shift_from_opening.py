# -*- coding: utf-8 -*-
# Copyright (c) 2024, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.utils import flt


@frappe.whitelist()
def make_closing_shift_from_opening(opening_shift):
    """
    POST - Create closing shift from opening shift
    """
    try:
        opening_shift = json.loads(opening_shift)
        _submit_printed_invoices(opening_shift.get("name"))
        closing_shift = frappe.new_doc("POS Closing Shift")
        closing_shift.pos_opening_shift = opening_shift.get("name")
        closing_shift.period_start_date = opening_shift.get("period_start_date")
        closing_shift.period_end_date = frappe.utils.get_datetime()
        closing_shift.pos_profile = opening_shift.get("pos_profile")
        closing_shift.user = opening_shift.get("user")
        closing_shift.company = opening_shift.get("company")
        closing_shift.grand_total = 0
        closing_shift.net_total = 0
        closing_shift.total_quantity = 0

        invoices = _get_pos_invoices(opening_shift.get("name"))

        pos_transactions = []
        taxes = []
        payments = []
        pos_payments_table = []
        
        # Check if balance_details exists and is not None
        balance_details = opening_shift.get("balance_details") or []
        for detail in balance_details:
            payments.append(
                frappe._dict(
                    {
                        "mode_of_payment": detail.get("mode_of_payment"),
                        "opening_amount": detail.get("amount") or 0,
                        "expected_amount": detail.get("amount") or 0,
                    }
                )
            )

        for d in invoices:
            pos_transactions.append(
                frappe._dict(
                    {
                        "sales_invoice": d.name,
                        "posting_date": d.posting_date,
                        "grand_total": d.grand_total,
                        "customer": d.customer,
                    }
                )
            )
            closing_shift.grand_total += flt(d.grand_total)
            closing_shift.net_total += flt(d.net_total)
            closing_shift.total_quantity += flt(d.total_qty)

            for t in d.taxes:
                existing_tax = [tx for tx in taxes if tx.account_head == t.account_head and tx.rate == t.rate]
                if existing_tax:
                    existing_tax[0].amount += flt(t.tax_amount)
                else:
                    taxes.append(
                        frappe._dict(
                            {
                                "account_head": t.account_head,
                                "rate": t.rate,
                                "amount": t.tax_amount,
                            }
                        )
                    )

            for p in d.payments:
                existing_pay = [pay for pay in payments if pay.mode_of_payment == p.mode_of_payment]
                if existing_pay:
                    cash_mode_of_payment = frappe.get_value(
                        "POS Profile",
                        opening_shift.get("pos_profile"),
                        "posa_cash_mode_of_payment",
                    )
                    if not cash_mode_of_payment:
                        cash_mode_of_payment = "Cash"
                    if existing_pay[0].mode_of_payment == cash_mode_of_payment:
                        amount = p.amount - d.change_amount
                    else:
                        amount = p.amount
                    existing_pay[0].expected_amount += flt(amount)
                else:
                    payments.append(
                        frappe._dict(
                            {
                                "mode_of_payment": p.mode_of_payment,
                                "opening_amount": 0,
                                "expected_amount": p.amount,
                            }
                        )
                    )

        pos_payments = _get_payments_entries(opening_shift.get("name"))

        for py in pos_payments:
            pos_payments_table.append(
                frappe._dict(
                    {
                        "payment_entry": py.name,
                        "mode_of_payment": py.mode_of_payment,
                        "paid_amount": py.paid_amount,
                        "posting_date": py.posting_date,
                        "customer": py.party,
                    }
                )
            )
            existing_pay = [pay for pay in payments if pay.mode_of_payment == py.mode_of_payment]
            if existing_pay:
                existing_pay[0].expected_amount += flt(py.paid_amount)
            else:
                payments.append(
                    frappe._dict(
                        {
                            "mode_of_payment": py.mode_of_payment,
                            "opening_amount": 0,
                            "expected_amount": py.paid_amount,
                        }
                    )
                )

        closing_shift.set("pos_transactions", pos_transactions)
        closing_shift.set("payment_reconciliation", payments)
        closing_shift.set("taxes", taxes)
        closing_shift.set("pos_payments", pos_payments_table)

        return closing_shift
        
    except Exception as e:
        frappe.log_error(f"[make_closing_shift_from_opening.py][make_closing_shift_from_opening] Error: {str(e)}")
        frappe.throw(f"Error creating closing shift: {str(e)}")


def _submit_printed_invoices(pos_opening_shift):
    """Helper function to submit printed invoices"""
    try:
        invoices_list = frappe.get_all(
            "Sales Invoice",
            filters={
                "posa_pos_opening_shift": pos_opening_shift,
                "docstatus": 0,
                "posa_is_printed": 1,
            },
        )
        for invoice in invoices_list:
            invoice_doc = frappe.get_doc("Sales Invoice", invoice.name)
            invoice_doc.submit()
    except Exception as e:
        frappe.log_error(f"[make_closing_shift_from_opening.py][_submit_printed_invoices] Error: {str(e)}")


def _get_pos_invoices(pos_opening_shift):
    """Helper function to get POS invoices"""
    try:
        data = frappe.db.sql(
            """
        select
            name
        from
            `tabSales Invoice`
        where
            docstatus = 1 and posa_pos_opening_shift = %s
        """,
            (pos_opening_shift),
            as_dict=1,
        )

        return [frappe.get_doc("Sales Invoice", d.name).as_dict() for d in data]
    except Exception as e:
        frappe.log_error(f"[make_closing_shift_from_opening.py][_get_pos_invoices] Error: {str(e)}")
        return []


def _get_payments_entries(pos_opening_shift):
    """Helper function to get payment entries"""
    try:
        return frappe.get_all(
            "Payment Entry",
            filters={
                "docstatus": 1,
                "reference_no": pos_opening_shift,
                "payment_type": "Receive",
            },
            fields=[
                "name",
                "mode_of_payment",
                "paid_amount",
                "reference_no",
                "posting_date",
                "party",
            ],
        )
    except Exception as e:
        frappe.log_error(f"[make_closing_shift_from_opening.py][_get_payments_entries] Error: {str(e)}")
        return []
