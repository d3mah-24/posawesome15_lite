# -*- coding: utf-8 -*-
# Copyright (c) 2021, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class POSOffer(Document):
    def validate(self):
        try:
            frappe.log_error(f"[DEBUG] POS Offer validation - Name: {self.name}, Title: {self.title}, Offer Type: {self.offer_type}", "POS Offer Debug")

            # Validate required fields
            if not self.title:
                frappe.log_error(f"[ERROR] POS Offer '{self.name}' missing title", "POS Offer Error")
                frappe.throw("Title is required")

            if not self.offer_type:
                frappe.log_error(f"[ERROR] POS Offer '{self.name}' missing offer_type", "POS Offer Error")
                frappe.throw("Offer Type is required")

            if not self.company:
                frappe.log_error(f"[ERROR] POS Offer '{self.name}' missing company", "POS Offer Error")
                frappe.throw("Company is required")

            # Validate discount fields
            if self.discount_type == "Discount Percentage" and not self.discount_percentage:
                frappe.log_error(f"[ERROR] POS Offer '{self.name}' missing discount_percentage", "POS Offer Error")
                frappe.throw("Discount Percentage is required when Discount Type is 'Discount Percentage'")

            frappe.log_error(f"[DEBUG] POS Offer '{self.name}' validation successful", "POS Offer Debug")

        except Exception as e:
            frappe.log_error(f"[ERROR] POS Offer validation failed: {str(e)}", "POS Offer Error")
            raise

    def before_save(self):
        try:
            frappe.log_error(f"[DEBUG] POS Offer before_save - Name: {self.name}", "POS Offer Debug")
        except Exception as e:
            frappe.log_error(f"[ERROR] POS Offer before_save failed: {str(e)}", "POS Offer Error")

    def after_insert(self):
        try:
            frappe.log_error(f"[DEBUG] POS Offer created - Name: {self.name}", "POS Offer Debug")
        except Exception as e:
            frappe.log_error(f"[ERROR] POS Offer after_insert failed: {str(e)}", "POS Offer Error")

    def on_update(self):
        try:
            frappe.log_error(f"[DEBUG] POS Offer updated - Name: {self.name}", "POS Offer Debug")
        except Exception as e:
            frappe.log_error(f"[ERROR] POS Offer on_update failed: {str(e)}", "POS Offer Error")
