# AI Agent Instructions for POS Awesome Lite

## Project Philosophy

**POS Awesome Lite = Modern Vue.js Interface + Original ERPNext Engine**

This is NOT a standalone system. It's a lightweight web interface built on top of ERPNext's proven foundation, using original ERPNext patterns (sales_invoice.js) and controllers. Zero custom calculations - all framework-powered.

## Architecture Overview

### Backend: Frappe App Structure
```
posawesome/
├── posawesome/              # Main module (note: nested same name)
│   ├── api/                 # API endpoints by DocType (ONE FUNCTION PER FILE)
│   │   ├── sales_invoice/   # CRUD: create, update, submit, delete, get_return
│   │   ├── customer/        # get, get_many, create, update, addresses, coupons
│   │   ├── item/           # get_items, get_items_groups, barcode, batch
│   │   ├── pos_profile/    # get_default_payment, get_opening_dialog_data
│   │   ├── pos_offer/      # get_applicable_offers, get_offers_for_profile
│   │   ├── pos_opening_shift/ # Shift management APIs
│   │   └── pos_closing_shift/ # Shift closing + payment totals APIs
│   ├── doctype/            # Custom DocTypes (only class methods, no @frappe.whitelist())
│   └── page/               # Frappe pages (posapp entry point)
└── public/js/              # Frontend code
    ├── posawesome.bundle.js # Bundle entry: imports toConsole, posapp
    ├── onscan.js           # Barcode scanning library (moved from page/posapp/)
    └── posapp/
        ├── components/     # Vue 3 components
        │   ├── Navbar.vue  # Top nav with shift info, payment totals (💰💳)
        │   └── pos/        # POS-specific components
        │       ├── Pos.vue       # Main container
        │       ├── Invoice.vue   # Invoice management (2,357 lines - being simplified)
        │       ├── ItemsSelector.vue # Item grid with 30+ scans/sec
        │       └── Payments.vue  # Payment modes
        ├── api_mapper.js   # Central API endpoint registry (ALWAYS USE THIS)
        └── bus.js          # Event bus (mitt 3.0.1)
```

**Critical Pattern**: API functions follow strict naming: `posawesome.posawesome.api.[doctype].[operation].[operation]_[doctype]`
- Example: `posawesome.posawesome.api.sales_invoice.create.create_invoice`
- All endpoints mapped in `api_mapper.js` - **ALWAYS use API_MAP constants, never hardcode paths**
- Example: `API_MAP.POS_CLOSING_SHIFT.GET_CURRENT_CASH_TOTAL` not hardcoded string

### Frontend: Vue 3 (Pure HTML/CSS - NO Vuetify)
- **Stack**: Vue 3.4.21, mitt 3.0.1 (event bus), NO frameworks
- **Entry**: `posawesome/page/posapp/posapp.js` → loads Vue app via `new frappe.PosApp.posapp()`
- **Bundle**: `posawesome.bundle.js` imports: toConsole → posapp
- **Build**: `bench build --app posawesome` (esbuild, ~606KB JS, ~114KB CSS)

## Critical Development Patterns

### 1. 3-API Batch Queue System (MANDATORY)

**The Golden Rule**: Only 3 API calls for entire invoice lifecycle:

```javascript
// API 1: CREATE invoice (first item added)
frappe.call({ method: API_MAP.SALES_INVOICE.CREATE, args: { data: doc } });

// API 2: UPDATE invoice (batch all changes after 1s idle)
// Collect in temp cache: qty changes, discounts, payments, offers
// Wait 1 second after last operation, then send ONE batch update
frappe.call({ method: API_MAP.SALES_INVOICE.UPDATE, args: { data: doc } });

// API 3: SUBMIT & PRINT invoice (final step)
frappe.call({ method: API_MAP.SALES_INVOICE.SUBMIT, args: { invoice, data } });
```

**Implementation**:
- Use debounced auto-save: wait 1000ms idle time before UPDATE
- Group operations by DocType (item_operations, payment_operations, etc.)
- Clear temp cache after successful API response
- NO caching except temporary operation batches

### 2. Backend API Standards (MANDATORY)

**File Structure**: One function per file (STRICTLY ENFORCED)
```python
# posawesome/posawesome/api/customer/get_customer.py
@frappe.whitelist()
def get_customer(customer_id):
    # MUST use specific fields - NO SELECT * queries
    return frappe.get_doc("Customer", customer_id, 
                          fields=["name", "customer_name", "mobile_no"])
```

**Naming Convention**:
- `get_[doctype].py` - Single record with specific fields
- `get_many_[doctype]s.py` - Multiple records with filters
- `create_[doctype].py` - Create new record
- `update_[doctype].py` - Update existing record
- `delete_[doctype].py` - Delete record

**Database Query Standards**:
- **Field Selection**: ALWAYS specify fields - `frappe.get_doc("DocType", name, fields=["field1", "field2"])`
- **Table Names**: Use backticks - ``` `tabSales Invoice Payment` ```
- **Column Names**: Check actual DB column names via `DESCRIBE \`tabDocType\`;`
  - Example: `amount` NOT `paid_amount` in Sales Invoice Payment
- **SQL Queries**: Use parametrized queries with `%s` placeholders
  ```python
  frappe.db.sql("""
      SELECT SUM(amount) as total
      FROM `tabSales Invoice Payment`
      WHERE parent IN (
          SELECT name FROM `tabSales Invoice` 
          WHERE posa_pos_opening_shift = %s
          AND docstatus = 1
      )
  """, (shift_name,), as_dict=1)
  ```

**Performance Rules**:
- Target: <100ms response time
- Use `ignore_version=True` for faster saves
- Call `frappe.db.commit()` immediately after operations
- NO `frappe.log_error()` for successful operations (only for actual errors)

### 3. Event Bus Communication

**Use mitt** (imported as `evntBus` from `bus.js`):
```javascript
// Emit
evntBus.emit('add_item', item);

// Listen (in mounted() or created())
evntBus.on('add_item', this.handleAddItem);

// CRITICAL: Clean up in beforeUnmount() (Vue 3)
beforeUnmount() {
  evntBus.off('add_item', this.handleAddItem);
  // Clear ALL timers and intervals
  if (this._debounceTimer) clearTimeout(this._debounceTimer);
  if (this.cashUpdateInterval) clearInterval(this.cashUpdateInterval);
}
```

**Common Events**: 
- `add_item`, `update_customer`, `new_invoice`, `show_payment`
- `item_updated`, `register_pos_profile`, `invoice_submitted`
- `show_mesage` (note: typo is intentional in codebase)
- `update_invoice_doc`, `set_pos_opening_shift`

### 4. Console Logging Policy (STRICTLY ENFORCED)

**REMOVED**: All debug `console.log()` statements
**KEEP**: Only `console.error()` for actual errors and `console.warn()` for warnings
```javascript
// ❌ NEVER do this
console.log("Fetching data...");
console.log("Result:", data);

// ✅ ONLY for errors
console.error('Error fetching cash total:', err);
console.warn('Deprecated API usage');
```

### 5. UI Component Standards

**NO Vuetify, NO Frameworks** - Pure HTML/CSS only:
```vue
<!-- ✅ Use native HTML tables -->
<table class="data-table">
  <thead>
    <tr><th>Name</th><th>Price</th></tr>
  </thead>
  <tbody>
    <tr v-for="item in items" :key="item.name">
      <td>{{ item.name }}</td>
      <td>{{ item.price }}</td>
    </tr>
  </tbody>
</table>

<!-- ✅ Use native HTML5 inputs -->
<input type="date" v-model="date" class="custom-input" />

<!-- ❌ NEVER use Vuetify -->
<v-data-table>  <!-- NO -->
<v-date-picker> <!-- NO -->
```

**Performance Rules**:
- Virtual scrolling for lists > 50 items
- Simple component structure only
- No animations or heavy CSS
- No global library imports (except mitt, Vue)
- Target component size: < 500 lines (split if larger)

### 6. File Organization Standards

**Third-Party Libraries**:
- Place in `public/js/` folder (e.g., `onscan.js`)
- Import in `posawesome.bundle.js` entry point
- **NEVER** use Jinja2 `{% include %}` in .js files (causes TypeScript errors)

**Frappe Page Files**:
- `posapp.js` loads Vue app - keep minimal
- Use `@ts-nocheck` comment if TypeScript complains about Frappe globals

### 7. Framework Integration Points

**Frappe Hooks** (`hooks.py`):
```python
# Vue.js + libraries bundled in posawesome.bundle.js
app_include_js = [
    "posawesome.bundle.js",  # Contains: toConsole, posapp
]

# Inject JS into ERPNext forms
doctype_js = {
    "POS Profile": "public/js/pos_profile.js",
    "Sales Invoice": "public/js/invoice.js",
    "Company": "public/js/company.js",
}

# Server-side hooks
doc_events = {
    "Sales Invoice": {
        "before_submit": "posawesome.posawesome.api.sales_invoice.before_submit.before_submit",
        "before_cancel": "posawesome.posawesome.api.sales_invoice.before_cancel.before_cancel",
    }
}
```

### 8. Common Workflows

**Apply Backend Changes**:
```bash
bench restart
```

**Apply Frontend Changes**:
```bash
cd ~/frappe-bench-15
bench build --app posawesome
# OR with cache clear
bench clear-cache && bench build --app posawesome
```

**Debug Database Schema**:
```bash
bench mariadb
DESCRIBE `tabDocTypeName`;
```

**Clean Python Cache**:
```bash
find . -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} +
```

## Recent Major Changes (October 2025)

### ✅ Payment Totals in Navbar (NEW)
- **Feature**: Real-time cash 💰 and non-cash 💳 totals in navbar
- **Implementation**: Uses shift-based queries matching closing shift logic
- **APIs**: `get_current_cash_total.py`, `get_current_non_cash_total.py`
- **Updates**: On shift open, invoice submit, every 5 minutes
- **Key Learning**: Must match closing shift calculations (subtract change_amount for cash)

### ✅ Console.log Cleanup (NEW)
- **Removed**: ALL 30+ debug console.log statements
- **Files**: Navbar.vue, Invoice.vue, Pos.vue
- **Method**: Used `sed -i` commands to bulk remove
- **Build Impact**: Reduced bundle size ~2KB

### ✅ Bundle Organization (NEW)
- **onscan.js**: Moved from `page/posapp/` to `public/js/`
- **Reason**: Cleaner structure, avoid Jinja2 templates in JS
- **Import**: `posawesome.bundle.js` → clean ES6 imports only
- **Benefit**: No TypeScript errors, modern ES6 imports

### ✅ API Migration Completed
- **All @frappe.whitelist()** moved from DocType files to `/api/` structure
- **DocType files**: Only class methods remain
- **api_mapper.js**: All paths updated to new structure

### ✅ Vuetify Removal
- **All Vuetify components removed**: Replaced with pure HTML/CSS
- **Build size**: Optimized to ~606KB JS, ~114KB CSS

### ✅ Success Logging Cleanup (NEW)
- **Removed**: `frappe.log_error()` calls for successful operations
- **Examples**: "Opening allowed", "Retrieved X users", "Successfully submitted"
- **Kept**: Only actual error logging in exception handlers
- **Benefit**: Cleaner error logs, reduced noise

## Code Review Checklist

Before committing:
- [ ] Backend: Used specific fields in `frappe.get_doc()` - NO SELECT *
- [ ] Backend: Verified column names via `DESCRIBE \`tabDocType\`;`
- [ ] Backend: Used parametrized SQL queries with `%s`
- [ ] Backend: NO `frappe.log_error()` for successful operations
- [ ] Frontend: Implemented 1s debounce for batch operations
- [ ] Frontend: Cleaned up event listeners in `beforeUnmount()`
- [ ] Frontend: Used `API_MAP` constants - NEVER hardcoded paths
- [ ] Frontend: NO `console.log()` - only console.error/warn
- [ ] Frontend: Components < 500 lines (split if larger)
- [ ] Frontend: Pure HTML/CSS - NO Vuetify or frameworks
- [ ] No caching (only temporary operation batches)
- [ ] Response time <100ms (backend)

## Key Files to Understand

1. `api_mapper.js` - ALL API endpoints (ALWAYS use this)
2. `posawesome.bundle.js` - Bundle entry point
3. `hooks.py` - Frappe integration
4. `api/` folder - All @frappe.whitelist() functions (one per file)
5. `components/Navbar.vue` - Top nav with payment totals
6. `components/pos/Invoice.vue` - Main invoice logic (being simplified)
7. `improvements_tasks/` - Detailed policy documentation

## What Makes This Project Unique

- **Barcode Performance**: 30+ scans/second via onscan.js
- **Zero Frontend Calculations**: All math via ERPNext controllers
- **Framework-First**: Uses original ERPNext patterns
- **Batch Queue System**: Only 3 API calls per invoice
- **One Function Per File**: Strictly enforced API structure
- **No Frameworks**: Pure Vue 3 + HTML/CSS, no Vuetify
- **No Debug Logs**: Clean console with only errors
- **Shift-Based Totals**: Real-time cash/non-cash tracking

## Common Pitfalls to Avoid

1. **❌ Hardcoding API paths** → ✅ Use `API_MAP.DOCTYPE.OPERATION`
2. **❌ Using console.log()** → ✅ Use console.error() only
3. **❌ SELECT * queries** → ✅ Specify fields in frappe.get_doc()
4. **❌ Wrong column names** → ✅ Check via DESCRIBE first
5. **❌ Vuetify components** → ✅ Use pure HTML/CSS
6. **❌ {% include %} in .js** → ✅ Import in bundle
7. **❌ frappe.log_error() for success** → ✅ Only for actual errors
8. **❌ Multiple API calls** → ✅ Use batch queue system
9. **❌ Forgetting beforeUnmount()** → ✅ Clean up listeners/timers
10. **❌ Large components (>500 lines)** → ✅ Split into smaller files
