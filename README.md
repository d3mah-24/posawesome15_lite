<div align="center">
    <img src="https://frappecloud.com/files/pos.png" height="128">
    <h2>POS Awesome Lite</h2>
    <p><em>Point of Sale for ERPNext v15</em></p>
</div>

---

## 📋 Overview

Point of Sale application for ERPNext v15 built with Vue 3 and Vuetify 3.

**Version:** 18.7.2025 | **License:** GPLv3  
**Repository:** [github.com/abdopcnet/posawesome15_lite](https://github.com/abdopcnet/posawesome15_lite)

---

## ✨ Features

### 💰 Sales & Invoices
- Create and submit sales invoices
- Multiple payment modes
- Split payments
- Invoice returns
- Draft invoices
- Barcode scanning (normal/weight/private)

### 🎯 Offers & Coupons
- POS Offers (item/group/brand/transaction)
- Quantity and amount triggers
- Discount types (percentage/amount)
- POS Coupons
- Auto-apply offers

### 👥 Customer Management
- Customer search and selection
- Create new customers
- Manage addresses
- Referral codes

### 📦 Inventory
- Real-time stock display
- Batch number support
- Serial number support
- Item search (name/code/barcode)
- Item group filtering

### 🔐 Shift Management
- POS Opening Shift
- POS Closing Shift
- Cash reconciliation
- Shift reports

### 🎨 User Interface
- Vue 3 + Vuetify 3
- Responsive layout
- Split view (items + invoice)
- Keyboard shortcuts

---

## 🛠️ Tech Stack

**Backend:** Frappe v15, ERPNext v15, Python 3.10+, MariaDB, Redis  
**Frontend:** Vue 3.4.21, Vuetify 3.6.9, mitt, lodash  
**Barcode Scanner:** [onScan.js](https://github.com/axenox/onscan.js) - Hardware barcode scanner detection library

---

## 📦 Installation

```bash
# Get app
bench get-app posawesome https://github.com/abdopcnet/posawesome15_lite.git

# Install
bench --site [site-name] install-app posawesome

# Build & restart
bench build --app posawesome && bench restart
```

**Setup:** Create POS Profile → Assign roles (POS User/Manager) → Open `/app/posapp`

---

## � Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl/Cmd + S` | Open payment |
| `Ctrl/Cmd + X` | Submit payment |
| `Ctrl/Cmd + D` | Remove item |
| `ESC` | Clear/Close |

---

## 📚 Documentation

- **[api_structure.md](./api_structure.md)** - API endpoints mapping (Vue ↔ Python)
- **[plan.md](./plan.md)** - Development roadmap
- **[Task Sheet](https://docs.google.com/spreadsheets/d/1EX9QDOkw0UD-qPh3Ynpcw37q3b_bFtQ4)** - Project tasks & progress tracking (with screenshots)

---

## 📄 License

**GNU General Public License v3.0** - See [license.txt](./license.txt)

---

## 👨‍💻 Contact

**Developer:** abdopcnet  
**Email:** abdopcnet@gmail.com  
**GitHub:** [github.com/abdopcnet/posawesome15_lite](https://github.com/abdopcnet/posawesome15_lite)

---

<div align="center">
    <p>Made with ❤️ for ERPNext community</p>
    <p>
        <a href="https://github.com/abdopcnet/posawesome15_lite">⭐ Star</a> •
        <a href="https://github.com/abdopcnet/posawesome15_lite/issues">🐛 Report Bug</a> •
        <a href="https://github.com/abdopcnet/posawesome15_lite/issues">💡 Request Feature</a>
    </p>
</div>
