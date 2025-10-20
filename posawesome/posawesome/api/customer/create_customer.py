# -*- coding: utf-8 -*-
"""
Post Customer API
Handles creating new customers with validation and data processing
"""

from __future__ import unicode_literals

import json
import frappe
from frappe import _
from datetime import datetime
import re


@frappe.whitelist(allow_guest=True)
def create_customer(
    customer_name,
    company=None,
    pos_profile=None,
    mobile_no=None,
    email_id=None,
    tax_id=None,
    birthday=None,
    gender=None,
    customer_group="Individual",
    territory="All Territories",
    customer_type="Individual",
    discount_percentage=0
):
    """
    Create a new customer with comprehensive validation and data processing.
    
    Args:
        customer_name (str): Customer name (required)
        company (str): Company name
        pos_profile (str): POS Profile for default values
        mobile_no (str): Mobile phone number
        email_id (str): Email address
        tax_id (str): Tax identification number
        birthday (str): Birthday in various formats
        gender (str): Gender (Male/Female/Other)
        customer_group (str): Customer group (default: Individual)
        territory (str): Territory (default: All Territories)
        customer_type (str): Customer type (default: Individual)
        discount_percentage (float): Default discount percentage
        
    Returns:
        dict: Created customer document with all details
    """
    try:
        # Validate required fields
        if not customer_name or not customer_name.strip():
            frappe.throw(_("Customer name is required"))
            
        customer_name = customer_name.strip()
        
        # Check permissions
        if not frappe.has_permission("Customer", "create"):
            frappe.throw(_("You don't have permission to create customers"), frappe.PermissionError)
        
        # Check for duplicate customer by name
        if frappe.db.exists("Customer", {"customer_name": customer_name}):
            frappe.throw(_("Customer with name '{0}' already exists").format(customer_name))
        
        # Check for duplicate by mobile number if provided
        if mobile_no and mobile_no.strip():
            existing_customer = frappe.db.get_value("Customer", {"mobile_no": mobile_no.strip()}, "name")
            if existing_customer:
                frappe.throw(_("Customer with mobile number '{0}' already exists: {1}").format(mobile_no, existing_customer))
        
        # Process birthday date
        formatted_birthday = None
        if birthday:
            formatted_birthday = _parse_birthday(birthday)
        
        # Get default values from POS Profile if provided
        pos_defaults = {}
        if pos_profile:
            try:
                pos_doc = frappe.get_cached_doc("POS Profile", pos_profile)
                if hasattr(pos_doc, 'customer_group') and pos_doc.customer_group:
                    pos_defaults["customer_group"] = pos_doc.customer_group
                if hasattr(pos_doc, 'territory') and pos_doc.territory:
                    pos_defaults["territory"] = pos_doc.territory
            except Exception as pos_error:
                # Silent fallback - no logging needed for optional POS defaults
                pass
        
        # Create customer document
        customer_doc = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name,
            "customer_type": customer_type or "Individual",
            "customer_group": pos_defaults.get("customer_group", customer_group) or "Individual",
            "territory": pos_defaults.get("territory", territory) or "All Territories",
            "mobile_no": mobile_no.strip() if mobile_no else "",
            "email_id": email_id.strip() if email_id else "",
            "tax_id": tax_id.strip() if tax_id else "",
            "gender": gender if gender in ["Male", "Female", "Other"] else "",
            "disabled": 0
        })
        
        # Add POS-specific fields if they exist
        if hasattr(customer_doc, 'posa_birthday') and formatted_birthday:
            customer_doc.posa_birthday = formatted_birthday
        if hasattr(customer_doc, 'posa_discount') and discount_percentage:
            customer_doc.posa_discount = float(discount_percentage)
            
        # Insert the customer
        customer_doc.insert(ignore_permissions=False)
        
        # Create gift coupon if applicable
        _create_gift_coupon(customer_doc)
        
        frappe.db.commit()
        
        # Return the created customer with all details
        return customer_doc.as_dict()
        
    except Exception as e:
        frappe.logger().error(f"Error in post_customer: {str(e)}")
        frappe.logger().error(frappe.get_traceback())
        
        # Re-raise the error with a user-friendly message
        if "already exists" in str(e):
            raise  # Re-raise duplicate errors as-is
        else:
            frappe.throw(_("Error creating customer: {0}").format(str(e)))


def _parse_birthday(birthday_input):
    """
    Parse birthday from various input formats to YYYY-MM-DD format.
    
    Args:
        birthday_input (str): Birthday in various formats
        
    Returns:
        str: Formatted birthday as YYYY-MM-DD or None if invalid
    """
    if not birthday_input:
        return None
        
    try:
        # Handle JavaScript Date string format (e.g., "Mon Oct 17 2025 00:00:00 GMT+0000")
        if 'GMT' in birthday_input or 'UTC' in birthday_input:
            match = re.search(r'(\w{3})\s+(\w{3})\s+(\d{1,2})\s+(\d{4})', birthday_input)
            if match:
                day_name, month_name, day, year = match.groups()
                month_map = {
                    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                }
                if month_name in month_map:
                    month = month_map[month_name]
                    day = day.zfill(2)
                    return f"{year}-{month}-{day}"
        
        # Handle ISO date format (YYYY-MM-DD)
        if re.match(r'^\d{4}-\d{2}-\d{2}', birthday_input):
            date_part = birthday_input[:10]  # Take only YYYY-MM-DD part
            datetime.strptime(date_part, '%Y-%m-%d')  # Validate
            return date_part
        
        # Handle MM/DD/YYYY format
        if re.match(r'^\d{1,2}/\d{1,2}/\d{4}', birthday_input):
            dt = datetime.strptime(birthday_input[:10], '%m/%d/%Y')
            return dt.strftime('%Y-%m-%d')
        
        # Handle DD/MM/YYYY format
        if re.match(r'^\d{1,2}/\d{1,2}/\d{4}', birthday_input):
            dt = datetime.strptime(birthday_input[:10], '%d/%m/%Y')
            return dt.strftime('%Y-%m-%d')
        
        # Handle DD-MM-YYYY format
        if re.match(r'^\d{1,2}-\d{1,2}-\d{4}', birthday_input):
            dt = datetime.strptime(birthday_input[:10], '%d-%m-%Y')
            return dt.strftime('%Y-%m-%d')
            
        # Invalid format - return None silently
        return None
        
    except ValueError:
        return None
    except Exception as e:
        frappe.logger().error(f"Error parsing birthday: {e}")
        return None


def _create_gift_coupon(customer_doc):
    """
    Create gift coupon for new customer if configured.
    
    Args:
        customer_doc: Customer document that was just created
    """
    try:
        # Check if customer has a company and if gift coupons are enabled
        if hasattr(customer_doc, 'posa_referral_company') and customer_doc.posa_referral_company:
            company_doc = frappe.get_cached_doc("Company", customer_doc.posa_referral_company)
            
            # Check if company has gift coupon settings enabled
            if hasattr(company_doc, 'posa_enable_gift_coupons') and company_doc.posa_enable_gift_coupons:
                # Check if POS Coupon doctype exists
                if frappe.db.exists("DocType", "POS Coupon"):
                    coupon = frappe.new_doc("POS Coupon")
                    coupon.customer = customer_doc.name
                    coupon.company = customer_doc.posa_referral_company
                    coupon.coupon_type = "Gift Card"
                    
                    # Set default gift coupon amount if configured
                    if hasattr(company_doc, 'posa_default_gift_amount') and company_doc.posa_default_gift_amount:
                        coupon.coupon_amount = company_doc.posa_default_gift_amount
                    
                    # Generate coupon code
                    coupon.coupon_code = f"WELCOME-{customer_doc.name}"
                    
                    try:
                        coupon.insert(ignore_permissions=True)
                        # Gift coupon created successfully - no logging needed
                    except Exception as coupon_error:
                        # Silent fallback - gift coupon is optional
                        pass
                        
    except Exception as e:
        # Silent fallback - gift coupon creation is optional
        pass
    
