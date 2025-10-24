# -*- coding: utf-8 -*-
# Copyright (c) 2021, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class POSOffer(Document):
    def validate(self):
        # Validate required fields
        if not self.title:
            frappe.throw("Title is required")

        if not self.offer_type:
            frappe.throw("Offer Type is required")

        if not self.company:
            frappe.throw("Company is required")

        # Validate discount fields
        if self.discount_type == "Discount Percentage" and not self.discount_percentage:
            frappe.throw("Discount Percentage is required when Discount Type is 'Discount Percentage'")

        # Validate date range
        if self.valid_from and self.valid_upto:
            from frappe.utils import getdate
            if getdate(self.valid_from) > getdate(self.valid_upto):
                frappe.throw("Valid From date cannot be after Valid Upto date")

        # Validate offer_type specific fields
        if self.offer_type == "item_code" and not self.item_code:
            frappe.throw("Item Code is required when Offer Type is 'Item Code'")

        if self.offer_type == "item_group" and not self.item_group:
            frappe.throw("Item Group is required when Offer Type is 'Item Group'")

        if self.offer_type == "brand" and not self.brand:
            frappe.throw("Brand is required when Offer Type is 'Brand'")

        if self.offer_type == "customer" and not self.customer:
            frappe.throw("Customer is required when Offer Type is 'Customer'")

        if self.offer_type == "customer_group" and not self.customer_group:
            frappe.throw("Customer Group is required when Offer Type is 'Customer Group'")
