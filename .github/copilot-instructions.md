# AI Agent Instructions for POS Awesome Lite

## Core Principles

**POS Awesome Lite = Vue.js UI + ERPNext Engine**
- Lightweight web interface on top of ERPNext v15 foundation
- Uses original ERPNext patterns and controllers (zero custom calculations)
- Framework-first approach: all business logic via ERPNext

## Architecture at a Glance

### Backend Structure
```
posawesome/posawesome/api/          # ONE function per file (STRICT)
├── sales_invoice/                  # create, update, submit, delete
├── customer/                       # get, get_many, create, update
├── item/                           # get_items, get_barcode_item (unified)
├── pos_profile/                    # get_default_payment, opening_dialog
├── pos_opening_shift/              # shift management
└── pos_closing_shift/              # shift closing + payment totals
```

**API Naming**: `posawesome.posawesome.api.[doctype].[operation].[operation]_[doctype]`

### Frontend Structure  
```
posawesome/public/js/posapp/
├── api_mapper.js                   # Central API registry (ALWAYS USE)
├── bus.js                          # Event bus (mitt 3.0.1)
└── components/
    ├── Navbar.vue                  # Top nav + payment totals
    └── pos/
        ├── Invoice.vue             # Main invoice (2,357 lines)
        ├── ItemsSelector.vue       # Items + barcode (30+ scans/sec)
        └── Payments.vue            # Payment processing
```

**Tech Stack**: Vue 3.4.21 + Vuetify 3.6.9, mitt event bus, onScan.js for barcode

## Critical Patterns

### 1. 3-API Batch Queue (MANDATORY)
Only 3 API calls per invoice lifecycle:
```javascript
// 1. CREATE (first item)
frappe.call({ method: API_MAP.SALES_INVOICE.CREATE, args: { data: doc } });

// 2. UPDATE (batch after 1s idle - collect qty, discounts, payments)
frappe.call({ method: API_MAP.SALES_INVOICE.UPDATE, args: { data: doc } });

// 3. SUBMIT (finalize + print)
frappe.call({ method: API_MAP.SALES_INVOICE.SUBMIT, args: { invoice, data } });
```
- Debounce 1000ms, max 50 operations/batch
- Clear temp cache after response
- NO caching except temp batches

### 2. Backend Standards
```python
# posawesome/posawesome/api/customer/get_customer.py
@frappe.whitelist()
def get_customer(customer_id):
    return frappe.get_doc("Customer", customer_id, 
                          fields=["name", "customer_name", "mobile_no"])  # MUST specify fields
```

**Requirements**:
- One function per file (STRICT)
- Specific field selection (NO `SELECT *`)
- Parametrized SQL with `%s` placeholders
- Check column names: `DESCRIBE \`tabDocType\`;`
- `ignore_version=True` + immediate `frappe.db.commit()`
- Target <100ms response time
- `frappe.log_error()` ONLY for actual errors (not success)

### 3. Event Bus (mitt)
```javascript
// Emit
evntBus.emit('add_item', item);

// Listen  
evntBus.on('add_item', this.handleAddItem);

// CRITICAL: Clean up in beforeUnmount()
beforeUnmount() {
  evntBus.off('add_item', this.handleAddItem);
  if (this._debounceTimer) clearTimeout(this._debounceTimer);
  if (this.cashUpdateInterval) clearInterval(this.cashUpdateInterval);
}
```

**Common Events**: `add_item`, `update_customer`, `new_invoice`, `show_payment`, `show_mesage` (typo intentional)

### 4. Barcode Scanning
- **Unified Handler**: `API_MAP.ITEM.GET_BARCODE_ITEM` (backend auto-detects type)
- **Types**: Standard EAN/UPC, weight scale (prefix), private/custom
- **Performance**: 30+ scans/second via onScan.js
- **Location**: `public/js/onscan.js` (imported in bundle)

### 5. UI Components
**Pure HTML/CSS** (NO Vuetify in new code):
```vue
<!-- ✅ Native HTML -->
<table class="data-table">
  <tr v-for="item in items" :key="item.name">
    <td>{{ item.name }}</td>
  </tr>
</table>

<!-- ❌ NO Vuetify -->
<v-data-table>  <!-- NO -->
```

**Rules**: Components <500 lines, virtual scroll >50 items, no animations, local assets only

### 6. Logging Policy
```javascript
// ❌ NEVER
console.log("Fetching data...");

// ✅ ONLY errors/warnings
console.error('Error fetching cash total:', err);
console.warn('Deprecated API usage');
```

## Developer Workflows

**Backend Changes**:
```bash
find . -name "*.pyc" -delete && find . -type d -name "__pycache__" -exec rm -rf {} + && bench restart
```

**Frontend Changes**:
```bash
cd ~/frappe-bench-15 && bench clear-cache && bench build --app posawesome
```

**Debug DB Schema**:
```bash
bench mariadb
DESCRIBE `tabSales Invoice Payment`;  # Check actual column names
```

**Full Rebuild** (after major changes):
```bash
bench clear-cache && bench clear-website-cache && bench build --app posawesome --force && bench restart
```

## Key Integration Points

### Frappe Hooks (`hooks.py`)
```python
app_include_js = ["posawesome.bundle.js"]  # Vue app + libs

doctype_js = {
    "POS Profile": "public/js/pos_profile.js",
    "Sales Invoice": "public/js/invoice.js",
}

doc_events = {
    "Sales Invoice": {
        "before_submit": "posawesome.posawesome.api.sales_invoice.before_submit.before_submit",
        "before_cancel": "posawesome.posawesome.api.sales_invoice.before_cancel.before_cancel",
    }
}
```

### API Mapper (ALWAYS USE)
```javascript
// posawesome/public/js/posapp/api_mapper.js
const API_MAP = {
  SALES_INVOICE: {
    CREATE: "posawesome.posawesome.api.sales_invoice.create.create_invoice",
    UPDATE: "posawesome.posawesome.api.sales_invoice.update.update_invoice",
    SUBMIT: "posawesome.posawesome.api.sales_invoice.submit.submit_invoice",
  },
  ITEM: {
    GET_BARCODE_ITEM: "posawesome.posawesome.api.item.get_barcode_item.get_barcode_item",
  }
};
```

**Usage**: `frappe.call({ method: API_MAP.SALES_INVOICE.CREATE, ... })`

## What Makes This Unique

- **Barcode Performance**: 30+ scans/second (onScan.js)
- **Zero Frontend Calc**: All math via ERPNext controllers
- **Batch Queue System**: Only 3 API calls per invoice
- **One Function Per File**: Strictly enforced API structure
- **Shift-Based Tracking**: Real-time cash/non-cash totals in navbar
- **Local Assets**: No external CDN requests

## Common Pitfalls

1. ❌ Hardcoded API paths → ✅ Use `API_MAP` constants
2. ❌ `console.log()` → ✅ Only `console.error/warn`
3. ❌ `SELECT *` queries → ✅ Specify fields in `frappe.get_doc()`
4. ❌ Wrong column names → ✅ Verify with `DESCRIBE`
5. ❌ Vuetify in new code → ✅ Pure HTML/CSS
6. ❌ `frappe.log_error()` for success → ✅ Only for errors
7. ❌ Multiple API calls → ✅ Use batch queue
8. ❌ Forgetting `beforeUnmount()` → ✅ Clean up listeners/timers
9. ❌ Large components (>500 lines) → ✅ Split into smaller files
10. ❌ External CDN → ✅ Local assets only

## Recent Changes (October 2025)

- ✅ Payment totals in navbar (cash 💰 + non-cash 💳)
- ✅ Console.log cleanup (30+ removed)
- ✅ Success logging cleanup (`frappe.log_error()` only for errors)
- ✅ Bundle organization (onscan.js → public/js/)
- ✅ Vuetify removal (pure HTML/CSS replacement)
- ✅ API migration (all @frappe.whitelist() → /api/)

## Key Files

1. `api_mapper.js` - API endpoint registry
2. `posawesome.bundle.js` - Bundle entry
3. `hooks.py` - Frappe integration
4. `api/` - All whitelisted functions
5. `components/Navbar.vue` - Nav + payment totals
6. `components/pos/Invoice.vue` - Main invoice logic
7. `README.md` - Complete documentation

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
