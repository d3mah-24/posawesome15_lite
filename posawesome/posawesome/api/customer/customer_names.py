# -*- coding: utf-8 -*-
"""
Customer Names Functions
Handles customer names operations
"""

from __future__ import unicode_literals

import json
import frappe
from .customer_groups import get_customer_group_condition


@frappe.whitelist()
def get_customer_names(pos_profile):
    pos_profile = json.loads(pos_profile)
    condition = ""
    condition += get_customer_group_condition(pos_profile)
    # Improve customer query with maximum performance limit
    customers = frappe.db.sql(
        """
        SELECT name, mobile_no, email_id, tax_id, customer_name, primary_address
        FROM `tabCustomer`
        WHERE {0}
        ORDER by name
        LIMIT 5000
        """.format(
            condition
        ),
        as_dict=1,
    )
    return customers
