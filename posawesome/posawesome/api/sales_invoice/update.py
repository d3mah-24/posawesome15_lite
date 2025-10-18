# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import time
import frappe
from frappe import _
from frappe.utils import flt
from frappe.exceptions import ValidationError

@frappe.whitelist()
def update_invoice(data):
    log = frappe.logger()
    try:
        data = json.loads(data) if isinstance(data, str) else data
    except (json.JSONDecodeError, ValueError) as e:
        frappe.throw(_("Invalid JSON data: {0}").format(str(e)))

    try:
        if not data.get("name"):
            frappe.log_error("update_invoice: No name in data", "Invoice Update Error")
            frappe.throw(_("Invoice name is required for update operations"))

        log.info(f"[update_invoice] start: {data.get('name')}")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                doc = frappe.get_doc("Sales Invoice", data.get("name"))
                break
            except frappe.QueryTimeoutError:
                if attempt == max_retries - 1:
                    raise
                time.sleep(0.1 * (attempt + 1))

        if doc.docstatus != 0:
            frappe.throw(_("Cannot update submitted invoice"))

        if data.get("items") is not None and not data.get("items"):
            try:
                frappe.delete_doc("Sales Invoice", doc.name, ignore_permissions=True, force=True)
                frappe.db.commit()
                log.info(f"[update_invoice] deleted invoice {doc.name}")
                return {"message": "Invoice deleted successfully"}
            except frappe.QueryTimeoutError:
                frappe.log_error("Delete timeout - marking as cancelled", "Invoice Delete Timeout")
                doc.workflow_state = "Cancelled"
                doc.save(ignore_version=True)
                frappe.db.commit()
                return {"message": "Invoice cancelled due to delete timeout"}

        doc.update(data)
        max_save_retries = 2
        saved = False
        for save_attempt in range(max_save_retries):
            try:
                doc.save(ignore_version=True)
                frappe.db.commit()
                saved = True
                log.info(f"[update_invoice] saved invoice {doc.name} on attempt {save_attempt+1}")
                break
            except ValidationError as ve:
                msg = str(ve)
                log.warning(f"[update_invoice] ValidationError: {msg}")
                if "POS Opening Shift is required" in msg or "POS Opening Shift is required for POS Invoice" in msg:
                    if data.get("pos_opening_shift"):
                        doc.pos_opening_shift = data.get("pos_opening_shift")
                        log.info(f"[update_invoice] set pos_opening_shift from payload: {doc.pos_opening_shift}")
                    else:
                        open_shift = frappe.get_all("POS Opening Shift", filters={"status": "Open"}, limit=1)
                        if open_shift:
                            doc.pos_opening_shift = open_shift[0].get("name")
                            log.info(f"[update_invoice] set pos_opening_shift to open shift: {doc.pos_opening_shift}")
                        else:
                            recent = frappe.get_all("POS Opening Shift", order_by="creation desc", limit=1)
                            if recent:
                                doc.pos_opening_shift = recent[0].get("name")
                                log.info(f"[update_invoice] set pos_opening_shift to recent shift: {doc.pos_opening_shift}")
                    try:
                        doc.save(ignore_version=True)
                        frappe.db.commit()
                        saved = True
                        log.info(f"[update_invoice] saved invoice after setting pos_opening_shift: {doc.name}")
                        break
                    except Exception as retry_exc:
                        log.error(f"[update_invoice] retry save after setting shift failed: {str(retry_exc)[:200]}")
                        raise
                else:
                    raise
            except frappe.QueryTimeoutError:
                if save_attempt == max_save_retries - 1:
                    raise
                time.sleep(0.05 * (save_attempt + 1))
            except Exception as e:
                log.error(f"[update_invoice] save failed: {str(e)[:200]}")
                raise

        if not saved:
            frappe.log_error("Invoice save failed after retries", "Invoice Save Failed")
            return {"message": "Failed to save invoice after retries", "status": "error"}

        try:
            def _extract_payment_amount(row):
                for fld in ("amount", "paid_amount", "received_amount", "allocated_amount", "amount_paid", "payment_amount"):
                    val = getattr(row, fld, None)
                    if val is not None:
                        return flt(val)
                return 0.0

            total_from_payments = 0.0
            payments_table = getattr(doc, "payments", None)
            if payments_table:
                for p in payments_table:
                    total_from_payments += _extract_payment_amount(p)

            rounded_total = flt(getattr(doc, "rounded_total", None) or getattr(doc, "grand_total", 0.0))
            rounding_adj = flt(getattr(doc, "rounding_adjustment", 0.0))

            precision = 2
            try:
                if getattr(doc, "currency", None):
                    val = frappe.db.get_value("Currency", doc.currency, "fraction_units")
                    precision = int(val) if val is not None else precision
            except Exception:
                precision = 2

            smallest_unit = 1 / (10 ** precision)
            threshold = max(abs(rounding_adj), smallest_unit)

            if total_from_payments:
                diff = abs(flt(total_from_payments) - rounded_total)
                if diff <= threshold:
                    paid_amount_to_set = round(rounded_total, precision)
                    doc.db_set("paid_amount", paid_amount_to_set, update_modified=False)
                    if hasattr(doc, "outstanding_amount"):
                        doc.db_set("outstanding_amount", 0.0, update_modified=False)
                    frappe.db.commit()
                    log.info(f"[update_invoice] rounded match: set paid_amount={paid_amount_to_set}, outstanding=0 for {doc.name}")
                    doc = frappe.get_doc("Sales Invoice", doc.name)
                else:
                    paid_amount_to_set = round(total_from_payments, precision)
                    doc.db_set("paid_amount", paid_amount_to_set, update_modified=False)
                    outstanding = flt(getattr(doc, "grand_total", rounded_total)) - paid_amount_to_set
                    if outstanding < 0:
                        outstanding = 0.0
                    if hasattr(doc, "outstanding_amount"):
                        doc.db_set("outstanding_amount", outstanding, update_modified=False)
                    frappe.db.commit()
                    log.info(f"[update_invoice] set paid_amount={paid_amount_to_set}, outstanding={outstanding} for {doc.name}")
                    doc = frappe.get_doc("Sales Invoice", doc.name)
        except Exception as paid_exc:
            frappe.log_error(f"Paid amount recalculation failed: {str(paid_exc)[:200]}", "Invoice Paid Amount Recalc")
            log.error(f"[update_invoice] Paid amount recalculation failed: {str(paid_exc)[:200]}")

        from .invoice_response import get_minimal_invoice_response
        resp = get_minimal_invoice_response(doc)
        log.info(f"[update_invoice] finished: {doc.name}")
        return resp

    except frappe.exceptions.QueryTimeoutError:
        frappe.log_error("Query timeout in update_invoice - rapid operations detected", "Invoice Update Timeout")
        return {"message": "عملية التحديث قيد المعالجة، يرجى الانتظار قليلاً", "status": "processing", "retry_recommended": True}

    except frappe.exceptions.TimestampMismatchError:
        frappe.log_error("Timestamp mismatch - using ignore_version", "Invoice Update Timestamp")
        try:
            doc = frappe.get_doc("Sales Invoice", data.get("name"))
            doc.update(data)
            doc.save(ignore_version=True)
            frappe.db.commit()
            from .invoice_response import get_minimal_invoice_response
            return get_minimal_invoice_response(doc)
        except Exception as retry_error:
            frappe.log_error(f"Ignore version save failed: {str(retry_error)[:80]}", "Invoice Update Ignore Version Failed")
            raise

    except Exception as e:
        frappe.log_error(f"Update error: {str(e)[:100]}", "Invoice Update Error")
        log.error(f"[update_invoice] fatal error: {str(e)[:200]}")
        raise
