<div align="center">
    <img src="./imgs/pos_lite.png" height="128">
    <h2>POS Awesome Lite</h2>
    <p><em>Point of Sale for ERPNext v15</em></p>

![Version](https://img.shields.io/badge/version-23.10.2025-blue)
![License](https://img.shields.io/badge/license-GPLv3-green)
![ERPNext](https://img.shields.io/badge/ERPNext-v15-orange)
![Frappe](https://img.shields.io/badge/Frappe-v15-red)
</div>

---

## 🎯 Goal

**POS Awesome Lite** = Modern Interface + Original ERPNext Engine

Just a lightweight web interface built on top of ERPNext's proven foundation:
- 🎨 **Interface:** Fast, responsive Vue.js UI (+ 30 BarcodeScan/s)
- 🔧 **Frontend:** Uses original ERPNext methods (sales_invoice.js patterns)
- ⚙️ **Backend:** Uses original ERPNext def's & imports (ERPNext controllers)
- 📦 **No Reinventing:** Zero custom calculations, all framework-powered

---

## 🖥️ Try It Live

**Remote Access to the POS UI system**
- 🌐 **Application:** (https://anydesk.com/en)
- 🔑 **ID:** `1134153623`
---

## 📚 Documentation

### 📁 Core Documentation

#### ✨ Features - Complete Feature List

**💰 Sales & Invoices**
- Create, update, and submit sales invoices
- Multiple payment modes (Cash, Card, Bank Transfer, Phone/M-PESA)
- Split payments across multiple payment methods
- Payment request creation (M-PESA/Phone payments)
- Invoice returns with item selection
- Draft invoices (save and resume later)
- Item-level discount (percentage/amount)
- Write-off change amount
- Credit sales with customer credit tracking
- Change amount calculation (cashback)

**💸 Easy Item Discount Control**
- Control show/hide discount price and discount percentage columns in POS interface
- Insert discounted price (limited to allowed max percentage)
- Insert discount percentage (limited to allowed max percentage)  
- Sales invoice shows total items discount amount (simplified for invoice print format)

**💰 Easy Invoice Discount Control**
- Control show/hide Invoice discount percentage
- Insert discount percentage (limited to allowed max percentage)
- Sales invoice shows total Invoice discount amount & Percentage (simplified for invoice print format)

**🎯 Offers & Coupons**
- **POS Offers** - Apply on: Item, Item Group, Brand, Transaction
- **Offer Types:** Product/Give Product, Discount (%), Discount (Amount)
- Min/Max quantity and amount triggers
- Date-based offer validity (from/to)
- Auto-apply offers or manual selection
- Coupon-based offers
- Gift coupons from referral codes
- Replace item or replace cheapest item options

**👥 Customer Management**
- Customer search and quick selection
- Create new customers with full details
- Customer addresses (shipping/billing)
- Manage multiple addresses
- Customer referral codes and campaigns
- Customer credit balance tracking
- Loyalty program integration
- Loyalty points redemption
- Tax ID support
- Mobile number tracking

**📦 Inventory**
- Real-time stock availability display
- Batch number selection and tracking
- Serial number support
- Multi-barcode support:
  - Standard EAN/UPC barcodes
  - Weight scale barcodes (prefix-based)
  - Private/custom barcodes
- Item search (name/code/barcode)
- Item group filtering
- Price list integration
- Item images display

**🔐 Shift Management**
- **POS Opening Shift** - Opening balance entry
- **POS Closing Shift** - End-of-day reconciliation
- Cash denomination counting
- Payment mode-wise summary
- Shift-wise invoice tracking
- Invoice count per shift
- Shift reports and statistics

**💳 Payment Features**
- Payment mode configuration
- Phone payment request (M-PESA/Mobile Money)
- Loyalty points payment
- Customer credit redemption
- Change amount handling
- Write-off excess/shortage
- Payment reference tracking

**📱 Barcode Scanner Compatibility**
- **Auto-Focus Free Scanning:** Scan barcodes anywhere in POS interface without focusing search field
- **Instant Item Addition:** Scanned items automatically added to invoice cart
- **Multiple Barcode Support:** EAN-13, Code 128, UPC-A, and custom barcodes
- **Hardware Scanner Compatible:** Works with USB and Bluetooth barcode scanners
- **Speed Optimized:** Handles 30+ scans per second for high-volume operations
- **Error Handling:** Clear feedback for invalid or unrecognized barcodes
- **OnScan.js Integration:** Advanced barcode detection with configurable timing
- **No Manual Input Required:** Seamless scanning workflow without keyboard interaction

**🎨 User Interface**
- **Frontend:** Vue 3.4.21 + Vuetify 3.6.9
- Responsive and modern design
- Split view (items selector + invoice)
- Compact table layouts
- Real-time calculations
- Keyboard shortcuts (Ctrl+S, Ctrl+X, Ctrl+D, ESC)
- Touch-friendly controls
- Dark/Light theme support

**📋 Configuration Options**
- **POS Profile Settings:** Allow user to edit item discount, Maximum item discount allowed, Allow write-off change, Allow credit sales, Use customer credit, Use cashback on returns
- **Payment Settings:** Multiple payment modes configuration, Default payment method, Payment request integration, Phone payment support
- **Offer Settings:** Auto-apply offers, Coupon-based offers, Date-based validity, Multi-level offer application

#### 🛠️ Tech Stack - Technology Stack Details

**Backend Infrastructure**
- **Frappe v15** - Python web framework with built-in ORM and API system
- **ERPNext v15** - Enterprise Resource Planning with integrated accounting and inventory
- **Python 3.10+** - Modern Python features with type hints support
- **MariaDB** - MySQL-compatible database with high performance and ACID compliance
- **Redis** - In-memory data store for session management and performance optimization

**Frontend Technology**
- **Vue 3.4.21** - Progressive JavaScript framework with Composition API
- **Vuetify 3.6.9** - Material Design components with responsive design
- **mitt** - Lightweight event emitter for component communication
- **lodash** - JavaScript utility library for data manipulation

**External Libraries & Dependencies**
- **Bootstrap 4.6.2** - CSS framework with responsive grid system
- **jQuery 3.7.0** - JavaScript library for DOM manipulation
- **Leaflet 1.2.0** - Interactive maps with mobile-friendly support
- **Moment.js 2.29.4** - Date manipulation with internationalization support
- **Moment Timezone 0.5.43** - Timezone handling with DST support
- **core-js** - JavaScript polyfills for ES6+ feature support

**Hardware Integration**
- **onScan.js** - Hardware barcode scanner detection with cross-platform compatibility
- **Supported Scanner Types:** USB HID, Bluetooth, Camera-based, Keyboard wedge scanners

**Development Tools**
- **Git/GitHub** - Version control with main branch strategy
- **npm/yarn** - Frontend dependencies management
- **Frappe Build System** - Built-in build tools with Webpack and Babel
- **Frappe Development Server** - Hot reload support with live reload

**Performance Optimizations**
- **Frontend:** Code splitting, tree shaking, minification, browser caching
- **Backend:** Database indexing, Redis caching, connection pooling, async processing

**Security Features**
- **Authentication:** Frappe authentication with role-based access control
- **Data Protection:** SQL injection prevention, XSS protection, CSRF protection, data encryption

#### ⌨️ Keyboard Shortcuts - Complete Guide

**Global Shortcuts**

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl/Cmd + S` | Open Payment | Opens the payment dialog for current invoice |
| `Ctrl/Cmd + X` | Submit Payment | Submits the payment and finalizes the invoice |
| `Ctrl/Cmd + D` | Delete First Item | Removes the first item from the invoice |
| `Ctrl/Cmd + A` | Expand First Item | Expands the first item for editing |
| `Ctrl/Cmd + Z` | Focus Discount | Focuses on the discount input field |
| `ESC` | Clear Search | Clears the item search field and resets search |
| `Enter` | Confirm Input | Confirms changes in rate and discount percentage fields |

**Shortcut Details**
- **Payment Shortcuts:** Ctrl/Cmd + S opens payment dialog, Ctrl/Cmd + X submits payment
- **Item Management:** Ctrl/Cmd + D removes first item, Ctrl/Cmd + A expands first item, Ctrl/Cmd + Z focuses discount field
- **Search Shortcuts:** ESC clears search field, Enter confirms input in form fields

**Barcode Scanner Integration**
- **Automatic Detection:** Hardware barcode scanners are automatically detected
- **Real-time Processing:** Barcodes are processed immediately upon scanning
- **Multiple Formats:** Supports standard EAN/UPC, weight scale, and private barcodes
- **Direct Addition:** Scanned items are added directly to the invoice without confirmation

**Usage Tips**
- **Efficient Workflow:** Use Ctrl/Cmd + S for quick payment, Ctrl/Cmd + D for fast item removal
- **Form Navigation:** Use Enter to confirm changes, Tab to move between fields
- **Cross-Platform Support:** Ctrl works on Windows/Linux, Cmd works on macOS

#### ⚙️ Development Commands - Common Commands

**🔍 Debug Policy**

**Backend (Python) Debug Policy**
- **Summary:** Use `frappe.log_error()` at the end of each function to summarize results
- **Details:** Include the filename, function name, and results in the log
- **Tracking:** [Error Log](http://localhost/app/error-log)

**Frontend Debug Policy**
- **Summary:** Use `console.log` to debug
- **Details:** Include the filename, section, and important parameters only

**🔄 Apply Changes Commands**

**Backend Apply Changes**
```bash
find . -name "*.pyc" -print -delete
find . -type d -name "__pycache__" -print -exec rm -rf {} + &&
bench restart
```

**Frontend Apply Changes**
```bash
cd ~/frappe-bench-15
bench clear-cache && \
bench clear-website-cache && \
bench build --app posawesome --force
```

### 🎨 Frontend Development

#### Frontend Analysis
**Critical Issues Identified:**
- **Invoice.vue** (2,357 lines) - Massive component size, performance bottleneck
- **ItemsSelector.vue** (1,801 lines) - Heavy filtering, memory leaks  
- **Payments.vue** (1,670 lines) - Complex calculations, tight coupling

**Performance Problems:**
- Large JavaScript bundle, no code splitting
- Excessive re-renders, memory leaks
- No caching, repeated API calls
- Heavy computed properties

#### Frontend Policy
**Memory Management Rules:**
- ✅ Event listeners cleanup in `beforeDestroy`/`onBeforeUnmount`
- ✅ Timer and interval cleanup
- ✅ Event bus cleanup
- ✅ DOM references release

**UI/UX Rules:**
- Vue.js + HTML + CSS only (NO Vuetify)
- NO caching (only temp operations batches)
- NO animations or heavy CSS
- Virtual scrolling for lists > 50 items
- Simple component structure only

**Asset Management:**
- ✅ Local CDN only - no external requests
- ✅ Local fonts and Material Design Icons
- ✅ Minimize dependencies, named imports only

**API Call Rules (MANDATORY):**
- Use `api_mapper.js` for all API calls
- Maximum 2 API calls on page load
- Batch operations: CREATE → UPDATE → SUBMIT
- 1 second idle time, max 50 operations per batch
- Clear temp cache after successful API call

### 🔧 Backend Development  

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

**Priority Tasks:**
1. Implement specific field queries (Phase 1)
2. Standardize API structure (Phase 1)  
3. Add error handling (Phase 2)
4. Optimize database performance (Phase 2)
5. Develop printing service (Phase 3)

### 🚀 Development Policies
**Mandatory compliance for all code contributions:**
- **Frontend:** 3-API batch queue system (CREATE → UPDATE → SUBMIT)
- **Backend:** Frappe ORM only with specific field selection
- **Performance:** < 100ms response time, lightweight components
- **Structure:** DocType-based API organization, no caching except temp batches
- **Assets:** Local-only dependencies, no external CDN requests

---

## 🚀 Feature Requests

### �️ Auto Delete Draft Invoices
Auto delete draft invoices after closing shift for same invoices created during the shift.

### 🔍 Analysis Offer Types
Analysis of offer types functionality (pending implementation).

### 📁 Vue File Splitting
- **[Vue File Splitting](./feature_requests/Vue_file_splitting/Vue_file_splitting.md)** - Vue.js file splitting implementation

---

## 🔧 Development Tools

---

## 💰 Collaboration

- ⚠️ **Terms**: Tasks negotiated before beginning
- 💵 **Payment:** to completed tasks only
- 🌐 **Payment Methods:**
- 💼 **International**: 
  -🟢 [Fiverr](https://fiverr.com) 
  -🔵 [Upwork](https://upwork.com) 
  -💰 Western Union 
  -₿ Crypto
- <img src="./imgs/Egypt.svg" width="16" height="16"> **Egypt**: Phone cash wallets
- <img src="./imgs/Saudi_Arabia.svg" width="16" height="16"> **Saudi Arabia**: STC Pay, Alrajhi Bank Transfer

**Development Server:**
- 🔗 Direct work via **SSH on single server**
- 📦 Repository: [github.com/abdopcnet/posawesome15_lite](https://github.com/abdopcnet/posawesome15_lite)
- 🌿 Branch: **main only**


**🐢 Server Specifications:**
- 💾 **RAM:** 324 GB DDR5
- 🔧 **CPU:** 2x AMD EPYC 9555
- ⚡ **Cores/Threads:** 2024 cores / 128 threads
- 🔋 **Power:** 360 Watt

⚠️ **Project POLICY:**  
- ⚠️ Changes into front conflicts improve policy
- ⚠️ Changes into backend conflicts improve policy  
- ⚠️ Changes not asked for
- ⚠️ Changing codebase structure
- ⚠️ Changes not direct in ssh dev_server
- ⚠️ Commits before review and test
- ❌ will deleted
- ❌ No payment

---

## 👨‍💻 Contact

<div align="center">
    <img src="./imgs/ERPNext-support.png" height="200" alt="Future Support" style="border-radius: 20px;">
</div>

**Developer:** abdopcnet  
**Company:** [Future Support](https://www.future-support.online/)  
**Email:** abdopcnet@gmail.com  
**GitHub:** [github.com/abdopcnet/posawesome15_lite](https://github.com/abdopcnet/posawesome15_lite)

**Need Support or Want to Join? Contact Now:**

### 🇬 Egypt Contact
- 📞 **Call:** <img src="./imgs/Egypt.svg" width="16" height="16"> [+20 115 648 3669](tel:+201156483669)
- <img src="./imgs/whatsapp.svg" width="16" height="16"> **WhatsApp:** <img src="./imgs/Egypt.svg" width="16" height="16"> [https://wa.me/201156483669](https://wa.me/201156483669)
- <img src="./imgs/telegram.svg" width="16" height="16"> **Telegram:** [https://t.me/abdo_01156483669](https://t.me/abdo_01156483669)

### 🇸🇦 Saudi Arabia Contact  
- 📞 **Call:** <img src="./imgs/Saudi_Arabia.svg" width="16" height="16"> [+966 57 891 9729](tel:+966578919729)
- <img src="./imgs/whatsapp.svg" width="16" height="16"> **WhatsApp:** <img src="./imgs/Saudi_Arabia.svg" width="16" height="16"> [https://wa.me/966578919729](https://wa.me/966578919729)
- <img src="./imgs/telegram.svg" width="16" height="16"> **Telegram:** [https://t.me/abdo_0578919729](https://t.me/abdo_0578919729)

### 🌐 Online
- 🌐 **Website:** [future-support.online](https://www.future-support.online/)

---

<div align="center">
    <p>Made with ❤️ for ERPNext community</p>
    <p>
        <a href="https://github.com/abdopcnet/posawesome15_lite">⭐ Star</a> •
        <a href="https://github.com/abdopcnet/posawesome15_lite/issues">🐛 Report Bug</a>
    </p>
</div>