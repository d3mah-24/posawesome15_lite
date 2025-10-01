# -*- coding: utf-8 -*-
# Copyright (c) 2023, Youssef Restom and contributors
# For license information, please see license.txt


from __future__ import unicode_literals

# import frappe
from frappe.utils import flt
from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice


class custom_calculate_taxes_and_totals(calculate_taxes_and_totals):
    def _get_tax_rate(self, tax, item_tax_map):
        try:
            print(f"[INFO] Getting tax rate for account_head: {tax.account_head}")
            if tax.account_head in item_tax_map:
                rate = flt(item_tax_map.get(tax.account_head), self.doc.precision("rate", tax))
                print(f"[INFO] Found tax rate: {rate}")
                return rate
            else:
                print(f"[INFO] Tax account_head {tax.account_head} not found in item_tax_map. Returning 0.")
                return 0
        except Exception as e:
            print(f"[ERROR] Exception in _get_tax_rate: {e}")
            raise


class customSalesInvoice(SalesInvoice):
    def calculate_taxes_and_totals(object):
        return custom_calculate_taxes_and_totals(object)
