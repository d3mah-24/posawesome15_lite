# Copyright (c) 2021, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe import _
from posawesome.posawesome.doctype.referral_code.referral_code import (
    create_referral_code,
)
from erpnext.accounts.doctype.pos_profile.pos_profile import get_child_nodes
from erpnext.accounts.doctype.loyalty_program.loyalty_program import (
    get_loyalty_program_details_with_points,
)

# متغير عام لتجميع التشخيصات
debug_log = []

def log_debug(message):
    """إضافة رسالة للتشخيص العام"""
    debug_log.append(str(message))

def clear_debug_log():
    """مسح التشخيص العام"""
    global debug_log
    debug_log = []

def save_debug_log():
    """حفظ التشخيص العام في سجل واحد"""
    global debug_log
    if debug_log:
        # حفظ في سجل الأخطاء فقط (بدون مسح)
        frappe.log_error(message="\n".join(debug_log), title="Customer API - تشخيص شامل")
        # لا نمسح debug_log هنا - نتركه للتجميع


def after_insert(doc, method):
    create_customer_referral_code(doc)
    create_gift_coupon(doc)


def validate(doc, method):
    validate_referral_code(doc)


def create_customer_referral_code(doc):
    if doc.posa_referral_company:
        company = frappe.get_cached_doc("Company", doc.posa_referral_company)
        if not company.posa_auto_referral:
            return
        create_referral_code(
            doc.posa_referral_company,
            doc.name,
            company.posa_customer_offer,
            company.posa_primary_offer,
            company.posa_referral_campaign,
        )


def create_gift_coupon(doc):
    if doc.posa_referral_code:
        coupon = frappe.new_doc("POS Coupon")
        coupon.customer = doc.name
        coupon.referral_code = doc.posa_referral_code
        coupon.create_coupon_from_referral()


def validate_referral_code(doc):
    referral_code = doc.posa_referral_code
    exist = None
    if referral_code:
        exist = frappe.db.exists("Referral Code", referral_code)
        if not exist:
            exist = frappe.db.exists("Referral Code", {"referral_code": referral_code})
        if not exist:
            frappe.throw(_("This Referral Code {0} not exists").format(referral_code))


def get_customer_groups(pos_profile):
    customer_groups = []
    if pos_profile.get("customer_groups"):
        # Get items based on the item groups defined in the POS profile
        for data in pos_profile.get("customer_groups"):
            customer_groups.extend(
                [
                    "%s" % frappe.db.escape(d.get("name"))
                    for d in get_child_nodes(
                        "Customer Group", data.get("customer_group")
                    )
                ]
            )

    return list(set(customer_groups))


def get_customer_group_condition(pos_profile):
    cond = "disabled = 0"
    customer_groups = get_customer_groups(pos_profile)
    if customer_groups:
        cond = " customer_group in (%s)" % (", ".join(["%s"] * len(customer_groups)))

    return cond % tuple(customer_groups)


@frappe.whitelist()
def get_pos_coupon(coupon, customer, company):
    res = check_coupon_code(coupon, customer, company)
    return res

@frappe.whitelist()
def get_active_gift_coupons(customer, company):
    coupons = []
    coupons_data = frappe.get_all(
        "POS Coupon",
        filters={
            "company": company,
            "coupon_type": "Gift Card",
            "customer": customer,
            "used": 0,
        },
        fields=["coupon_code"],
    )
    if len(coupons_data):
        coupons = [i.coupon_code for i in coupons_data]
    return coupons

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


@frappe.whitelist()
def get_available_credit(customer, company):
    total_credit = []

    outstanding_invoices = frappe.get_all(
        "Sales Invoice",
        {
            "outstanding_amount": ["<", 0],
            "docstatus": 1,
            "is_return": 0,
            "customer": customer,
            "company": company,
        },
        ["name", "outstanding_amount"],
    )

    for row in outstanding_invoices:
        outstanding_amount = -(row.outstanding_amount)
        row = {
            "type": "Invoice",
            "credit_origin": row.name,
            "total_credit": outstanding_amount,
            "credit_to_redeem": 0,
        }

        total_credit.append(row)

    advances = frappe.get_all(
        "Payment Entry",
        {
            "unallocated_amount": [">", 0],
            "party_type": "Customer",
            "party": customer,
            "company": company,
            "docstatus": 1,
        },
        ["name", "unallocated_amount"],
    )

    for row in advances:
        row = {
            "type": "Advance",
            "credit_origin": row.name,
            "total_credit": row.unallocated_amount,
            "credit_to_redeem": 0,
        }

        total_credit.append(row)

    return total_credit


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


@frappe.whitelist()
def set_customer_info(customer, fieldname, value=""):
    # Handle loyalty program separately (Customer only)
    if fieldname == "loyalty_program":
        frappe.db.set_value("Customer", customer, "loyalty_program", value)
        return

    # Get primary contact ID from Customer
    contact = (
        frappe.get_cached_value("Customer", customer, "customer_primary_contact") or ""
    )

    # Case 1: Contact exists - update existing contact
    if contact:
        contact_doc = frappe.get_doc("Contact", contact)
        
        # Update email in both Contact and Customer
        if fieldname == "email_id":
            contact_doc.set("email_ids", [{"email_id": value, "is_primary": 1}])
            frappe.db.set_value("Customer", customer, "email_id", value)
        
        # Update mobile in both Contact and Customer
        elif fieldname == "mobile_no":
            contact_doc.set("phone_nos", [{"phone": value, "is_primary_mobile_no": 1}])
            frappe.db.set_value("Customer", customer, "mobile_no", value)
        
        # Update gender in both Contact and Customer
        elif fieldname == "gender":
            contact_doc.gender = value
            frappe.db.set_value("Customer", customer, "gender", value)
        
        contact_doc.save()

    # Case 2: No contact exists - create new contact
    else:
        contact_doc = frappe.new_doc("Contact")
        contact_doc.first_name = customer
        contact_doc.is_primary_contact = 1
        contact_doc.is_billing_contact = 1
        
        # Add mobile number to new contact
        if fieldname == "mobile_no":
            contact_doc.add_phone(value, is_primary_mobile_no=1, is_primary_phone=1)

        # Add email to new contact
        if fieldname == "email_id":
            contact_doc.add_email(value, is_primary=1)
            
        # Add gender to new contact
        if fieldname == "gender":
            contact_doc.gender = value

        # Link contact to customer
        contact_doc.append("links", {"link_doctype": "Customer", "link_name": customer})

        # Save new contact and update customer reference
        contact_doc.flags.ignore_mandatory = True
        contact_doc.save()
        frappe.set_value(
            "Customer", customer, "customer_primary_contact", contact_doc.name
        )


@frappe.whitelist()
def get_customer_addresses(customer):
    """
    Get customer addresses using Frappe ORM
    """
    if not customer:
        frappe.throw(_("Customer parameter is required"))
    
    try:
        # First get the address names linked to this customer
        dynamic_links = frappe.get_all(
            "Dynamic Link",
            filters={
                "link_doctype": "Customer",
                "link_name": customer
            },
            fields=["parent"]
        )
        
        # Extract address names
        address_names = [link.parent for link in dynamic_links]
        
        if not address_names:
            return []
        
        # Get the actual address details
        addresses = frappe.get_all(
            "Address",
            filters={
                "name": ["in", address_names],
                "disabled": 0
            },
            fields=[
                "name",
                "address_line1", 
                "address_line2",
                "address_title",
                "city",
                "state", 
                "country",
                "address_type"
            ],
            order_by="name"
        )
        
        return addresses
        
    except Exception as e:
        frappe.log_error(f"Error getting customer addresses for {customer}: {str(e)}")
        return []


@frappe.whitelist()
def make_address(args):
    args = json.loads(args)
    address = frappe.get_doc(
        {
            "doctype": "Address",
            "address_title": args.get("name"),
            "address_line1": args.get("address_line1"),
            "address_line2": args.get("address_line2"),
            "city": args.get("city"),
            "state": args.get("state"),
            "pincode": args.get("pincode"),
            "country": args.get("country"),
            "address_type": "Shipping",
            "links": [
                {"link_doctype": args.get("doctype"), "link_name": args.get("customer")}
            ],
        }
    ).insert()

    return address


@frappe.whitelist()
def get_customer_info(customer):
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


# دالة لحفظ جميع التشخيصات في Error Log
def show_all_debug_logs():
    """حفظ جميع التشخيصات المجمعة في Error Log"""
    global debug_log
    if debug_log:
        # حفظ في سجل الأخطاء فقط
        frappe.log_error(message="\n".join(debug_log), title="Customer API - جميع التشخيصات المجمعة")
        
        # مسح التشخيصات بعد الحفظ
        debug_log = []
