# -*- coding: utf-8 -*-
# Copyright (c) 2020, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt
from datetime import datetime, time as dtime, timedelta


class POSClosingShift(Document):
    def validate(self):
        # Validate shift closing allowed time window based on POS Profile settings
        self._validate_shift_closing_window()

        user = frappe.get_all(
            "POS Closing Shift",
            filters={
                "user": self.user,
                "docstatus": 1,
                "pos_opening_shift": self.pos_opening_shift,
                "name": ["!=", self.name],
            },
        )

        if user:
            frappe.throw(
                _(
                    "POS Closing Shift {} against {} between selected period".format(
                        frappe.bold("already exists"), frappe.bold(self.user)
                    )
                ),
                title=_("Invalid Period"),
            )

        if frappe.db.get_value("POS Opening Shift", self.pos_opening_shift, "status") != "Open":
            frappe.throw(
                _("Selected POS Opening Shift should be open."),
                title=_("Invalid Opening Entry"),
            )
        self.update_payment_reconciliation()

    def _parse_time(self, value):
        """Parse a value to datetime.time supporting str and time inputs."""
        if not value:
            return None
        if isinstance(value, dtime):
            return value
        # Support formats with microseconds
        for fmt in ("%H:%M:%S.%f", "%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(str(value), fmt).time()
            except Exception:
                continue
        return None

    def _validate_shift_closing_window(self):
        """Validate if period_end_date is within allowed closing window for POS Profile."""
        if not self.pos_profile or not self.period_end_date:
            return

        profile = frappe.get_doc("POS Profile", self.pos_profile)
        
        # Check if closing time control is enabled
        if not profile.get("posa_closing_time_control"):
            return  # Skip validation if time control is not enabled

        shift_opening_time = profile.get("posa_closing_time_start")
        shift_closing_time = profile.get("posa_closing_time_end")

        if not shift_opening_time or not shift_closing_time:
            return  # No restriction if not configured

        # Parse times
        start_time = self._parse_time(shift_opening_time)
        end_time = self._parse_time(shift_closing_time)

        if not start_time or not end_time:
            return

        # Get period_end_date as datetime
        period_end_dt = frappe.utils.get_datetime(self.period_end_date)

        # Create datetime objects for comparison
        start_dt = period_end_dt.replace(hour=start_time.hour, minute=start_time.minute, second=start_time.second, microsecond=start_time.microsecond)
        end_dt = period_end_dt.replace(hour=end_time.hour, minute=end_time.minute, second=end_time.second, microsecond=end_time.microsecond)

        # If start_time > end_time, assume end_time is next day
        if start_time > end_time:
            end_dt = end_dt + timedelta(days=1)

        # Check if period_end_dt is within [start_dt, end_dt]
        allowed = start_dt <= period_end_dt <= end_dt

        if not allowed:
            start_str = start_time.strftime("%H:%M")
            end_str = end_time.strftime("%H:%M")
            if start_time > end_time:
                end_str += " (next day)"
            frappe.throw(
                _("Closing shift is not allowed at this time. Closing is allowed only between {0} and {1}").format(start_str, end_str),
                title=_("Closing Time Not Allowed")
            )

    def update_payment_reconciliation(self):
        # update the difference values in Payment Reconciliation child table
        # get default precision for site
        precision = frappe.get_cached_value("System Settings", None, "currency_precision") or 3
        for d in self.payment_reconciliation:
            d.difference = +flt(d.closing_amount, precision) - flt(d.expected_amount, precision)

    def on_submit(self):
        opening_entry = frappe.get_doc("POS Opening Shift", self.pos_opening_shift)
        opening_entry.pos_closing_shift = self.name
        opening_entry.set_status()
        opening_entry.save()

    def on_cancel(self):
        if frappe.db.exists("POS Opening Shift", self.pos_opening_shift):
            opening_entry = frappe.get_doc("POS Opening Shift", self.pos_opening_shift)
            if opening_entry.pos_closing_shift == self.name:
                opening_entry.pos_closing_shift = ""
                opening_entry.set_status()
            opening_entry.save()

    @frappe.whitelist()
    def get_payment_reconciliation_details(self):
            currency = frappe.get_cached_value("Company", self.company, "default_currency")
            return frappe.render_template(
                "posawesome/posawesome/doctype/pos_closing_shift/closing_shift_details.html",
                {"data": self, "currency": currency},
            )
