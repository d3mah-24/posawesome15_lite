#### Backend Policy
**Code Structure:**
```
posawesome/api/
└── [doctype_name]/
    ├── get_[doctype].py        # Single record with specific fields
    ├── get_many_[doctype]s.py  # Multiple records with filters
    ├── post_[doctype].py       # Create new record
    ├── update_[doctype].py     # Update existing record
    └── delete_[doctype].py     # Delete record
```

**Implementation Requirements:**
- **Database Field Optimization**: MUST specify required fields only
- **NO `SELECT *` queries allowed**
- Use `fields=["field1", "field2"]` parameter
- Example: `frappe.get_doc("Item", name, fields=["name", "item_code", "item_name"])`

**Performance Optimization:**
- Use `ignore_version=True` for faster saves
- Implement immediate `frappe.db.commit()`
- Target: < 100ms response time without caching
- Handle `QueryTimeoutError` gracefully

**Error Handling:**
- Implement `frappe.log_error` only for actual errors
- NO logging for successful operations
- Handle database timeouts gracefully
- Example: `frappe.log_error("Error in get_customer: {0}".format(str(e)))`


### 🚀 Development Policies
**Mandatory compliance for all code contributions:**
- **Frontend:** 3-API batch queue system (CREATE → UPDATE → SUBMIT)
- **Backend:** Frappe ORM only with specific field selection
- **Performance:** < 100ms response time, lightweight components
- **Structure:** DocType-based API organization, no caching except temp batches

