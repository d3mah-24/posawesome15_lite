# -*- coding: utf-8 -*-
"""
Get Payment Account Function
Handles getting account for mode of payment
"""

from __future__ import unicode_literals

import frappe


def get_payment_account(mode_of_payment, company):
    """
    Get account for mode of payment
    """
    try:
        # Try to get account from Mode of Payment Account table
        account = frappe.db.get_value(
            "Mode of Payment Account",
            {"parent": mode_of_payment, "company": company},
            "default_account"
        )
        
        if account:
            result = {"account": account}
            return result
        
        # Try to get account from POS Payment Method
        account = frappe.db.get_value(
            "POS Payment Method",
            {"mode_of_payment": mode_of_payment},
            "account"
        )
        
        if account:
            result = {"account": account}
            return result
        
        # Try to get company's default cash account
        cash_account = frappe.db.get_value(
            "Company",
            company,
            "default_cash_account"
        )
        
        if cash_account:
            result = {"account": cash_account}
            return result
        
        # Try to get company's default bank account
        bank_account = frappe.db.get_value(
            "Company",
            company,
            "default_bank_account"
        )
        
        if bank_account:
            result = {"account": bank_account}
            return result
        
        # Try to get any cash account for the company
        cash_account = frappe.db.get_value(
            "Account",
            {"account_type": "Cash", "company": company, "is_group": 0},
            "name"
        )
        
        if cash_account:
            result = {"account": cash_account}
            return result
        
        # Try to get any bank account for the company
        bank_account = frappe.db.get_value(
            "Account",
            {"account_type": "Bank", "company": company, "is_group": 0},
            "name"
        )
        
        if bank_account:
            result = {"account": bank_account}
            return result
        
        result = {"account": ""}
        return result
        
    except Exception as e:
        return {"account": ""}
