# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, comma_or, nowdate, getdate
from frappe.model.document import Document
import sys


class OverAllowanceError(frappe.ValidationError):
    pass


def validate_status(status, options):
    try:
        print(f"[INFO] Validating status: {status} against options: {options}")
        if status not in options:
            print(f"[ERROR] Status '{status}' is not in options: {options}")
            frappe.throw(_("Status must be one of {0}").format(comma_or(options)))
    except Exception as e:
        print(f"[ERROR] Exception in validate_status: {e}")
        raise


status_map = {
    "POS Opening Shift": [
        ["Draft", None],
        ["Open", "eval:self.docstatus == 1 and not self.pos_closing_shift"],
        ["Closed", "eval:self.docstatus == 1 and self.pos_closing_shift"],
        ["Cancelled", "eval:self.docstatus == 2"],
    ]
}


class StatusUpdater(Document):

    def set_status(self, update=False, status=None, update_modified=True):
        print(f"[INFO] set_status called with update={update}, status={status}, update_modified={update_modified}")
        try:
            if self.is_new():
                print("[INFO] Document is new. Checking for amended_from.")
                if self.get('amended_from'):
                    self.status = 'Draft'
                    print("[INFO] Status set to Draft due to amended_from.")
                return

            if self.doctype in status_map:
                _status = self.status
                if status and update:
                    print(f"[INFO] Updating status in DB to: {status}")
                    self.db_set("status", status)

                sl = status_map[self.doctype][:]
                sl.reverse()
                for s in sl:
                    if not s[1]:
                        self.status = s[0]
                        print(f"[INFO] Status set to: {s[0]}")
                        break
                    elif s[1].startswith("eval:"):
                        try:
                            result = frappe.safe_eval(s[1][5:], None, {"self": self.as_dict(), "getdate": getdate,
                                                                       "nowdate": nowdate, "get_value": frappe.db.get_value})
                            print(f"[INFO] Evaluated {s[1]} to {result}")
                            if result:
                                self.status = s[0]
                                print(f"[INFO] Status set to: {s[0]}")
                                break
                        except Exception as e:
                            print(f"[ERROR] Exception in safe_eval: {e}")
                            raise
                    elif getattr(self, s[1])():
                        self.status = s[0]
                        print(f"[INFO] Status set to: {s[0]}")
                        break

                if self.status != _status and self.status not in ("Cancelled", "Partially Ordered",
                                                                  "Ordered", "Issued", "Transferred"):
                    print(f"[INFO] Adding comment for status: {self.status}")
                    self.add_comment("Label", _(self.status))

                if update:
                    print(f"[INFO] Updating status in DB to: {self.status}")
                    self.db_set('status', self.status, update_modified=update_modified)
        except Exception as e:
            print(f"[ERROR] Exception in set_status: {e}")
            raise


class POSOpeningShift(StatusUpdater):
    def validate(self):
        print(f"[INFO] validate called for POSOpeningShift: {self.name if hasattr(self, 'name') else ''}", file=sys.stdout)
        try:
            self.validate_pos_profile_and_cashier()
            self.validate_pos_shift()
            self.set_status()
        except Exception as e:
            print(f"[ERROR] Exception in validate: {e}", file=sys.stderr)
            raise

    def validate_pos_profile_and_cashier(self):
        print(f"[INFO] validate_pos_profile_and_cashier called for POSOpeningShift: {self.name if hasattr(self, 'name') else ''}", file=sys.stdout)
        try:
            if self.company != frappe.db.get_value("POS Profile", self.pos_profile, "company"):
                print(f"[ERROR] POS Profile {self.pos_profile} does not belong to company {self.company}", file=sys.stderr)
                frappe.throw(_("POS Profile {} does not belongs to company {}".format(self.pos_profile, self.company)))

            if not cint(frappe.db.get_value("User", self.user, "enabled")):
                print(f"[ERROR] User {self.user} has been disabled.", file=sys.stderr)
                frappe.throw(_("User {} has been disabled. Please select valid user/cashier".format(self.user)))

            # Verify that the user is registered in POS Profile
            if self.pos_profile and self.user:
                user_exists = frappe.db.exists("POS Profile User", {
                    "parent": self.pos_profile,
                    "user": self.user
                })

                if not user_exists:
                    print(f"[ERROR] User {self.user} is not assigned to POS Profile {self.pos_profile}", file=sys.stderr)
                    frappe.throw(_("User {} is not registered in POS Profile {}. Please select a user registered in the profile".format(self.user, self.pos_profile)))
        except Exception as e:
            print(f"[ERROR] Exception in validate_pos_profile_and_cashier: {e}", file=sys.stderr)
            raise

    def validate_pos_shift(self):
        """
        Validate POS Opening Shift specific rules
        """
        print(f"[INFO] validate_pos_shift called for POSOpeningShift: {self.name if hasattr(self, 'name') else ''}", file=sys.stdout)
        try:
            # Validate company
            if not self.company:
                frappe.throw(_("Company is required"))
            
            # Validate POS Profile
            if not self.pos_profile:
                frappe.throw(_("POS Profile is required"))
            
            # Validate user
            if not self.user:
                frappe.throw(_("User is required"))
            
            # Validate opening balance details
            if not self.balance_details:
                frappe.throw(_("Opening balance details are required"))
            
            # Flexible validation - allow zero opening balance
            total_opening_amount = 0
            negative_amounts = 0
            
            for detail in self.balance_details:
                amount = frappe.utils.flt(detail.amount) if detail.amount else 0
                if amount > 0:
                    total_opening_amount += amount
                elif amount < 0:
                    negative_amounts += abs(amount)
            
            # Allow zero opening balance (for digital stores)
            # But prevent negative amounts
            if negative_amounts > 0:
                frappe.throw(_("Opening cash amount cannot be negative"))
            
            # Removed mandatory positive amount validation
            # Allow opening shift with zero or positive balance
            # if total_opening_amount <= 0:
            #     frappe.throw(_("Opening cash amount must be greater than zero"))
                
        except Exception as e:
            print(f"[ERROR] Exception in validate_pos_shift: {e}", file=sys.stderr)
            raise

    def on_submit(self):
        print(f"[INFO] on_submit called for POSOpeningShift: {self.name if hasattr(self, 'name') else ''}", file=sys.stdout)
        try:
            self.set_status(update=True)
        except Exception as e:
            print(f"[ERROR] Exception in on_submit: {e}", file=sys.stderr)
            raise


@frappe.whitelist()
def get_profile_users(doctype, txt, searchfield, start, page_len, filters):
    """Retrieve users registered in POS Profile"""
    try:
        pos_profile = filters.get("parent")

        # Use frappe.get_all instead of direct SQL
        users = frappe.get_all(
            "POS Profile User",
            filters={
                "parent": pos_profile,
                "user": ["like", f"%{txt}%"]
            },
            fields=["user"],
            order_by="user",
            limit_start=start,
            limit_page_length=page_len
        )

        # Convert result to required format
        return [[user.user] for user in users]
    except Exception as e:
        print(f"[ERROR] Exception in get_profile_users: {e}")
        raise


# ===== API FUNCTIONS =====

def update_opening_shift_data(data, pos_profile):
    """
    Helper function to update opening shift data
    """
    try:
        data["pos_profile"] = frappe.get_doc("POS Profile", pos_profile)
        data["company"] = frappe.get_doc("Company", data["pos_profile"].company)
        allow_negative_stock = frappe.get_value(
            "Stock Settings", None, "allow_negative_stock"
        )
        data["stock_settings"] = {}
        data["stock_settings"].update({"allow_negative_stock": allow_negative_stock})
    except Exception as e:
        pass


@frappe.whitelist()
def create_opening_voucher(pos_profile, company, balance_details):
    """
    POST - Create new POS Opening Shift
    """
    import json
    
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


@frappe.whitelist()
def get_current_shift_name():
    """
    GET - Get current user's open POS Opening Shift basic info
    """
    try:
        user = frappe.session.user

        # Find latest open shift for this user
        rows = frappe.get_all(
            "POS Opening Shift",
            filters={
                "user": user,
                "docstatus": 1,
                "status": "Open",
            },
            fields=["name", "company", "period_start_date", "pos_profile", "user"],
            order_by="period_start_date desc",
            limit=1,
        )

        if not rows:
            return {
                "success": False,
                "message": "No active shift found",
                "data": None,
            }

        row = rows[0]
        # Ensure period_start_date is serializable
        if row.get("period_start_date"):
            row["period_start_date"] = str(row["period_start_date"])

        result = {
            "success": True,
            "data": row,
        }
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting current shift: {str(e)}",
            "data": None,
        }


@frappe.whitelist()
def get_user_shift_invoice_count(pos_profile, pos_opening_shift):
    """
    GET - Get user shift invoice count
    """
    try:
        count = frappe.db.count("Sales Invoice", {
            "posa_pos_opening_shift": pos_opening_shift,
            "docstatus": 1
        })
        return count
        
    except Exception as e:
        return 0
