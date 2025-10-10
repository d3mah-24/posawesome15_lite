# -*- coding: utf-8 -*-
"""
POS Profile API
Handles all POS Profile related operations
"""

from __future__ import unicode_literals

import frappe

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
        frappe.log_error(message="\n".join(debug_log), title="POS Profile API - تشخيص شامل")
        # لا نمسح debug_log هنا - نتركه للتجميع


@frappe.whitelist()
def get_opening_dialog_data():
    """
    GET - Get opening dialog data
    """
    try:
        log_debug("=== بدء جلب بيانات حوار الافتتاح ===")
        
        data = {}
        data["companies"] = frappe.get_list("Company", limit_page_length=0, order_by="name")
        log_debug(f"تم جلب {len(data['companies'])} شركة")
        
        data["pos_profiles_data"] = frappe.get_list(
            "POS Profile",
            filters={"disabled": 0},
            fields=["name", "company", "currency"],
            limit_page_length=0,
            order_by="name",
        )
        log_debug(f"تم جلب {len(data['pos_profiles_data'])} POS Profile")

        pos_profiles_list = []
        for i in data["pos_profiles_data"]:
            pos_profiles_list.append(i.name)

        payment_method_table = "POS Payment Method"
        data["payments_method"] = frappe.get_list(
            payment_method_table,
            filters={"parent": ["in", pos_profiles_list]},
            fields=["*"],
            limit_page_length=0,
            order_by="parent",
            ignore_permissions=True,
        )
        log_debug(f"تم جلب {len(data['payments_method'])} طريقة دفع")
        
        # Set currency from pos profile
        for mode in data["payments_method"]:
            mode["currency"] = frappe.get_cached_value(
                "POS Profile", mode["parent"], "currency"
            )

        log_debug("=== انتهاء جلب بيانات حوار الافتتاح بنجاح ===")
        
        # حفظ كل التشخيص في سجل واحد
        save_debug_log()
        
        return data
        
    except Exception as e:
        log_debug(f"❌ خطأ في جلب بيانات حوار الافتتاح: {str(e)}")
        # حفظ التشخيص حتى في حالة الخطأ
        save_debug_log()
        frappe.log_error(f"Error getting opening dialog data: {str(e)}")
        return {}


@frappe.whitelist()
def get_profile_details(profile_name):
    """
    GET - Get POS Profile details
    """
    try:
        log_debug(f"=== بدء جلب تفاصيل POS Profile ===")
        log_debug(f"Profile Name: {profile_name}")
        
        profile = frappe.get_doc("POS Profile", profile_name)
        log_debug(f"تم جلب POS Profile: {profile.name}")
        
        log_debug("=== انتهاء جلب تفاصيل POS Profile بنجاح ===")
        
        # حفظ كل التشخيص في سجل واحد
        save_debug_log()
        
        return profile.as_dict()
        
    except Exception as e:
        log_debug(f"❌ خطأ في جلب تفاصيل POS Profile: {str(e)}")
        # حفظ التشخيص حتى في حالة الخطأ
        save_debug_log()
        frappe.log_error(f"Error getting profile details: {str(e)}")
        return None


@frappe.whitelist()
def get_profile_payment_methods(profile_name):
    """
    GET - Get POS Profile payment methods
    """
    try:
        log_debug(f"=== بدء جلب طرق الدفع ===")
        log_debug(f"Profile Name: {profile_name}")
        
        payment_methods = frappe.get_all(
            "POS Payment Method",
            filters={"parent": profile_name},
            fields=["*"],
            order_by="idx"
        )
        
        log_debug(f"تم جلب {len(payment_methods)} طريقة دفع")
        log_debug("=== انتهاء جلب طرق الدفع بنجاح ===")
        
        # حفظ كل التشخيص في سجل واحد
        save_debug_log()
        
        return payment_methods
        
    except Exception as e:
        log_debug(f"❌ خطأ في جلب طرق الدفع: {str(e)}")
        # حفظ التشخيص حتى في حالة الخطأ
        save_debug_log()
        frappe.log_error(f"Error getting profile payment methods: {str(e)}")
        return []


@frappe.whitelist()
def get_profile_warehouses(profile_name):
    """
    GET - Get POS Profile warehouses
    """
    try:
        log_debug(f"=== بدء جلب المستودعات ===")
        log_debug(f"Profile Name: {profile_name}")
        
        warehouses = frappe.get_all(
            "POS Profile Warehouse",
            filters={"parent": profile_name},
            fields=["warehouse"],
            order_by="idx"
        )
        
        log_debug(f"تم جلب {len(warehouses)} مستودع")
        log_debug("=== انتهاء جلب المستودعات بنجاح ===")
        
        # حفظ كل التشخيص في سجل واحد
        save_debug_log()
        
        return [w.warehouse for w in warehouses]
        
    except Exception as e:
        log_debug(f"❌ خطأ في جلب المستودعات: {str(e)}")
        # حفظ التشخيص حتى في حالة الخطأ
        save_debug_log()
        frappe.log_error(f"Error getting profile warehouses: {str(e)}")
        return []


@frappe.whitelist()
def get_profile_users(profile_name):
    """
    GET - Get POS Profile users
    """
    try:
        log_debug(f"=== بدء جلب المستخدمين ===")
        log_debug(f"Profile Name: {profile_name}")
        
        users = frappe.get_all(
            "POS Profile User",
            filters={"parent": profile_name},
            fields=["user"],
            order_by="idx"
        )
        
        log_debug(f"تم جلب {len(users)} مستخدم")
        log_debug("=== انتهاء جلب المستخدمين بنجاح ===")
        
        # حفظ كل التشخيص في سجل واحد
        save_debug_log()
        
        return [u.user for u in users]
        
    except Exception as e:
        log_debug(f"❌ خطأ في جلب المستخدمين: {str(e)}")
        # حفظ التشخيص حتى في حالة الخطأ
        save_debug_log()
        frappe.log_error(f"Error getting profile users: {str(e)}")
        return []


@frappe.whitelist()
def validate_profile_access(profile_name, user):
    """
    POST - Validate if user has access to POS Profile
    """
    try:
        log_debug(f"=== بدء التحقق من صلاحية الوصول ===")
        log_debug(f"Profile Name: {profile_name}")
        log_debug(f"User: {user}")
        
        # Check if user is assigned to this profile
        user_exists = frappe.db.exists("POS Profile User", {
            "parent": profile_name,
            "user": user
        })
        
        if not user_exists:
            log_debug(f"❌ المستخدم {user} غير مسجل في POS Profile {profile_name}")
            # حفظ كل التشخيص في سجل واحد
            save_debug_log()
            return {
                "success": False,
                "message": f"User {user} is not assigned to POS Profile {profile_name}"
            }
        
        # Check if profile is enabled
        profile_enabled = frappe.get_cached_value("POS Profile", profile_name, "disabled")
        
        if profile_enabled:
            log_debug(f"❌ POS Profile {profile_name} معطل")
            # حفظ كل التشخيص في سجل واحد
            save_debug_log()
            return {
                "success": False,
                "message": f"POS Profile {profile_name} is disabled"
            }
        
        log_debug("✅ تم منح الصلاحية بنجاح")
        log_debug("=== انتهاء التحقق من صلاحية الوصول بنجاح ===")
        
        # حفظ كل التشخيص في سجل واحد
        save_debug_log()
        
        return {
            "success": True,
            "message": "Access granted"
        }
        
    except Exception as e:
        log_debug(f"❌ خطأ في التحقق من صلاحية الوصول: {str(e)}")
        # حفظ التشخيص حتى في حالة الخطأ
        save_debug_log()
        frappe.log_error(f"Error validating profile access: {str(e)}")
        return {
            "success": False,
            "message": f"Error validating access: {str(e)}"
        }


@frappe.whitelist()
def get_default_payment_from_pos_profile(pos_profile, company):
    """
    Get default payment method from POS Profile
    """
    try:
        log_debug(f"=== بدء جلب طريقة الدفع الافتراضية ===")
        log_debug(f"POS Profile: {pos_profile}")
        log_debug(f"Company: {company}")
        
        if not pos_profile:
            log_debug("❌ لا يوجد POS Profile")
            # حفظ كل التشخيص في سجل واحد
            save_debug_log()
            return None
            
        # Get POS Profile document
        pos_profile_doc = frappe.get_doc("POS Profile", pos_profile)
        log_debug(f"تم جلب POS Profile: {pos_profile_doc.name}")
        log_debug(f"عدد طرق الدفع: {len(pos_profile_doc.payments)}")
        
        # Find default payment method
        for payment in pos_profile_doc.payments:
            log_debug(f"فحص طريقة الدفع: {payment.mode_of_payment}, default: {payment.default}")
            if payment.default:
                # Get account for this payment method
                account = get_payment_account(payment.mode_of_payment, company)
                log_debug(f"✅ تم العثور على طريقة الدفع الافتراضية: {payment.mode_of_payment}")
                log_debug(f"✅ الحساب: {account.get('account', '')}")
                log_debug("=== انتهاء جلب طريقة الدفع الافتراضية بنجاح ===")
                # حفظ كل التشخيص في سجل واحد
                save_debug_log()
                return {
                    "mode_of_payment": payment.mode_of_payment,
                    "account": account.get("account", "")
                }
        
        # If no default found, use first payment method
        if pos_profile_doc.payments:
            first_payment = pos_profile_doc.payments[0]
            account = get_payment_account(first_payment.mode_of_payment, company)
            log_debug(f"⚠️ لم يتم العثور على طريقة دفع افتراضية، استخدام الأولى: {first_payment.mode_of_payment}")
            log_debug(f"✅ الحساب: {account.get('account', '')}")
            log_debug("=== انتهاء جلب طريقة الدفع الافتراضية بنجاح ===")
            # حفظ كل التشخيص في سجل واحد
            save_debug_log()
            return {
                "mode_of_payment": first_payment.mode_of_payment,
                "account": account.get("account", "")
            }
            
        log_debug("❌ لا توجد طرق دفع في POS Profile")
        log_debug("=== انتهاء جلب طريقة الدفع الافتراضية ===")
        # حفظ كل التشخيص في سجل واحد
        save_debug_log()
        return None
        
    except Exception as e:
        log_debug(f"❌ خطأ في جلب طريقة الدفع الافتراضية: {str(e)}")
        # حفظ التشخيص حتى في حالة الخطأ
        save_debug_log()
        frappe.log_error(f"Error getting default payment from POS Profile: {str(e)}")
        return None


def get_payment_account(mode_of_payment, company):
    """
    Get account for mode of payment
    """
    try:
        log_debug(f"=== بدء جلب حساب طريقة الدفع ===")
        log_debug(f"Mode of Payment: {mode_of_payment}")
        log_debug(f"Company: {company}")
        
        # Try to get account from Mode of Payment Account table
        account = frappe.db.get_value(
            "Mode of Payment Account",
            {"parent": mode_of_payment, "company": company},
            "default_account"
        )
        
        if account:
            log_debug(f"✅ تم العثور على الحساب من Mode of Payment Account: {account}")
            return {"account": account}
        
        # Try to get account from POS Payment Method
        account = frappe.db.get_value(
            "POS Payment Method",
            {"mode_of_payment": mode_of_payment},
            "account"
        )
        
        if account:
            log_debug(f"✅ تم العثور على الحساب من POS Payment Method: {account}")
            return {"account": account}
        
        # Try to get company's default cash account
        cash_account = frappe.db.get_value(
            "Company",
            company,
            "default_cash_account"
        )
        
        if cash_account:
            log_debug(f"✅ تم العثور على الحساب النقدي الافتراضي: {cash_account}")
            return {"account": cash_account}
        
        # Try to get company's default bank account
        bank_account = frappe.db.get_value(
            "Company",
            company,
            "default_bank_account"
        )
        
        if bank_account:
            log_debug(f"✅ تم العثور على الحساب المصرفي الافتراضي: {bank_account}")
            return {"account": bank_account}
        
        # Try to get any cash account for the company
        cash_account = frappe.db.get_value(
            "Account",
            {"account_type": "Cash", "company": company, "is_group": 0},
            "name"
        )
        
        if cash_account:
            log_debug(f"✅ تم العثور على أي حساب نقدي: {cash_account}")
            return {"account": cash_account}
        
        # Try to get any bank account for the company
        bank_account = frappe.db.get_value(
            "Account",
            {"account_type": "Bank", "company": company, "is_group": 0},
            "name"
        )
        
        if bank_account:
            log_debug(f"✅ تم العثور على أي حساب مصرفي: {bank_account}")
            return {"account": bank_account}
        
        log_debug("❌ لم يتم العثور على أي حساب مناسب")
        return {"account": ""}
        
    except Exception as e:
        log_debug(f"❌ خطأ في جلب حساب طريقة الدفع: {str(e)}")
        frappe.log_error(f"Error getting payment account: {str(e)}")
        return {"account": ""}


# دالة لحفظ جميع التشخيصات في Error Log
def show_all_debug_logs():
    """حفظ جميع التشخيصات المجمعة في Error Log"""
    global debug_log
    if debug_log:
        # حفظ في سجل الأخطاء فقط
        frappe.log_error(message="\n".join(debug_log), title="POS Profile API - جميع التشخيصات المجمعة")
        
        # مسح التشخيصات بعد الحفظ
        debug_log = []
