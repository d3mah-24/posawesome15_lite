import frappe
from frappe.utils import nowdate, flt

@frappe.whitelist()
def get_current_cash_total():
    """
    Get the total amount of cash payments for the current shift
    Uses the same logic as closing shift to calculate cash totals
    """
    try:
        # Get the current open shift
        opening_shift = frappe.get_all(
            "POS Opening Shift",
            filters={"status": "Open"},
            fields=["name", "pos_profile"],
            order_by="period_start_date desc",
            limit=1
        )
        
        if not opening_shift:
            return {"total": 0}
        
        pos_opening_shift_name = opening_shift[0].name
        pos_profile = opening_shift[0].pos_profile
        
        # Get cash mode of payment from POS Profile
        cash_mode_of_payment = frappe.get_value(
            "POS Profile",
            pos_profile,
            "posa_cash_mode_of_payment"
        )
        if not cash_mode_of_payment:
            cash_mode_of_payment = "Cash"
        
        # Get all submitted invoices for this shift
        invoices = frappe.db.sql("""
            SELECT name, change_amount
            FROM `tabSales Invoice`
            WHERE docstatus = 1 
            AND posa_pos_opening_shift = %s
        """, (pos_opening_shift_name,), as_dict=1)
        
        total_cash = 0
        
        # Calculate cash payments for each invoice
        for invoice in invoices:
            # Get payments for this invoice
            payments = frappe.db.sql("""
                SELECT amount, mode_of_payment
                FROM `tabSales Invoice Payment`
                WHERE parent = %s
                AND mode_of_payment = %s
            """, (invoice.name, cash_mode_of_payment), as_dict=1)
            
            for payment in payments:
                # Subtract change amount from cash payment (same as closing shift logic)
                amount = flt(payment.amount) - flt(invoice.change_amount)
                total_cash += amount
        
        return {"total": total_cash}
    
    except Exception as e:
        frappe.log_error(f"[get_current_cash_total.py][get_current_cash_total] Error: {str(e)}")
        return {"total": 0, "error": str(e)}