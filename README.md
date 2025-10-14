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

- **💰 Sales & Invoices**
- **🎯 Offers & Coupons**
- **👥 Customer Management**
- **📦 Inventory**
- **🔐 Shift Management**
- **💳 Payment Features**
- **🎨 Modern UI**

### Key Highlights
- Multiple payment modes with split payments
- M-PESA/Phone payment integration
- Auto-apply offers and coupons
- Multi-barcode support (standard/weight/private)
- Loyalty points and customer credit
- Real-time inventory tracking
- Draft and return invoices
- Shift-based reconciliation

📄 **[View Complete Features List →](./FEATURES.md)**

---

## � API Structure

Frontend (Vue 3) ↔ Backend (Python) API mapping  
**37 endpoints** across **9 API files**

**Components:** Customer • Invoice • Items  
Payments • Returns • Shifts

🔗 **[View Complete API Documentation →](./API_STRUCTURE.md)**

---

## 🛠️ Tech Stack

### Backend
- Frappe v15
- ERPNext v15
- Python 3.10+
- MariaDB
- Redis

### Frontend
- Vue 3.4.21
- Vuetify 3.6.9
- mitt
- lodash

### Tools
- **Barcode Scanner:** [onScan.js](https://github.com/axenox/onscan.js) - Hardware barcode scanner detection

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

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl/Cmd + S` | Open payment |
| `Ctrl/Cmd + X` | Submit payment |
| `Ctrl/Cmd + D` | Remove item |
| `ESC` | Clear/Close |

---

## 📚 Documentation

- **[FEATURES.md](./FEATURES.md)** - Complete feature list with details
- **[API_STRUCTURE.md](./API_STRUCTURE.md)** - Frontend ↔ Backend API mapping
- **[Task Sheet](https://docs.google.com/spreadsheets/d/1EX9QDOkw0UD-qPh3Ynpcw37q3b_bFtQ4)** - Project tasks & progress

---

## � License

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
