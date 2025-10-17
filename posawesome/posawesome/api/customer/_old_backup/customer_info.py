# -*- coding: utf-8 -*-
"""
Customer Info Functions
Handles customer information retrieval
"""

from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def get_customer_info(customer):
    try:
        customer_doc = frappe.get_doc("Customer", customer)

        res = {"loyalty_points": None, "conversion_factor": None}

        res["email_id"] = customer_doc.email_id
        res["mobile_no"] = customer_doc.mobile_no
        res["image"] = customer_doc.image
        res["loyalty_program"] = customer_doc.loyalty_program
        res["customer_price_list"] = customer_doc.default_price_list
        res["customer_group"] = customer_doc.customer_group
        res["customer_type"] = customer_doc.customer_type
        res["territory"] = customer_doc.territory
        res["birthday"] = customer_doc.posa_birthday
        res["gender"] = customer_doc.gender
        res["tax_id"] = customer_doc.tax_id
        res["posa_discount"] = customer_doc.posa_discount
        res["name"] = customer_doc.name
        res["customer_name"] = customer_doc.customer_name
        res["customer_group_price_list"] = frappe.get_value(
            "Customer Group", customer_doc.customer_group, "default_price_list"
        )

        if customer_doc.loyalty_program:
            lp_details = get_loyalty_program_details_with_points(
                customer_doc.name,
                customer_doc.loyalty_program,
                silent=True,
                include_expired_entry=False,
            )
            res["loyalty_points"] = lp_details.get("loyalty_points")
            res["conversion_factor"] = lp_details.get("conversion_factor")

        return res
        
    except Exception as e:
        raise
