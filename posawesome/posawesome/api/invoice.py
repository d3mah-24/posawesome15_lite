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
from posawesome.posawesome.doctype.delivery_charges.delivery_charges import (
    get_applicable_delivery_charges,
    get_applicable_delivery_charges as _get_applicable_delivery_charges,
)


def validate(doc, method):
    validate_shift(doc)
    auto_set_delivery_charges(doc)
    calc_delivery_charges(doc)
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


def auto_set_delivery_charges(doc):
    if not doc.pos_profile:
        return
    if not frappe.get_cached_value("POS Profile", doc.pos_profile, "posa_auto_set_delivery_charges"):
        return

    delivery_charges = get_applicable_delivery_charges(
        doc.company,
        doc.pos_profile,
        doc.customer,
        doc.shipping_address_name,
        doc.posa_delivery_charges,
        restrict=True,
    )

    if doc.posa_delivery_charges:
        if doc.posa_delivery_charges_rate:
            return
        else:
            if len(delivery_charges) > 0:
                doc.posa_delivery_charges_rate = delivery_charges[0].rate
    else:
        if len(delivery_charges) > 0:
            doc.posa_delivery_charges = delivery_charges[0].name
            doc.posa_delivery_charges_rate = delivery_charges[0].rate
        else:
            doc.posa_delivery_charges = None
            doc.posa_delivery_charges_rate = None


def calc_delivery_charges(doc):
    if not doc.pos_profile:
        return

    old_doc = None
    calculate_taxes_and_totals = False
    if not doc.is_new():
        old_doc = doc.get_doc_before_save()
        if not doc.posa_delivery_charges and not old_doc.posa_delivery_charges:
            return
    else:
        if not doc.posa_delivery_charges:
            return
    if not doc.posa_delivery_charges:
        doc.posa_delivery_charges_rate = 0

    charges_doc = None
    if doc.posa_delivery_charges:
        charges_doc = frappe.get_cached_doc("Delivery Charges", doc.posa_delivery_charges)
        doc.posa_delivery_charges_rate = charges_doc.default_rate
        charges_profile = next((i for i in charges_doc.profiles if i.pos_profile == doc.pos_profile), None)
        if charges_profile:
            doc.posa_delivery_charges_rate = charges_profile.rate

    if old_doc and old_doc.posa_delivery_charges:
        old_charges = next(
            (
                i
                for i in doc.taxes
                if i.charge_type == "Actual" and i.description == old_doc.posa_delivery_charges
            ),
            None,
        )
        if old_charges:
            doc.taxes.remove(old_charges)
            calculate_taxes_and_totals = True

    if doc.posa_delivery_charges:
        doc.append(
            "taxes",
            {
                "charge_type": "Actual",
                "description": doc.posa_delivery_charges,
                "tax_amount": doc.posa_delivery_charges_rate,
                "cost_center": charges_doc.cost_center,
                "account_head": charges_doc.shipping_account,
            },
        )
        calculate_taxes_and_totals = True

    if calculate_taxes_and_totals:
        doc.calculate_taxes_and_totals()


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
    البحث عن الفواتير التي يمكن إرجاعها.
    يستبعد:
    - الفواتير المرتجعة مسبقاً (is_return=1)
    - الفواتير الملغية
    - الفواتير المسودة
    - الفواتير غير POS
    - الفواتير التي لها مرتجعات مسبقاً
    """
    filters = {
        "docstatus": 1,  # فواتير مسلمة فقط
        "is_return": 0,  # استبعاد الفواتير المرتجعة مسبقاً (هذا هو الفلتر الأساسي)
        "is_pos": 1,     # فواتير POS فقط
        "status": ["not in", ["Cancelled", "Draft"]]  # استبعاد الفواتير الملغية والمسودات
    }
    
    if invoice_name:
        filters["name"] = ["like", f"%{invoice_name}%"]
    if company:
        filters["company"] = company

    # الحصول على قائمة الفواتير المؤهلة مع حد لمنع تحميل الكثير
    invoices_list = frappe.get_list(
        "Sales Invoice",
        filters=filters,
        fields=["name"],
        limit_page_length=10,  # حد أقصى 10 فواتير لمنع مشاكل الأداء
        order_by="creation desc",
    )
    
    data = []
    
    for invoice in invoices_list:
        # فحص مزدوج: التأكد من أن هذه الفاتورة ليس لها مرتجع مسبقاً
        existing_returns = frappe.get_all(
            "Sales Invoice",
            filters={
                "return_against": invoice["name"],
                "docstatus": 1,
                "is_return": 1
            },
            fields=["name"]
        )
        
        # تضمين الفواتير التي ليس لها مرتجعات بعد فقط
        if not existing_returns:
            try:
                invoice_doc = frappe.get_doc("Sales Invoice", invoice["name"])
                # التأكد من تحميل الأصناف
                if not invoice_doc.items:
                    invoice_doc.load_from_db()
                data.append(invoice_doc)
            except Exception as e:
                # تخطي الفواتير التي لا يمكن تحميلها
                frappe.log_error(f"خطأ في تحميل الفاتورة {invoice['name']}: {str(e)}")
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
    data = json.loads(data)
    if data.get("name"):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                invoice_doc = frappe.get_doc("Sales Invoice", data.get("name"))
                invoice_doc.update(data)
                break  # Success, exit the retry loop
            except frappe.DoesNotExistError:
                # Document was deleted, create a new one
                invoice_doc = frappe.get_doc(data)
                break
            except frappe.ValidationError as e:
                if "Document has been modified" in str(e) and retry_count < max_retries - 1:
                    # Document was modified by another process, reload and retry
                    frappe.db.rollback()
                    retry_count += 1
                    frappe.log_error(f"Document modification conflict, retry {retry_count}/{max_retries}")
                    continue
                else:
                    raise e
    else:
        invoice_doc = frappe.get_doc(data)

    # Set currency from data before set_missing_values
    # Validate return items if this is a return invoice
    if (data.get("is_return") or invoice_doc.is_return) and invoice_doc.get("return_against"):
        validation = validate_return_items(
            invoice_doc.return_against, [d.as_dict() for d in invoice_doc.items]
        )
        if not validation.get("valid"):
            frappe.throw(validation.get("message"))
    selected_currency = data.get("currency")

    # Set missing values first
    invoice_doc.set_missing_values()

    # Ensure selected currency is preserved after set_missing_values
    if selected_currency:
        invoice_doc.currency = selected_currency
        # Get default conversion rate from ERPNext if currency is different from company currency
        if invoice_doc.currency != frappe.get_cached_value(
            "Company", invoice_doc.company, "default_currency"
        ):
            company_currency = frappe.get_cached_value("Company", invoice_doc.company, "default_currency")

            # Determine price list currency
            price_list_currency = data.get("price_list_currency")
            if not price_list_currency and invoice_doc.get("selling_price_list"):
                price_list_currency = frappe.db.get_value(
                    "Price List", invoice_doc.selling_price_list, "currency"
                )
            if not price_list_currency:
                price_list_currency = company_currency

            conversion_rate = 1
            if invoice_doc.currency != company_currency:
                conversion_rate = get_exchange_rate(
                    invoice_doc.currency,
                    company_currency,
                    invoice_doc.posting_date,
                )

            plc_conversion_rate = 1
            if price_list_currency != invoice_doc.currency:
                plc_conversion_rate = get_exchange_rate(
                    price_list_currency,
                    invoice_doc.currency,
                    invoice_doc.posting_date,
                )

            invoice_doc.conversion_rate = conversion_rate
            invoice_doc.plc_conversion_rate = plc_conversion_rate
            invoice_doc.price_list_currency = price_list_currency

            # Update rates and amounts for all items using division
            for item in invoice_doc.items:
                if item.price_list_rate:
                    # If exchange rate is 285 PKR = 1 USD
                    # To convert PKR to USD: divide by exchange rate
                    # Example: 100 PKR / 285 = 0.35 USD
                    item.base_price_list_rate = flt(
                        item.price_list_rate * (conversion_rate / plc_conversion_rate),
                        item.precision("base_price_list_rate"),
                    )
                if item.rate:
                    item.base_rate = flt(item.rate * conversion_rate, item.precision("base_rate"))
                if item.amount:
                    item.base_amount = flt(item.amount * conversion_rate, item.precision("base_amount"))

            # Update payment amounts
            for payment in invoice_doc.payments:
                payment.base_amount = flt(payment.amount * conversion_rate, payment.precision("base_amount"))

            # Update invoice level amounts
            invoice_doc.base_total = flt(
                invoice_doc.total * conversion_rate, invoice_doc.precision("base_total")
            )
            invoice_doc.base_net_total = flt(
                invoice_doc.net_total * conversion_rate,
                invoice_doc.precision("base_net_total"),
            )
            invoice_doc.base_grand_total = flt(
                invoice_doc.grand_total * conversion_rate,
                invoice_doc.precision("base_grand_total"),
            )
            invoice_doc.base_rounded_total = flt(
                invoice_doc.rounded_total * conversion_rate,
                invoice_doc.precision("base_rounded_total"),
            )
            invoice_doc.base_in_words = money_in_words(
                invoice_doc.base_rounded_total, invoice_doc.company_currency
            )

            # Update data to be sent back to frontend

            data["conversion_rate"] = conversion_rate
            data["plc_conversion_rate"] = plc_conversion_rate

    allow_zero_rated_items = frappe.get_cached_value(
        "POS Profile", invoice_doc.pos_profile, "posa_allow_zero_rated_items"
    )
    for item in invoice_doc.items:
        if not item.rate or item.rate == 0:
            if allow_zero_rated_items:
                item.price_list_rate = 0.00
                item.is_free_item = 1
            else:
                frappe.throw(_("Rate cannot be zero for item {0}").format(item.item_code))
        else:
            item.is_free_item = 0

        add_taxes_from_tax_template(item, invoice_doc)

    inclusive = frappe.get_cached_value("POS Profile", invoice_doc.pos_profile, "posa_tax_inclusive")
    if invoice_doc.get("taxes"):
        for tax in invoice_doc.taxes:
            if tax.charge_type == "Actual":
                tax.included_in_print_rate = 0
            else:
                tax.included_in_print_rate = 1 if inclusive else 0
    invoice_doc.flags.ignore_permissions = True
    frappe.flags.ignore_account_permission = True
    invoice_doc.docstatus = 0
    invoice_doc.save()

    # Return both the invoice doc and the updated data
    response = invoice_doc.as_dict()
    response["conversion_rate"] = invoice_doc.conversion_rate
    response["plc_conversion_rate"] = invoice_doc.plc_conversion_rate
    return response


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
