# -*- coding: utf-8 -*-
"""
Create Customer Functions
Handles customer creation and updates
"""

from __future__ import unicode_literals

import json
import frappe
from frappe import _
from .set_customer_info import set_customer_info


@frappe.whitelist()
def create_customer(
    customer_id,
    customer_name,
    company,
    pos_profile_doc,
    tax_id=None,
    mobile_no=None,
    email_id=None,
    referral_code=None,
    birthday=None,
    customer_group=None,
    territory=None,
    customer_type=None,
    gender=None,
    method="create",
):
    pos_profile = json.loads(pos_profile_doc)
    if method == "create":
        if frappe.db.exists("Customer", {"customer_name": customer_name}):
            frappe.throw(_("Customer already registered"))

        # Convert birthday from various formats to YYYY-MM-DD
        formatted_birthday = None
        if birthday:
            try:
                from datetime import datetime
                import re
                # Handle different date formats
                if 'GMT' in birthday or 'UTC' in birthday:
                    match = re.search(r'(\w{3})\s+(\w{3})\s+(\d{1,2})\s+(\d{4})', birthday)
                    if match:
                        day_name, month_name, day, year = match.groups()
                        month_map = {
                            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                        }
                        month = month_map.get(month_name, '01')
                        formatted_birthday = f"{year}-{month}-{day.zfill(2)}"
                    else:
                        formatted_birthday = None
                elif 'T' in birthday:
                    dt = datetime.fromisoformat(birthday.replace('Z', '+00:00'))
                    formatted_birthday = dt.strftime('%Y-%m-%d')
                else:
                    formatted_birthday = birthday
            except Exception:
                formatted_birthday = None

        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": customer_name,
                "posa_referral_company": company,
                "tax_id": tax_id,
                "mobile_no": mobile_no,
                "email_id": email_id,
                "posa_referral_code": referral_code,
                "posa_birthday": formatted_birthday,
                "customer_type": customer_type,
                "gender": gender,
            }
        )
        customer.customer_group = customer_group or "All Customer Groups"
        customer.territory = territory or "All Territories"
        customer.save()
        return customer

    elif method == "update":
        # Get existing customer document
        customer_doc = frappe.get_doc("Customer", customer_id)
        
        # Update basic customer fields
        customer_doc.customer_name = customer_name
        customer_doc.posa_referral_company = company
        customer_doc.tax_id = tax_id
        customer_doc.posa_referral_code = referral_code
        
        # Set birthday (convert various date formats to YYYY-MM-DD)
        if birthday:
            try:
                from datetime import datetime
                import re
                
                # Handle different date formats
                if 'GMT' in birthday or 'UTC' in birthday:
                    # JavaScript Date string (Thu Sep 18 2025 00:00:00 GMT+0300)
                    # Extract date parts using regex
                    match = re.search(r'(\w{3})\s+(\w{3})\s+(\d{1,2})\s+(\d{4})', birthday)
                    if match:
                        day_name, month_name, day, year = match.groups()
                        month_map = {
                            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                        }
                        month = month_map.get(month_name, '01')
                        birthday = f"{year}-{month}-{day.zfill(2)}"
                    else:
                        birthday = None
                elif 'T' in birthday:
                    # ISO format (1989-02-05T21:00:00.000Z)
                    dt = datetime.fromisoformat(birthday.replace('Z', '+00:00'))
                    birthday = dt.strftime('%Y-%m-%d')
                else:
                    # Already in YYYY-MM-DD format or other format
                    pass
                    
                customer_doc.posa_birthday = birthday
            except Exception as e:
                customer_doc.posa_birthday = None
        else:
            customer_doc.posa_birthday = None
            
        customer_doc.customer_type = customer_type
        customer_doc.territory = territory
        customer_doc.customer_group = customer_group
        customer_doc.gender = gender
        customer_doc.save()
        
        # Update Contact fields if values provided
        if mobile_no:
            set_customer_info(customer_doc.name, "mobile_no", mobile_no)
        if email_id:
            set_customer_info(customer_doc.name, "email_id", email_id)
        if gender:
            set_customer_info(customer_doc.name, "gender", gender)
        
        # Update local object with new values before returning
        customer_doc.mobile_no = mobile_no
        customer_doc.email_id = email_id
        customer_doc.gender = gender
        
        return customer_doc
