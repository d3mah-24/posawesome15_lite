# 📝 Task 1: Auto Delete Draft Invoices

**💰 Budget**: $10

**👨‍💻 Developer**: Oscar

**💳 Payment**: ✅ Payed USDT crypto

**🎯 Priority**: 🔥 High

**📊 Status**: ✅ Completed

**🔧 Feature**: `pos_profile_posa_auto_delete_draft_invoices`

**📖 Description**:

- Auto delete draft invoices after closing shift
- For same invoices created during the shift

**⚙️ Implementation Notes**:

- ✅ Add checkbox field to POS Profile
  (`posa_auto_delete_draft_invoices`)
- 🔗 Hook into shift closing process
- 🗑️ Delete only draft Sales Invoices created during the shift
- 📋 Follow POS Awesome API patterns:
  - One function per file

**🛠️ Technical Requirements**:

- 📁 API file:
  `posawesome/api/pos_closing_shift/auto_delete_drafts.py`
- 🔧 Function: `@frappe.whitelist() def auto_delete_draft_invoices
  (shift_name)`
- 🔍 Query: Find drafts where `posa_pos_opening_shift = %s AND
  docstatus = 0`
- 🗑️ Use `frappe.delete_doc("Sales Invoice", invoice_name,
  ignore_permissions=True)`
- 🔗 Add to closing shift workflow
- If POS Profile checkbox enabled
