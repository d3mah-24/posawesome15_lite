# AI Agent Instructions for POS Awesome Lite

## Project Philosophy

**POS Awesome Lite = Modern Vue.js Interface + Original ERPNext Engine**

This is NOT a standalone system. It's a lightweight web interface built on top of ERPNext's proven foundation, using original ERPNext patterns (sales_invoice.js) and controllers. Zero custom calculations - all framework-powered.

## Architecture Overview

### Backend: Frappe App Structure
```
posawesome/
├── posawesome/              # Main module (note: nested same name)
│   ├── api/                 # API endpoints by DocType
│   │   ├── sales_invoice/   # CRUD: create, update, submit, delete, get_return
│   │   ├── customer/        # get, get_many, create, update, addresses, coupons
│   │   ├── item/           # get_items, get_items_groups, barcode, batch
│   │   ├── pos_profile/    # get_default_payment
│   │   ├── pos_offer/      # get_applicable_offers, get_offers_for_profile
│   │   └── pos_opening_shift/ # shift management
│   ├── doctype/            # Custom DocTypes
│   └── page/               # Frappe pages
└── public/js/              # Frontend code
    └── posapp/
        ├── components/pos/  # Vue components
        ├── api_mapper.js   # Central API endpoint registry
        └── bus.js          # Event bus (mitt)
```

**Critical Pattern**: API functions follow strict naming: `posawesome.posawesome.api.[doctype].[operation].[operation]_[doctype]`
- Example: `posawesome.posawesome.api.sales_invoice.create.create_invoice`
- All endpoints mapped in `api_mapper.js` - **ALWAYS use API_MAP constants, never hardcode paths**

### Frontend: Vue 3 (Pure HTML/CSS)
- **Stack**: Vue 3.4.21, mitt 3.0.1 (event bus)
- **NO Vuetify** - Migrated to pure HTML/CSS for performance
- **Entry**: `posawesome/page/posapp/posapp.js` loads Vue app
- **Components**: `/posawesome/public/js/posapp/components/pos/`
  - `Pos.vue` - Main container, panel switching
  - `Invoice.vue` - Invoice management (simplified from 3,484 lines)
  - `ItemsSelector.vue` - Item grid/list with barcode scanning (30+ scans/sec)
  - `Payments.vue` - Payment mode handling
  - `Customer.vue` - Customer selection
  - `Returns.vue` - Return invoice handling
  - `PosOffers.vue` - Offer management

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

**File Structure**: One function per file
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

**Performance Rules**:
- Target: <100ms response time
- Use `fields=["field1", "field2"]` parameter - **NO SELECT * allowed**
- Use `ignore_version=True` for faster saves
- Call `frappe.db.commit()` immediately after operations
- Implement `frappe.log_error()` at end of each function

### 3. Event Bus Communication

**Use mitt** (imported as `evntBus` from `bus.js`):
```javascript
// Emit
evntBus.emit('add_item', item);

// Listen (in mounted() or created())
evntBus.on('add_item', this.handleAddItem);

// CRITICAL: Clean up in beforeDestroy() (Vue 2) or beforeUnmount() (Vue 3)
beforeDestroy() {
  evntBus.off('add_item', this.handleAddItem);
  // Clear ALL timers
  if (this._debounceTimer) clearTimeout(this._debounceTimer);
}
```

**Common Events**: add_item, update_customer, new_invoice, show_payment, item_updated, register_pos_profile, show_mesage (note: typo is intentional in codebase)

### 4. Console Logging Policy

**REMOVED**: All debug `console.log()` statements have been cleaned up
**KEEP**: Only `console.error()` for actual errors and `console.warn()` for warnings
- Example: Debug logs like "Barcode scan", "API Response", "check data" are all removed
- Focus on clean console output showing only actionable errors

### 5. UI Component Standards

**NO Vuetify** - All components use pure HTML/CSS:
```vue
<!-- Use native HTML tables instead of v-data-table -->
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

<!-- Use native HTML5 inputs instead of Vuetify components -->
<input type="date" v-model="creditDate" class="custom-date-input" />
```

**Performance Rules**:
- Virtual scrolling for lists > 50 items
- Simple component structure only
- No animations or heavy CSS
- No global library imports
- Lightweight, responsive designs

### 6. Framework Integration Points

**Frappe Hooks** (`hooks.py`):
```python
# Vue.js bundled in posawesome.bundle.js
app_include_js = [
    "posawesome.bundle.js",
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

### 7. Common Workflows

**Apply Backend Changes**:
```bash
find . -name "*.pyc" -print -delete
find . -type d -name "__pycache__" -print -exec rm -rf {} +
bench restart
```

**Apply Frontend Changes**:
```bash
cd ~/frappe-bench-15
bench clear-cache && bench clear-website-cache && bench build --app posawesome --force
```

**Debug**:
- Backend: `frappe.log_error(f"[filename.py][function_name] Result: {result}")`
- Frontend: Use `console.error()` only for actual errors (no debug console.log)

## Active Simplification Initiative

**Target**: Reduce Invoice.vue from 3,484 → 400 lines (89% reduction)

See `improving_frontend_docs/` for detailed analysis:
- `COMPARISON.md` - ERPNext vs POSAwesome patterns (1,169 vs 3,484 lines)
- `PLAN.md` - 5-phase migration roadmap with code examples
- `README.md` - Quick overview and metrics

**Key Insight**: ERPNext's sales_invoice.js does same functionality in 1,169 lines because framework handles:
- Automatic calculations (totals, taxes, discounts)
- State management (reactive updates)
- CRUD operations (save, submit, validate)
- Print formats

**When modifying Invoice.vue**: Prefer framework patterns over manual implementations. Check PLAN.md for approved simplification patterns.

**Recent Improvements**:
- ✅ Removed all Vuetify dependencies - migrated to pure HTML/CSS
- ✅ Cleaned up all debug console.log statements
- ✅ Removed all sound notifications (`frappe.utils.play_sound()`)
- 🎯 Target: Continue Invoice.vue simplification using ERPNext patterns

## Code Review Checklist

Before committing:
- [ ] Backend: Used specific fields in `frappe.get_doc()` (no SELECT *)
- [ ] Backend: Added `frappe.log_error()` at function end
- [ ] Frontend: Implemented 1s debounce for batch operations
- [ ] Frontend: Cleaned up event listeners in `beforeDestroy()`
- [ ] Frontend: Used `API_MAP` constants (never hardcoded paths)
- [ ] Frontend: Components under 500 lines (split if larger)
- [ ] No caching (only temporary operation batches allowed)
- [ ] Response time <100ms (backend)
- [ ] No heavy CSS, animations, or complex JavaScript

## External Dependencies

**Payment**: $35 USD/day based on progress via Fiverr/Upwork/Western Union  
**Development**: SSH access to single server (main branch only)  
**Server**: 2x AMD EPYC 9555 (128 threads), 324GB RAM  

**STRICT**: Work outside this process = not reviewed, not accepted, not paid

## Key Files to Understand

1. `api_mapper.js` - ALL API endpoints (never hardcode)
2. `improving_frontend_docs/PLAN.md` - Framework migration strategy
3. `improvements_tasks/frontend/frontend_improvment_policy.md` - Batch queue rules
4. `improvements_tasks/backend/backend_improvment_policy.md` - API standards
5. `hooks.py` - Frappe integration points
6. `Invoice.vue` - Main target for simplification (3,484 lines)

## What Makes This Project Unique

- **Barcode Performance**: Handles 30+ scans/second
- **Zero Frontend Calculations**: All math done server-side using ERPNext controllers
- **Framework-First**: Uses original ERPNext methods (sales_invoice.js patterns)
- **Batch Queue System**: Only 3 API calls per invoice (CREATE → UPDATE → SUBMIT)
- **DocType-Based APIs**: One function per file, organized by DocType
- **No Reinventing**: Leverages ERPNext's battle-tested foundation
