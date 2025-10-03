# -*- coding: utf-8 -*-
# Copyright (c) 2021, Youssef Restom and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, add_days, nowdate, cstr, getdate
from frappe.utils.data import money_in_words
from erpnext.setup.utils import get_exchange_rate
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
from posawesome.posawesome.doctype.pos_coupon.pos_coupon import update_coupon_code_count, check_coupon_code

# =============================================================================
# OFFER API FUNCTIONS
# =============================================================================

@frappe.whitelist()
def apply_offers_to_invoice(invoice_name, offer_names):
    """
    POST - Apply specific offers to an invoice
    """
    try:
        if not invoice_name or not offer_names:
            return None
        
        # Handle both string and list inputs
        if isinstance(offer_names, str):
            try:
                offer_names = json.loads(offer_names)
            except:
                offer_names = [offer_names]
        
        if not isinstance(offer_names, list):
            offer_names = [offer_names]
        
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        
        # Apply each offer
        for offer_name in offer_names:
            try:
                _apply_single_offer(doc, offer_name)
            except Exception as e:
                frappe.log_error(f"Error applying offer {offer_name}: {str(e)}")
                continue
        
        # Let ERPNext handle all calculations
        doc.set_missing_values()
        doc.calculate_taxes_and_totals()
        doc.save()
        
        return doc.as_dict()
    except Exception as e:
        frappe.log_error(f"Error in apply_offers_to_invoice: {str(e)}")
        raise

@frappe.whitelist()
def remove_offers_from_invoice(invoice_name, offer_names):
    """
    DELETE - Remove specific offers from an invoice
    """
    try:
        if not invoice_name or not offer_names:
            return None
        
        # Handle both string and list inputs
        if isinstance(offer_names, str):
            try:
                offer_names = json.loads(offer_names)
            except:
                offer_names = [offer_names]
        
        if not isinstance(offer_names, list):
            offer_names = [offer_names]
        
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        
        # Remove each offer
        for offer_name in offer_names:
            try:
                _remove_single_offer(doc, offer_name)
            except Exception as e:
                frappe.log_error(f"Error removing offer {offer_name}: {str(e)}")
                continue
        
        # Let ERPNext handle all calculations
        doc.set_missing_values()
        doc.calculate_taxes_and_totals()
        doc.save()
        
        return doc.as_dict()
    except Exception as e:
        frappe.log_error(f"Error in remove_offers_from_invoice: {str(e)}")
        raise

def _apply_single_offer(doc, offer_name):
    """
    Apply a single offer to the invoice (internal helper)
    """
    try:
        # Get the offer details
        offer = frappe.get_doc("POS Offer", offer_name)
        
        if not offer or offer.disabled:
            return
        
        if offer.apply_on == "Item Code":
            _apply_item_code_offer(doc, offer)
        elif offer.apply_on == "Item Group":
            _apply_item_group_offer(doc, offer)
        elif offer.apply_on == "Brand":
            _apply_brand_offer(doc, offer)
        elif offer.apply_on == "Transaction":
            _apply_transaction_offer(doc, offer)
    except Exception as e:
        frappe.log_error(f"Error in _apply_single_offer for {offer_name}: {str(e)}")
        raise

def _remove_single_offer(doc, offer_name):
    """
    Remove a single offer from the invoice (internal helper)
    """
    try:
        # This would need to track which offers were applied and reverse them
        # For now, we'll reset discounts and let user reapply
        for item in doc.items:
            if not getattr(item, 'posa_is_offer', False):
                item.discount_percentage = 0
                item.discount_amount = 0
                item.rate = item.price_list_rate
        
        # Reset transaction level discounts
        doc.additional_discount_percentage = 0
        doc.discount_amount = 0
    except Exception as e:
        frappe.log_error(f"Error in _remove_single_offer for {offer_name}: {str(e)}")
        raise

def _apply_item_code_offer(doc, offer):
    """
    Apply item code specific offer
    """
    for item in doc.items:
        if item.item_code == offer.item and not getattr(item, 'posa_is_offer', False):
            if offer.discount_type == "Rate":
                item.rate = offer.rate
            elif offer.discount_type == "Discount Percentage":
                item.discount_percentage = offer.discount_percentage
            elif offer.discount_type == "Discount Amount":
                item.discount_amount = offer.discount_amount

def _apply_item_group_offer(doc, offer):
    """
    Apply item group specific offer
    """
    for item in doc.items:
        if item.item_group == offer.item_group and not getattr(item, 'posa_is_offer', False):
            if offer.discount_type == "Rate":
                item.rate = offer.rate
            elif offer.discount_type == "Discount Percentage":
                item.discount_percentage = offer.discount_percentage
            elif offer.discount_type == "Discount Amount":
                item.discount_amount = offer.discount_amount

def _apply_brand_offer(doc, offer):
    """
    Apply brand specific offer
    """
    for item in doc.items:
        if item.brand == offer.brand and not getattr(item, 'posa_is_offer', False):
            if offer.discount_type == "Rate":
                item.rate = offer.rate
            elif offer.discount_type == "Discount Percentage":
                item.discount_percentage = offer.discount_percentage
            elif offer.discount_type == "Discount Amount":
                item.discount_amount = offer.discount_amount

def _apply_transaction_offer(doc, offer):
    """
    Apply transaction level offer
    """
    if offer.discount_type == "Discount Percentage":
        doc.additional_discount_percentage = offer.discount_percentage
    elif offer.discount_type == "Discount Amount":
        doc.discount_amount = offer.discount_amount

def validate(doc, method):
    validate_shift(doc)
    apply_tax_inclusive(doc)


def before_submit(doc, method):
    add_loyalty_point(doc)
    update_coupon(doc, "used")


def before_cancel(doc, method):
    update_coupon(doc, "cancelled")


def add_loyalty_point(invoice_doc):
    for offer in invoice_doc.posa_offers:
        if offer.offer == "Loyalty Point":
            original_offer = frappe.get_doc("POS Offer", offer.offer_name)
            if original_offer.loyalty_points > 0:
                loyalty_program = frappe.get_value("Customer", invoice_doc.customer, "loyalty_program")
                if not loyalty_program:
                    loyalty_program = original_offer.loyalty_program
                doc = frappe.get_doc(
                    {
                        "doctype": "Loyalty Point Entry",
                        "loyalty_program": loyalty_program,
                        "loyalty_program_tier": original_offer.name,
                        "customer": invoice_doc.customer,
                        "invoice_type": "Sales Invoice",
                        "invoice": invoice_doc.name,
                        "loyalty_points": original_offer.loyalty_points,
                        "expiry_date": add_days(invoice_doc.posting_date, 10000),
                        "posting_date": invoice_doc.posting_date,
                        "company": invoice_doc.company,
                    }
                )
                doc.insert(ignore_permissions=True)


def update_coupon(doc, transaction_type):
    for coupon in doc.posa_coupons:
        if not coupon.applied:
            continue
        update_coupon_code_count(coupon.coupon, transaction_type)




def apply_tax_inclusive(doc):
    """Mark taxes as inclusive based on POS Profile setting."""
    if not doc.pos_profile:
        return
    try:
        tax_inclusive = frappe.get_cached_value("POS Profile", doc.pos_profile, "posa_tax_inclusive")
    except Exception:
        tax_inclusive = 0

    if not tax_inclusive:
        return

    has_changes = False
    for tax in doc.get("taxes", []):
        if not tax.included_in_print_rate:
            tax.included_in_print_rate = 1
            has_changes = True

    if has_changes:
        doc.calculate_taxes_and_totals()


def validate_shift(doc):
    if doc.posa_pos_opening_shift and doc.pos_profile and doc.is_pos:
        # check if shift is open
        shift = frappe.get_cached_doc("POS Opening Shift", doc.posa_pos_opening_shift)
        if shift.status != "Open":
            frappe.throw(_("POS Shift {0} is not open").format(shift.name))
        # check if shift is for the same profile
        if shift.pos_profile != doc.pos_profile:
            frappe.throw(_("POS Opening Shift {0} is not for the same POS Profile").format(shift.name))
        # check if shift is for the same company
        if shift.company != doc.company:
            frappe.throw(_("POS Opening Shift {0} is not for the same company").format(shift.name))


# =============================================================================
# FUNCTIONS COPIED FROM update_invoice.py
# =============================================================================

def validate_return_items(return_against, items):
    """
    Validate return items against original invoice
    """
    try:
        original_invoice = frappe.get_doc("Sales Invoice", return_against)
        original_items = {item.item_code: item.qty for item in original_invoice.items}
        
        for item in items:
            item_code = item.get("item_code")
            qty = abs(item.get("qty", 0))  # Return qty is negative, so we use abs
            
            if item_code not in original_items:
                return {
                    "valid": False,
                    "message": _("Item {0} was not found in the original invoice {1}").format(
                        item_code, return_against
                    )
                }
            
            if qty > original_items[item_code]:
                return {
                    "valid": False,
                    "message": _("Return quantity for item {0} cannot be greater than the original quantity {1}").format(
                        item_code, original_items[item_code]
                    )
                }
        
        return {"valid": True}
        
    except Exception as e:
        return {
            "valid": False,
            "message": _("Error validating return items: {0}").format(str(e))
        }

@frappe.whitelist()
def search_invoices_for_return(invoice_name, company):
    """
    Search for invoices that can be returned.
    Excludes:
    - Previously returned invoices (is_return=1)
    - Cancelled invoices
    - Draft invoices
    - Non-POS invoices
    - Invoices that already have returns
    """
    filters = {
        "docstatus": 1,  # Submitted invoices only
        "is_return": 0,  # Exclude previously returned invoices (this is the primary filter)
        "is_pos": 1,     # POS invoices only
        "status": ["not in", ["Cancelled", "Draft"]]  # Exclude cancelled and draft invoices
    }
    
    if invoice_name:
        filters["name"] = ["like", f"%{invoice_name}%"]
    if company:
        filters["company"] = company

    # Get list of eligible invoices with limit to prevent loading too many
    invoices_list = frappe.get_list(
        "Sales Invoice",
        filters=filters,
        fields=["name"],
        limit_page_length=10,  # Maximum 10 invoices to prevent performance issues
        order_by="creation desc",
    )
    
    data = []
    
    for invoice in invoices_list:
        # Double check: Ensure this invoice does not already have a return
        existing_returns = frappe.get_all(
            "Sales Invoice",
            filters={
                "return_against": invoice["name"],
                "docstatus": 1,
                "is_return": 1
            },
            fields=["name"]
        )
        
        # Include only invoices that don't have returns yet
        if not existing_returns:
            try:
                invoice_doc = frappe.get_doc("Sales Invoice", invoice["name"])
                # Ensure items are loaded
                if not invoice_doc.items:
                    invoice_doc.load_from_db()
                data.append(invoice_doc)
            except Exception as e:
                # Skip invoices that cannot be loaded
                frappe.log_error(f"Error loading invoice {invoice['name']}: {str(e)}")
                continue
    
    return data

def add_taxes_from_tax_template(item, parent_doc):
    accounts_settings = frappe.get_cached_doc("Accounts Settings")
    add_taxes_from_item_tax_template = (
        accounts_settings.add_taxes_from_item_tax_template
    )
    if item.get("item_tax_template") and add_taxes_from_item_tax_template:
        item_tax_template = item.get("item_tax_template")
        taxes_template_details = frappe.get_all(
            "Item Tax Template Detail",
            filters={"parent": item_tax_template},
            fields=["tax_type"],
        )

        for tax_detail in taxes_template_details:
            tax_type = tax_detail.get("tax_type")

            found = any(tax.account_head == tax_type for tax in parent_doc.taxes)
            if not found:
                tax_row = parent_doc.append("taxes", {})
                tax_row.update(
                    {
                        "description": str(tax_type).split(" - ")[0],
                        "charge_type": "On Net Total",
                        "account_head": tax_type,
                    }
                )

                if parent_doc.doctype == "Purchase Order":
                    tax_row.update({"category": "Total", "add_deduct_tax": "Add"})
                tax_row.db_insert()

@frappe.whitelist()
def update_invoice(data):
    """
    Let ERPNext handle all calculations through set_missing_values() and save()
    """
    data = json.loads(data)
    
    if data.get("name"):
        try:
            invoice_doc = frappe.get_doc("Sales Invoice", data.get("name"))
            invoice_doc.update(data)
        except frappe.DoesNotExistError:
            invoice_doc = frappe.new_doc("Sales Invoice")
            invoice_doc.update(data)
    else:
        invoice_doc = frappe.new_doc("Sales Invoice")
        invoice_doc.update(data)

    # Basic validation for return invoices
    if (data.get("is_return") or invoice_doc.is_return) and invoice_doc.get("return_against"):
        validation = validate_return_items(
            invoice_doc.return_against, [d.as_dict() for d in invoice_doc.items]
        )
        if not validation.get("valid"):
            frappe.throw(validation.get("message"))

    #Let ERPNext handle all calculations
    invoice_doc.set_missing_values()
    
    # Basic business rules (not calculations)
    allow_zero_rated_items = frappe.get_cached_value(
        "POS Profile", invoice_doc.pos_profile, "posa_allow_zero_rated_items"
    )
    for item in invoice_doc.items:
        if not item.rate or item.rate == 0:
            if allow_zero_rated_items:
                item.is_free_item = 1
            else:
                frappe.throw(_("Rate cannot be zero for item {0}").format(item.item_code))
        else:
            item.is_free_item = 0

    # CRITICAL: Calculate taxes and totals to apply item discounts and invoice discounts
    # Without this, discount_percentage and additional_discount_percentage won't be applied
    invoice_doc.calculate_taxes_and_totals()

    # Save and let ERPNext calculate everything
    invoice_doc.flags.ignore_permissions = True
    frappe.flags.ignore_account_permission = True
    invoice_doc.docstatus = 0
    invoice_doc.save()

    #Return ERPNext calculated data as-is
    return invoice_doc.as_dict()

# =============================================================================
# FUNCTIONS COPIED FROM submit_invoice.py
# =============================================================================

def set_batch_nos_for_bundels(doc, warehouse_field, throw=False):
    """Automatically select `batch_no` for outgoing items in item table"""
    for d in doc.packed_items:
        qty = d.get("stock_qty") or d.get("transfer_qty") or d.get("qty") or 0
        has_batch_no = frappe.db.get_value("Item", d.item_code, "has_batch_no")
        warehouse = d.get(warehouse_field, None)
        if has_batch_no and warehouse and qty > 0:
            if not d.batch_no:
                d.batch_no = get_batch_no(
                    d.item_code, warehouse, qty, throw, d.serial_no
                )
            else:
                batch_qty = get_batch_qty(batch_no=d.batch_no, warehouse=warehouse)
                if flt(batch_qty, d.precision("qty")) < flt(qty, d.precision("qty")):
                    frappe.throw(
                        _(
                            "Row #{0}: The batch {1} has only {2} qty. Please select another batch which has {3} qty available or split the row into multiple rows, to deliver/issue from multiple batches"
                        ).format(d.idx, d.batch_no, batch_qty, qty)
                    )

def set_batch_nos(doc, warehouse_field, throw=False, child_table="items"):
    """Automatically select `batch_no` for outgoing items in item table"""
    for d in doc.get(child_table):
        qty = d.get("stock_qty") or d.get("transfer_qty") or d.get("qty") or 0
        warehouse = d.get(warehouse_field, None)
        if warehouse and qty > 0 and frappe.db.get_value("Item", d.item_code, "has_batch_no"):
            if not d.batch_no:
                d.batch_no = get_batch_no(d.item_code, warehouse, qty, throw, d.serial_no)
            else:
                batch_qty = get_batch_qty(batch_no=d.batch_no, warehouse=warehouse)
                if flt(batch_qty, d.precision("qty")) < flt(qty, d.precision("qty")):
                    frappe.throw(
                        _(
                            "Row #{0}: The batch {1} has only {2} qty. Please select another batch which has {3} qty available or split the row into multiple rows, to deliver/issue from multiple batches"
                        ).format(d.idx, d.batch_no, batch_qty, qty)
                    )

def redeeming_customer_credit(
    invoice_doc, data, is_payment_entry, total_cash, cash_account, payments
):
    # redeeming customer credit with journal voucher
    today = nowdate()
    if data.get("redeemed_customer_credit"):
        cost_center = frappe.get_value(
            "POS Profile", invoice_doc.pos_profile, "cost_center"
        )
        if not cost_center:
            cost_center = frappe.get_value(
                "Company", invoice_doc.company, "cost_center"
            )
        if not cost_center:
            frappe.throw(
                _("Cost Center is not set in pos profile {}").format(
                    invoice_doc.pos_profile
                )
            )
        for row in data.get("customer_credit_dict"):
            if row["type"] == "Invoice" and row["credit_to_redeem"]:
                outstanding_invoice = frappe.get_doc(
                    "Sales Invoice", row["credit_origin"]
                )

                jv_doc = frappe.get_doc(
                    {
                        "doctype": "Journal Entry",
                        "voucher_type": "Journal Entry",
                        "posting_date": today,
                        "company": invoice_doc.company,
                    }
                )

                jv_debit_entry = {
                    "account": outstanding_invoice.debit_to,
                    "party_type": "Customer",
                    "party": invoice_doc.customer,
                    "reference_type": "Sales Invoice",
                    "reference_name": outstanding_invoice.name,
                    "debit_in_account_currency": row["credit_to_redeem"],
                    "cost_center": cost_center,
                }

                jv_credit_entry = {
                    "account": invoice_doc.debit_to,
                    "party_type": "Customer",
                    "party": invoice_doc.customer,
                    "reference_type": "Sales Invoice",
                    "reference_name": invoice_doc.name,
                    "credit_in_account_currency": row["credit_to_redeem"],
                    "cost_center": cost_center,
                }

                jv_doc.append("accounts", jv_debit_entry)
                jv_doc.append("accounts", jv_credit_entry)

                jv_doc.flags.ignore_permissions = True
                frappe.flags.ignore_account_permission = True
                jv_doc.set_missing_values()
                jv_doc.save()
                jv_doc.submit()

    if is_payment_entry and total_cash > 0:
        for payment in payments:
            if not payment.amount:
                continue
            payment_entry_doc = frappe.get_doc(
                {
                    "doctype": "Payment Entry",
                    "posting_date": today,
                    "payment_type": "Receive",
                    "party_type": "Customer",
                    "party": invoice_doc.customer,
                    "paid_amount": payment.amount,
                    "received_amount": payment.amount,
                    "paid_from": invoice_doc.debit_to,
                    "paid_to": payment.account,
                    "company": invoice_doc.company,
                    "mode_of_payment": payment.mode_of_payment,
                    "reference_no": invoice_doc.posa_pos_opening_shift,
                    "reference_date": today,
                }
            )

            payment_reference = {
                "allocated_amount": payment.amount,
                "due_date": data.get("due_date"),
                "reference_doctype": "Sales Invoice",
                "reference_name": invoice_doc.name,
            }

            payment_entry_doc.append("references", payment_reference)
            payment_entry_doc.flags.ignore_permissions = True
            frappe.flags.ignore_account_permission = True
            payment_entry_doc.save()
            payment_entry_doc.submit()

def submit_in_background_job(kwargs):
    invoice = kwargs.get("invoice")
    invoice_doc = kwargs.get("invoice_doc")
    data = kwargs.get("data")
    is_payment_entry = kwargs.get("is_payment_entry")
    total_cash = kwargs.get("total_cash")
    cash_account = kwargs.get("cash_account")
    payments = kwargs.get("payments")

    invoice_doc = frappe.get_doc("Sales Invoice", invoice)
    invoice_doc.submit()
    redeeming_customer_credit(
        invoice_doc, data, is_payment_entry, total_cash, cash_account, payments
    )

@frappe.whitelist()
def submit_invoice(invoice, data):
    data = json.loads(data)
    invoice = json.loads(invoice)
    invoice_doc = frappe.get_doc("Sales Invoice", invoice.get("name"))
    invoice_doc.update(invoice)
    if invoice.get("posa_delivery_date"):
        invoice_doc.update_stock = 0
    mop_cash_list = [
        i.mode_of_payment
        for i in invoice_doc.payments
        if "cash" in i.mode_of_payment.lower() and i.type == "Cash"
    ]
    if len(mop_cash_list) > 0:
        cash_account = get_bank_cash_account(mop_cash_list[0], invoice_doc.company)
    else:
        cash_account = {
            "account": frappe.get_value(
                "Company", invoice_doc.company, "default_cash_account"
            )
        }

    # creating advance payment
    if data.get("credit_change"):
        advance_payment_entry = frappe.get_doc(
            {
                "doctype": "Payment Entry",
                "mode_of_payment": "Cash",
                "paid_to": cash_account["account"],
                "payment_type": "Receive",
                "party_type": "Customer",
                "party": invoice_doc.get("customer"),
                "paid_amount": invoice_doc.get("credit_change"),
                "received_amount": invoice_doc.get("credit_change"),
                "company": invoice_doc.get("company"),
            }
        )

        advance_payment_entry.flags.ignore_permissions = True
        frappe.flags.ignore_account_permission = True
        advance_payment_entry.save()
        advance_payment_entry.submit()

    # calculating cash
    total_cash = 0
    if data.get("redeemed_customer_credit"):
        total_cash = invoice_doc.total - float(data.get("redeemed_customer_credit"))

    is_payment_entry = 0
    if data.get("redeemed_customer_credit"):
        for row in data.get("customer_credit_dict"):
            if row["type"] == "Advance" and row["credit_to_redeem"]:
                advance = frappe.get_doc("Payment Entry", row["credit_origin"])

                advance_payment = {
                    "reference_type": "Payment Entry",
                    "reference_name": advance.name,
                    "remarks": advance.remarks,
                    "advance_amount": advance.unallocated_amount,
                    "allocated_amount": row["credit_to_redeem"],
                }

                invoice_doc.append("advances", advance_payment)
                invoice_doc.is_pos = 0
                is_payment_entry = 1

    payments = invoice_doc.payments

    if frappe.get_value("POS Profile", invoice_doc.pos_profile, "posa_auto_set_batch"):
        set_batch_nos(invoice_doc, "warehouse", throw=True)
    set_batch_nos_for_bundels(invoice_doc, "warehouse", throw=True)
    invoice_doc.cost_center = frappe.get_value("POS Profile", invoice_doc.pos_profile, "cost_center")
    invoice_doc.flags.ignore_permissions = True
    frappe.flags.ignore_account_permission = True
    invoice_doc.posa_is_printed = 1
    invoice_doc.save()

    if data.get("due_date"):
        frappe.db.set_value(
            "Sales Invoice",
            invoice_doc.name,
            "due_date",
            data.get("due_date"),
            update_modified=False,
        )

    # Background Jobs enabled for performance improvement
    invoices_list = frappe.get_all(
        "Sales Invoice",
        filters={
            "posa_pos_opening_shift": invoice_doc.posa_pos_opening_shift,
            "docstatus": 0,
            "posa_is_printed": 1,
        },
    )
    for invoice in invoices_list:
        enqueue(
            method=submit_in_background_job,
            queue="short",
            timeout=1000,
            is_async=True,
            kwargs={
                "invoice": invoice.name,
                "data": data,
                "is_payment_entry": is_payment_entry,
                "total_cash": total_cash,
                "cash_account": cash_account,
                "payments": payments,
            },
        )

    return {"name": invoice_doc.name, "status": invoice_doc.docstatus}


# =============================================================================
# FUNCTIONS COPIED FROM get_draft_invoices.py
# =============================================================================

@frappe.whitelist()
def get_draft_invoices(pos_opening_shift):
    """
    Get draft invoices for a specific POS opening shift
    
    Args:
        pos_opening_shift: POS Opening Shift name
    
    Returns:
        List of draft Sales Invoice documents
    """
    invoices_list = frappe.get_list(
        "Sales Invoice",
        filters={
            "posa_pos_opening_shift": pos_opening_shift,
            "docstatus": 0,
            "posa_is_printed": 0,
        },
        fields=["name"],
        limit_page_length=0,
        order_by="creation desc",
    )
    data = []
    for invoice in invoices_list:
        data.append(frappe.get_cached_doc("Sales Invoice", invoice["name"]))
    return data

# ===========================================================
# INVOICE COMPUTED PROPERTIES FOR FRONTEND
# ===========================================================

@frappe.whitelist()
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

@frappe.whitelist()
def get_invoice(invoice_name):
    """
    GET - Get invoice with all data
    """
    if not invoice_name:
        return None
    
    doc = frappe.get_doc("Sales Invoice", invoice_name)
    return doc.as_dict()

@frappe.whitelist()
def add_item_to_invoice(invoice_name, item_code, qty, rate, uom):
    """
    POST - Add item to invoice
    """
    doc = frappe.get_doc("Sales Invoice", invoice_name)
    doc.append("items", {
        "item_code": item_code,
        "qty": qty,
        "rate": rate,
        "uom": uom
    })
    doc.save()
    return doc.as_dict()

@frappe.whitelist()
def update_item_in_invoice(invoice_name, item_idx, qty=None, rate=None, discount_percentage=None):
    """
    PUT - Update item in invoice
    """
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        # Convert item_idx to integer since it comes as string from frontend
        item_idx = int(item_idx)
        
        if item_idx < 0 or item_idx >= len(doc.items):
            frappe.throw(_("Invalid item index: {0}").format(item_idx))
            
        item = doc.items[item_idx]
        
        if qty is not None:
            item.qty = flt(qty)
        if rate is not None:
            item.rate = flt(rate)
        if discount_percentage is not None:
            item.discount_percentage = flt(discount_percentage)
            
        doc.save()
        return doc.as_dict()
    except ValueError:
        frappe.throw(_("Invalid item index format"))
    except Exception as e:
        frappe.throw(_("Error updating item: {0}").format(str(e)))

@frappe.whitelist()
def delete_item_from_invoice(invoice_name, item_idx):
    """
    DELETE - Remove item from invoice
    """
    try:
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        # Convert item_idx to integer since it comes as string from frontend
        item_idx = int(item_idx)
        
        if item_idx < 0 or item_idx >= len(doc.items):
            frappe.throw(_("Invalid item index: {0}").format(item_idx))
            
        doc.items.pop(item_idx)
        doc.save()
        return doc.as_dict()
    except ValueError:
        frappe.throw(_("Invalid item index format"))
    except Exception as e:
        frappe.throw(_("Error deleting item: {0}").format(str(e)))

@frappe.whitelist()
def add_payment_to_invoice(invoice_name, mode_of_payment, amount):
    """
    POST - Add payment to invoice
    """
    doc = frappe.get_doc("Sales Invoice", invoice_name)
    doc.append("payments", {
        "mode_of_payment": mode_of_payment,
        "amount": amount
    })
    doc.save()
    return doc.as_dict()

@frappe.whitelist()
def submit_invoice_simple(invoice_name):
    """
    PUT - Submit invoice (simple version)
    """
    doc = frappe.get_doc("Sales Invoice", invoice_name)
    doc.submit()
    return doc.as_dict()

@frappe.whitelist()
def delete_invoice(invoice_name):
    """
    DELETE - Delete draft invoice
    """
    doc = frappe.get_doc("Sales Invoice", invoice_name)
    if doc.docstatus == 0:  # Only delete drafts
        doc.delete()
        return {"deleted": True}
    return {"deleted": False, "error": "Cannot delete submitted invoice"}

@frappe.whitelist()
def get_total_items_discount(invoice_name):
    """
    GET - Get sum of all item-level discounts
    """
    if not invoice_name:
        return 0
    
    doc = frappe.get_doc("Sales Invoice", invoice_name)
    total_discount = 0
    
    for item in doc.items:
        if item.discount_amount:
            total_discount += item.discount_amount
        elif item.discount_percentage:
            discount_amount = (item.price_list_rate * item.discount_percentage) / 100
            total_discount += discount_amount
    
    return total_discount

# ===========================================================
# OFFER OPERATIONS - Following 1:1 Architecture
# ===========================================================

@frappe.whitelist()
def get_applicable_offers(invoice_name):
    """
    GET - Get all applicable offers for an invoice
    """
    try:
        if not invoice_name:
            return []
        
        doc = frappe.get_doc("Sales Invoice", invoice_name)
        
        if not doc.pos_profile:
            return []
            
        pos_profile = frappe.get_doc("POS Profile", doc.pos_profile)
        company = pos_profile.company
        warehouse = pos_profile.warehouse
        date = frappe.utils.nowdate()

        # Get offers using the same logic as get_offers.py
        values = {
            "company": company,
            "pos_profile": doc.pos_profile,
            "warehouse": warehouse,
            "valid_from": date,
            "valid_upto": date,
        }
        
        offers = frappe.db.sql(
            """
            SELECT *
            FROM `tabPOS Offer`
            WHERE 
            disable = 0 AND
            company = %(company)s AND
            (pos_profile is NULL OR pos_profile = '' OR pos_profile = %(pos_profile)s) AND
            (warehouse is NULL OR warehouse = '' OR warehouse = %(warehouse)s) AND
            (valid_from is NULL OR valid_from = '' OR valid_from <= %(valid_from)s) AND
            (valid_upto is NULL OR valid_upto = '' OR valid_upto >= %(valid_upto)s)
            """,
            values=values,
            as_dict=1,
        )
        
        # Filter offers based on invoice conditions
        applicable_offers = []
        for offer in offers:
            if _check_offer_conditions(doc, offer):
                applicable_offers.append(offer)
        
        return applicable_offers
        
    except Exception as e:
        frappe.log_error(f"Error in get_applicable_offers: {str(e)}")
        return []


@frappe.whitelist()
def calculate_item_discount_amount(price_list_rate, discount_percentage):
    """
    Calculate discount amount based on price and percentage
    """
    price_list_rate = flt(price_list_rate) or 0
    discount_percentage = flt(discount_percentage) or 0
    
    if discount_percentage > 0 and price_list_rate > 0:
        return flt((price_list_rate * discount_percentage) / 100, 2)
    
    return 0

@frappe.whitelist()
def calculate_item_price(item_data):
    """
    Calculate item price with discounts - ERPNext handles this automatically
    Just return the item data as ERPNext will calculate
    """
    # Convert string to dict if needed
    if isinstance(item_data, str):
        item_data = json.loads(item_data)
    
    # Let ERPNext handle the calculations
    # We just validate and return the data
    original_rate = flt(item_data.get('base_rate')) or flt(item_data.get('price_list_rate')) or 0
    
    if original_rate <= 0:
        frappe.throw(_("Price is invalid for item"))
    
    return {
        'original_rate': original_rate,
        'message': 'Use ERPNext calculated fields: doc.total, doc.grand_total, etc.'
    }

@frappe.whitelist()
def calculate_stock_qty(qty, conversion_factor):
    """
    Calculate stock quantity based on UOM conversion
    """
    qty = flt(qty) or 1
    conversion_factor = flt(conversion_factor) or 1
    
    return qty * conversion_factor

@frappe.whitelist()
def validate_invoice_items(items_data, pos_profile_name, stock_settings):
    """
    Validate invoice items - business logic should be in Python
    """
    if isinstance(items_data, str):
        items_data = json.loads(items_data)
    if isinstance(stock_settings, str):
        stock_settings = json.loads(stock_settings)
    
    pos_profile = frappe.get_cached_doc("POS Profile", pos_profile_name)
    
    validation_errors = []
    
    for item in items_data:
        # Check quantity
        if item.get('qty') == 0:
            validation_errors.append({
                'item': item.get('item_name', item.get('item_code')),
                'error': 'Quantity cannot be zero'
            })
            continue
        
        # Check negative quantity for regular invoices
        if not item.get('is_return') and item.get('qty', 0) < 0:
            validation_errors.append({
                'item': item.get('item_name', item.get('item_code')),
                'error': 'Quantity cannot be negative for regular invoices'
            })
            continue
        
        # Check discount limits
        if pos_profile.posa_item_max_discount_allowed and not item.get('posa_offer_applied'):
            if item.get('discount_amount') and flt(item.get('discount_amount')) > 0:
                discount_percentage = (flt(item.get('discount_amount')) * 100) / flt(item.get('price_list_rate', 0))
                if discount_percentage > pos_profile.posa_item_max_discount_allowed:
                    validation_errors.append({
                        'item': item.get('item_name', item.get('item_code')),
                        'error': f'Discount percentage cannot exceed {pos_profile.posa_item_max_discount_allowed}%'
                    })
                    continue
        
        # Check stock availability
        if stock_settings.get('allow_negative_stock') != 1:
            if (not item.get('is_return') and item.get('is_stock_item') and 
                item.get('stock_qty') and item.get('actual_qty') is not None and
                item.get('stock_qty') > item.get('actual_qty')):
                validation_errors.append({
                    'item': item.get('item_name', item.get('item_code')),
                    'error': f'Available quantity {item.get("actual_qty")} is insufficient'
                })
                continue
    
    return {
        'valid': len(validation_errors) == 0,
        'errors': validation_errors
    }

# =============================================================================
# BATCH MANAGEMENT API FUNCTIONS - MOVED FROM VUE FRONTEND
# =============================================================================

@frappe.whitelist()
def calculate_batch_quantities(item_code, current_item_row_id, existing_items_data, batch_no_data):
    """
    Calculate used and remaining quantities for each batch
    Moved from Vue set_batch_qty method
    """
    if isinstance(existing_items_data, str):
        existing_items_data = json.loads(existing_items_data)
    if isinstance(batch_no_data, str):
        batch_no_data = json.loads(batch_no_data)
    
    # Filter existing items for the same item code (excluding current item)
    existing_items = [
        item for item in existing_items_data 
        if item.get('item_code') == item_code and item.get('posa_row_id') != current_item_row_id
    ]
    
    # Calculate used quantities for each batch
    used_batches = {}
    for batch in batch_no_data:
        batch_no = batch.get('batch_no')
        used_batches[batch_no] = {
            **batch,
            'used_qty': 0,
            'remaining_qty': flt(batch.get('batch_qty', 0)),
        }
        
        # Calculate used quantity from existing items
        for existing_item in existing_items:
            if existing_item.get('batch_no') == batch_no:
                used_qty = flt(existing_item.get('qty', 0))
                used_batches[batch_no]['used_qty'] += used_qty
                used_batches[batch_no]['remaining_qty'] -= used_qty
    
    return list(used_batches.values())

@frappe.whitelist()
def select_optimal_batch(batch_data, preferred_batch_no=None):
    """
    Select the optimal batch based on business rules:
    1. Use preferred batch if specified and available
    2. Prioritize batches with expiry dates (FIFO - First Expiry First Out)
    3. Then by manufacturing date (FIFO - First In First Out)
    4. Finally by highest remaining quantity
    
    Moved from Vue set_batch_qty method
    """
    if isinstance(batch_data, str):
        batch_data = json.loads(batch_data)
    
    # Filter batches with remaining quantity > 0
    available_batches = [
        batch for batch in batch_data 
        if flt(batch.get('remaining_qty', 0)) > 0
    ]
    
    if not available_batches:
        return None
    
    # If preferred batch is specified and available, use it
    if preferred_batch_no:
        preferred_batch = next(
            (batch for batch in available_batches if batch.get('batch_no') == preferred_batch_no),
            None
        )
        if preferred_batch:
            return preferred_batch
    
    # Sort batches by business rules
    def sort_key(batch):
        expiry_date = batch.get('expiry_date')
        manufacturing_date = batch.get('manufacturing_date')
        remaining_qty = flt(batch.get('remaining_qty', 0))
        
        # Convert dates to sortable format (None becomes a large number for sorting)
        expiry_sort = getdate(expiry_date) if expiry_date else getdate('2099-12-31')
        mfg_sort = getdate(manufacturing_date) if manufacturing_date else getdate('1900-01-01')
        
        # Sort by: expiry_date (asc), manufacturing_date (asc), remaining_qty (desc)
        return (expiry_sort, mfg_sort, -remaining_qty)
    
    sorted_batches = sorted(available_batches, key=sort_key)
    return sorted_batches[0]

@frappe.whitelist()
def process_batch_selection(item_code, current_item_row_id, existing_items_data, batch_no_data, preferred_batch_no=None):
    """
    Complete batch selection process combining calculation and selection
    Returns the selected batch with all necessary data
    """
    try:
        # Calculate batch quantities
        calculated_batches = calculate_batch_quantities(
            item_code, current_item_row_id, existing_items_data, batch_no_data
        )
        
        # Select optimal batch
        selected_batch = select_optimal_batch(calculated_batches, preferred_batch_no)
        
        if not selected_batch:
            return {
                'success': False,
                'message': 'No available batches with sufficient quantity',
                'batch_data': calculated_batches
            }
        
        return {
            'success': True,
            'selected_batch': {
                'batch_no': selected_batch.get('batch_no'),
                'actual_batch_qty': selected_batch.get('batch_qty'),
                'remaining_qty': selected_batch.get('remaining_qty'),
                'expiry_date': selected_batch.get('expiry_date'),
                'manufacturing_date': selected_batch.get('manufacturing_date'),
                'batch_price': selected_batch.get('batch_price')
            },
            'batch_data': calculated_batches
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error processing batch selection: {str(e)}',
            'batch_data': []
        }

# =============================================================================
# OFFER MANAGEMENT API FUNCTIONS - SIMPLIFIED
# =============================================================================

@frappe.whitelist()
def validate_offer_coupon(offer_data):
    """Simple coupon validation"""
    if isinstance(offer_data, str):
        offer_data = json.loads(offer_data)
    
    if not offer_data.get('coupon_based'):
        return {'valid': True}
    
    coupon_code = offer_data.get('coupon')
    if not coupon_code:
        return {'valid': False, 'message': 'Coupon required'}
    
    try:
        coupon = frappe.get_doc('POS Coupon', coupon_code)
        if coupon.disabled or (coupon.maximum_use > 0 and coupon.used >= coupon.maximum_use):
            return {'valid': False, 'message': 'Coupon not available'}
        return {'valid': True}
    except:
        return {'valid': False, 'message': 'Invalid coupon'}

@frappe.whitelist()
def check_offer_conditions(offer_data, qty, amount):
    """Check if qty/amount meets offer conditions"""
    if isinstance(offer_data, str):
        offer_data = json.loads(offer_data)
    
    # Simple validation - same logic as Vue checkOfferEligibility
    checks = {
        'min_qty': flt(offer_data.get('min_qty', 0)) <= 0 or qty >= flt(offer_data.get('min_qty', 0)),
        'max_qty': flt(offer_data.get('max_qty', 0)) <= 0 or qty <= flt(offer_data.get('max_qty', 0)),
        'min_amt': flt(offer_data.get('min_amt', 0)) <= 0 or amount >= flt(offer_data.get('min_amt', 0)),
        'max_amt': flt(offer_data.get('max_amt', 0)) <= 0 or amount <= flt(offer_data.get('max_amt', 0))
    }
    
    return {'apply': all(checks.values()), 'conditions': checks}

@frappe.whitelist()
def process_item_offer(offer_data, items_data):
    """Simplified offer processing - mirrors original Vue logic"""
    if isinstance(offer_data, str):
        offer_data = json.loads(offer_data)
    if isinstance(items_data, str):
        items_data = json.loads(items_data)
    
    # Check coupon first
    coupon_check = validate_offer_coupon(offer_data)
    if not coupon_check['valid']:
        return {'success': False, 'message': coupon_check.get('message')}
    
    if offer_data.get('apply_on') != 'Item Code':
        return {'success': False, 'message': 'Only Item Code offers supported'}
    
    target_item = offer_data.get('item')
    eligible_items = []
    
    for item in items_data:
        # Skip offer items and non-matching items
        if item.get('posa_is_offer') or item.get('item_code') != target_item:
            continue
            
        # Skip if price offer already applied
        if (offer_data.get('offer') == 'Item Price' and item.get('posa_offer_applied')):
            continue
        
        # Calculate quantities
        qty = flt(item.get('qty', 1)) or 1
        stock_qty = flt(item.get('stock_qty', qty)) or qty
        amount = stock_qty * flt(item.get('price_list_rate', 0))
        
        # Check conditions
        conditions = check_offer_conditions(offer_data, stock_qty, amount)
        if conditions['apply']:
            eligible_items.append(item.get('posa_row_id'))
    
    if not eligible_items:
        return {'success': True, 'offer': None}
    
    # Return offer with eligible items
    offer_result = offer_data.copy()
    offer_result['items'] = eligible_items
    
    return {'success': True, 'offer': offer_result}

# =============================================================================
# FUNCTIONS COPIED FROM get_draft_invoices.py
# =============================================================================

@frappe.whitelist()
def get_draft_invoices(pos_opening_shift):
    """
    Get draft invoices for a specific POS opening shift
    
    Args:
        pos_opening_shift: POS Opening Shift name
    
    Returns:
        List of draft Sales Invoice documents
    """
    invoices_list = frappe.get_list(
        "Sales Invoice",
        filters={
            "posa_pos_opening_shift": pos_opening_shift,
            "docstatus": 0,
            "posa_is_printed": 0,
        },
        fields=["name"],
        limit_page_length=0,
        order_by="creation desc",
    )
    data = []
    for invoice in invoices_list:
        data.append(frappe.get_cached_doc("Sales Invoice", invoice["name"]))
    return data
