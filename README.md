<div align="center">
    <img src="https://frappecloud.com/files/pos.png" height="128">
    <h2>POS Awesome Lite</h2>
    <p><em>Modern Point of Sale System for ERPNext</em></p>
</div>

---

## 📋 Overview

**POS Awesome Lite** is an advanced, high-performance Point of Sale application for ERPNext v15, built with modern web technologies. This lite version focuses on core POS functionality with optimized performance and a clean, intuitive user interface.

**Version:** 18.7.2025  
**License:** GPLv3  
**Repository:** [https://github.com/abdopcnet/posawesome15_lite](https://github.com/abdopcnet/posawesome15_lite)

---

## 🚀 Key Features

### 💰 Sales & Transactions
- **Smart Invoice Management** - Create, edit, and submit invoices with automatic calculations
- **Flexible Payment Options** - Support for multiple payment modes, split payments, and rounding adjustments
- **Return Processing** - Handle returns and credit notes with validation against original invoices
- **Draft Management** - Save and resume incomplete transactions
- **Barcode Scanning** - Instant item lookup and cart addition via barcode

### 🎯 Promotions & Marketing
- **POS Offers System** - Flexible promotional offers with multiple discount types:
  - Item-specific, item group, brand, or transaction-wide offers
  - Quantity-based and amount-based triggers
  - Buy-One-Get-One (BOGO) support
  - Automatic or coupon-based activation
- **Coupon Management** - Promotional and gift card coupons with usage tracking
- **Referral System** - Built-in customer referral program with automatic coupon generation
- **Loyalty Integration** - ERPNext loyalty program integration

### 👥 Customer Management
- **Quick Customer Selection** - Fast customer lookup with search
- **Customer Profiles** - Mobile, email, tax ID tracking
- **Address Management** - Add and manage customer addresses
- **Referral Tracking** - Track customer referral codes and rewards

### 📦 Inventory Management
- **Real-time Stock Tracking** - Live inventory updates
- **Batch & Serial Number Support** - Track batch/serial numbers for items
- **Item Variants** - Handle product variants seamlessly
- **Item Group Filtering** - Browse items by category
- **Dual Search** - Search by item name, code, or barcode

### 🔐 Shift Management
- **POS Opening Shift** - Start shifts with cash denomination tracking
- **POS Closing Shift** - End-of-shift reconciliation with payment breakdown
- **Multi-terminal Support** - Each cashier maintains their own shift
- **Audit Trail** - Complete transaction history per shift

### 🎨 User Interface
- **Material Design** - Modern UI with Vuetify 3 components
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Split-Screen Design** - Items selector on left, invoice on right
- **Keyboard Shortcuts** - Fast navigation for power users
- **Real-time Updates** - Live data synchronization across components

### ⚙️ Configuration
- **POS Profile** - Customizable settings per POS terminal
- **Posting Date Override** - Backdate invoices (configurable ±7 days)
- **Zero-Rate Items** - Allow or prevent zero-priced items
- **New Line Mode** - Create new line for each scan or increment existing
- **Custom Fields** - Extended ERPNext DocTypes with POS-specific fields

---

## 🛠️ Technical Stack

### Backend Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| **Frappe Framework** | v15.x | Core framework and ORM |
| **ERPNext** | v15.x | ERP system and business logic |
| **MariaDB** | 10.6+ | Database server |
| **Redis** | Latest | Caching and session storage |
| **Python** | 3.10+ | Backend language |

### Frontend Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| **Vue.js** | 3.4.21 | Progressive JavaScript framework |
| **Vuetify** | 3.6.9 | Material Design component library |
| **mitt** | 3.0.1 | Event emitter (200 bytes) for component communication |
| **lodash** | 4.17.21 | JavaScript utility functions |
| **@mdi/font** | 6.0.95 | Material Design Icons |

### Architecture Patterns
- **Component-Based UI** - Modular Vue components for maintainability
- **Event-Driven Backend** - Frappe document lifecycle hooks
- **RESTful API** - Whitelisted API endpoints for security
- **Permission Bypass** - Controlled POS user permissions
- **Graceful Degradation** - Fallbacks for deleted/invalid data
- **ERPNext Delegation** - Leverage ERPNext calculations (taxes, totals)

---

## 📦 Installation

### Prerequisites
- Frappe Bench with ERPNext v15 installed
- Node.js 18+ and npm
- MariaDB 10.6+
- Redis server

### Installation Steps

```bash
# 1. Navigate to your bench directory
cd /home/frappe/frappe-bench-15

# 2. Get the app from repository
bench get-app posawesome https://github.com/abdopcnet/posawesome15_lite.git

# 3. Install on your site
bench --site [your.site.name] install-app posawesome

# 4. Build assets
bench build --app posawesome

# 5. Restart bench
bench restart

# 6. Clear cache
bench --site [your.site.name] clear-cache
```

### Post-Installation Setup

1. **Create POS Profile**
   - Go to: POS Profile > New
   - Set: Company, Warehouse, Price List, Payment Methods
   - Enable POS Awesome specific settings

2. **Assign User Roles**
   - Add "Sales User" or "POS User" role to cashiers
   - Add "POS Manager" for shift management

3. **Configure Custom Settings** (Optional)
   - Enable/disable posting date override
   - Set zero-rate item policy
   - Configure new line behavior

4. **Test Installation**
   - Navigate to: /app/posapp
   - Create opening shift
   - Test item search and invoice creation

---

## 🎯 Recent Improvements & Optimizations

### Performance Enhancements
- ✅ **Optimized Database Queries** - Efficient JOIN queries for item and price fetching
- ✅ **Minimal Response Payloads** - Only essential data returned from APIs
- ✅ **Lazy Component Loading** - Code splitting for faster initial load (planned)
- ✅ **Caching Strategy** - Redis caching for offers and profiles (planned)

### Code Quality
- ✅ **Comprehensive Documentation** - Detailed code analysis and API documentation
- ✅ **Structured API Layer** - Clear separation of concerns
- ✅ **Error Handling** - Try-except blocks with proper logging
- ✅ **Code Comments** - Critical sections well-documented

### Security
- ✅ **API Whitelisting** - All public endpoints explicitly whitelisted
- ✅ **Parameterized Queries** - SQL injection prevention
- ✅ **Session Authentication** - Frappe session-based security
- ✅ **Permission Checks** - Role-based access control (enhanced in roadmap)

### User Experience
- ✅ **Responsive Design** - Mobile-friendly interface
- ✅ **Loading Indicators** - Visual feedback for operations
- ✅ **Keyboard Shortcuts** - Fast navigation
- ✅ **Automatic Offers** - Auto-apply eligible promotions
- ✅ **Empty Invoice Cleanup** - Auto-delete orphaned invoices

---

## 🎹 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + S` | Open payment panel |
| `Ctrl/Cmd + X` | Submit payment |
| `Ctrl/Cmd + D` | Remove first item from cart |
| `Ctrl/Cmd + A` | Expand first item details |
| `Ctrl/Cmd + E` | Focus on discount field |
| `ESC` | Clear search / Close dialogs |

---

## 📚 Documentation

### Core Documentation
- **📖 README** - [README.md](./README.md) - This file
- **🏗️ Architecture Diagrams** - [app_diagram.md](./app_diagram.md) - Visual system architecture with Mermaid diagrams
- **📂 File Structure** - [app_tree.md](./app_tree.md) - Complete file tree with detailed descriptions
- **📊 Comprehensive Analysis** - [posawesome_comprehensive_analysis.md](./posawesome_comprehensive_analysis.md) - Full technical analysis
- **📋 Improvement Plan** - [IMPROVEMENT_PLAN.md](./IMPROVEMENT_PLAN.md) - 20 numbered improvement tasks

### Architecture & Structure
The application architecture is documented in detail across these files:

- **[app_diagram.md](./app_diagram.md)** - Contains 13 Mermaid diagrams:
  - System Architecture Overview
  - Component Communication Flow
  - Data Flow Architecture
  - Database Schema Relationships
  - Security & Permission Flow
  - Frontend Component Tree
  - Event Bus Architecture
  - And more...

- **[app_tree.md](./app_tree.md)** - Complete file structure:
  - Every file documented with purpose
  - Line counts and size statistics
  - Critical files highlighted
  - Quick lookup guide
  - File relationships

### Planned Documentation
- **Event Bus Documentation:** [docs/EVENT_BUS.md](./docs/EVENT_BUS.md) (planned)
- **API Documentation:** [docs/api/README.md](./docs/api/README.md) (planned)
- **Deployment Guide:** [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md) (planned)

### How to View Diagrams
To view the Mermaid diagrams in `app_diagram.md`:
1. **VS Code**: Install extension `bierner.markdown-mermaid`
2. **GitHub**: Diagrams render automatically
3. **Online**: Copy to [mermaid.live](https://mermaid.live)

---

## 🔧 Configuration Options

### POS Profile Settings
- `posa_allow_change_posting_date` - Enable backdating invoices
- `posa_allow_zero_rated_items` - Allow items with zero price
- `posa_new_line` - Create new line per scan vs increment quantity
- `selling_price_list` - Default price list for this profile
- `warehouse` - Default warehouse for inventory

### Company Settings
- `posa_auto_referral` - Auto-create referral codes for new customers
- `posa_customer_offer` - Default offer for referred customers
- `posa_primary_offer` - Default offer for referring customers
- `posa_referral_campaign` - Campaign for referral tracking

---

## 🐛 Known Issues & Roadmap

### Upcoming Improvements
- [ ] **N+1 Query Optimization** - Single JOIN query for items + prices
- [ ] **Component Splitting** - Break down large Invoice.vue component
- [ ] **Unit Testing** - Comprehensive test coverage
- [ ] **TypeScript Migration** - Type safety for frontend
- [ ] **PWA Support** - Offline functionality
- [ ] **WebSocket Updates** - Real-time inventory sync
- [ ] **Analytics Dashboard** - Sales insights and reports

See [IMPROVEMENT_PLAN.md](./IMPROVEMENT_PLAN.md) for detailed task list.

---

## 🤝 Support & Contribution

### Technical Support
- **Email:** [abdopcnet@gmail.com](mailto:abdopcnet@gmail.com)
- **Repository:** [https://github.com/abdopcnet/posawesome15_lite](https://github.com/abdopcnet/posawesome15_lite)

### Bug Reports & Feature Requests
Please create GitHub issues on our repository:
[https://github.com/abdopcnet/posawesome15_lite/issues](https://github.com/abdopcnet/posawesome15_lite/issues)

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0** - see the [license.txt](./license.txt) file for details.

---

## 👨‍💻 Developer Information

- **Publisher:** abdopcnet
- **Email:** abdopcnet@gmail.com
- **Maintainer:** future-support
- **Repository:** [https://github.com/abdopcnet/posawesome15_lite](https://github.com/abdopcnet/posawesome15_lite)
- **Version:** 18.7.2025

---

## 📖 Quick Documentation Reference

**New to the project?** Start here:

1. **[README.md](./README.md)** ← You are here - Overview and features
2. **[app_diagram.md](./app_diagram.md)** → Visual architecture diagrams
3. **[app_tree.md](./app_tree.md)** → Complete file structure guide
4. **[IMPROVEMENT_PLAN.md](./IMPROVEMENT_PLAN.md)** → Step-by-step improvement tasks

**Need detailed information?**

- 🔍 Understanding the codebase? → [posawesome_comprehensive_analysis.md](./posawesome_comprehensive_analysis.md)
- 🏗️ Understanding architecture? → [app_diagram.md](./app_diagram.md)
- 📂 Finding specific files? → [app_tree.md](./app_tree.md)
- 🛠️ Want to improve the app? → [IMPROVEMENT_PLAN.md](./IMPROVEMENT_PLAN.md)

---

## 🙏 Acknowledgments

Built on top of:
- [Frappe Framework](https://github.com/frappe/frappe) - The best Python framework for web apps
- [ERPNext](https://github.com/frappe/erpnext) - The world's best free and open source ERP
- [Vue.js](https://vuejs.org/) - The Progressive JavaScript Framework
- [Vuetify](https://vuetifyjs.com/) - Material Design Component Framework

---

<div align="center">
    <p>Made with ❤️ for the ERPNext community</p>
    <p>
        <a href="https://github.com/abdopcnet/posawesome15_lite">⭐ Star us on GitHub</a> •
        <a href="https://github.com/abdopcnet/posawesome15_lite/issues">🐛 Report Bug</a> •
        <a href="https://github.com/abdopcnet/posawesome15_lite/issues">💡 Request Feature</a>
    </p>
</div>

### Contributing

Please follow the ERPNext contribution guidelines:

1. [Issue Guidelines](https://github.com/frappe/erpnext/wiki/Issue-Guidelines)
2. [Pull Request Requirements](https://github.com/frappe/erpnext/wiki/Contribution-Guidelines)

---

### License

GNU/General Public License v3 (GPLv3)
