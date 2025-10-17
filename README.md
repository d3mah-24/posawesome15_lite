<div align="center">
    <img src="./imgs/pos_lite.png" height="128">
    <h2>POS Awesome Lite</h2>
    <p><em>Point of Sale for ERPNext v15</em></p>

![Version](https://img.shields.io/badge/version-17.10.2025-blue)
![License](https://img.shields.io/badge/license-GPLv3-green)
![ERPNext](https://img.shields.io/badge/ERPNext-v15-orange)
![Frappe](https://img.shields.io/badge/Frappe-v15-red)
</div>

---

## 🎯 Goal

**Lite Web POS**
- Fast, responsive interface (+ 30 BarcodeScan/s)
- Server Side Batch Operations (Maximum durability & security)
- Based On official Sales Invoice Doctype (No Calculations in Frontend)

---

## 🖥️ Try It Live

**Remote Desktop Access** - Test the POS system remotely
- 💻 **Server:** `remote_hoptodesk_pos_pc`
- 🌐 **Application:** [HopToDesk](https://hoptodesk.com)
- 🔑 **ID:** `378901992`

---

## 📚 Documentation

### 📁 Core Documentation
- 📄 **[Features](./docs/FEATURES.md)** - Complete feature list
- 🔧 **[Tech Stack](./docs/TECH_STACK.md)** - Technology stack details
- ⌨️ **[Shortcuts](./docs/SHORTCUTS.md)** - Keyboard shortcuts guide
- ⚙️ **[Dev Commands](./docs/common_dev_cmd.md)** - Common development commands

### 🎨 Frontend Development
- 🔍 **[Frontend Analysis](./improvements_tasks/frontend/frontend_analysis.md)** - Comprehensive Vue.js analysis
- 📋 **[Frontend Policy](./improvements_tasks/frontend/frontend_improvment_policy.md)** - Development policy & batch queue system

### 🔧 Backend Development  
- 📋 **[Backend Policy](./improvements_tasks/backend/backend_improvment_policy.md)** - API structure & performance policy
- 🔌 **[API Structure](./improvements_tasks/backend/API_STRUCTURE.md)** - API documentation

### 🚀 Development Policies
**Mandatory compliance for all code contributions:**
- **Frontend:** 3-API batch queue system (CREATE → UPDATE → SUBMIT)
- **Backend:** Frappe ORM only with specific field selection
- **Performance:** < 100ms response time, lightweight components
- **Structure:** DocType-based API organization, no caching except temp batches

---

## 🚀 Feature Requests

### 📁 Feature Requests Directory
- 🔍 **[Customer Search by Mobile](./feature_requests/customer_searchby_mobile_no/auto_complete_mobile_search.md)** - Auto-complete mobile search functionality
- ⏰ **[Shift Time Controller](./feature_requests/shift_time_controller/pos_opening_closing_shift_timer.md)** - POS opening/closing shift timer control
- 🎨 **[Customize Main Menu](./feature_requests/main_manu/customize_menu.md)** - CSS styling for main menu appearance

---

## 🔧 Development Tools

### 🤖 Auto Commit Tool
**MANDATORY for all development work**

```bash
python3 auto_commiter.py
```

**📋 Auto Commit Policy:**
- ✅ **One File Per Commit:** Each file gets its own commit for precise tracking
- ✅ **Smart Messages:** Intelligent commit messages based on file type and path
- ✅ **Auto Push:** Automatically pushes all commits to remote repository
- ✅ **Zero Manual Work:** No need to manually stage, commit, or push files

**🎯 Usage:**
1. Make your changes to any files
2. Run `python3 auto_commiter.py`
3. Script automatically:
   - Detects all changed files
   - Commits each file separately with smart messages
   - Pushes all commits to `main` branch

**⚠️ STRICT POLICY:**
- **MUST USE** `auto_commiter.py` for all commits
- **NO MANUAL** `git add`, `git commit`, or `git push` commands
- **ENSURES** clean commit history with one file per commit
- **ENABLES** easy tracking and rollback of individual file changes

**📊 Benefits:**
- 🔍 **Easy Debugging:** Find exactly which file caused issues
- 🔄 **Selective Rollback:** Revert individual files without affecting others
- 📈 **Better Tracking:** Clear history of what changed when
- 🤝 **Team Coordination:** Understand exactly what each commit does

---

## 💰 Collaboration

- 💵 **Daily Payment:** $35 USD Based On Progress
- 🌐 **Payment Methods:**
  - Fiverr
  - Upwork
  - Western Union

**Development Server:**
- 🔗 Direct work via **SSH on single server**
- 📦 Repository: [github.com/abdopcnet/posawesome15_lite](https://github.com/abdopcnet/posawesome15_lite)
- 🌿 Branch: **main only**

**🐢 Server Specifications:**
- 💾 **RAM:** 324 GB DDR5
- 🔧 **CPU:** 2x AMD EPYC 9555
- ⚡ **Cores/Threads:** 2024 cores / 128 threads
- 🔋 **Power:** 360 Watt

⚠️ **STRICT POLICY:**  
**Any work done outside this process or not following the Development Server Policy:**
- ❌ Will NOT be reviewed
- ❌ Will NOT be accepted
- ❌ Will NOT be paid

---

## 👨‍💻 Contact

<div align="center">
    <img src="./imgs/ERPNext-support.png" height="200" alt="Future Support" style="border-radius: 20px;">
</div>

**Developer:** abdopcnet  
**Company:** [Future Support](https://www.future-support.online/)  
**Email:** abdopcnet@gmail.com  
**GitHub:** [github.com/abdopcnet/posawesome15_lite](https://github.com/abdopcnet/posawesome15_lite)

**Contact via:**
- 🌐 Website: [future-support.online](https://www.future-support.online/)
- 📱 WhatsApp (EG): [+20 115 648 3669](https://wa.me/201156483669)
- 💬 Telegram (EG): [@abdo_01156483669](https://t.me/abdo_01156483669)
- 📱 WhatsApp (SA): [+966 57 891 9729](https://wa.me/966578919729)
- 💬 Telegram (SA): [@abdo_0578919729](https://t.me/abdo_0578919729)

---

<div align="center">
    <p>Made with ❤️ for ERPNext community</p>
    <p>
        <a href="https://github.com/abdopcnet/posawesome15_lite">⭐ Star</a> •
        <a href="https://github.com/abdopcnet/posawesome15_lite/issues">🐛 Report Bug</a>
    </p>
</div>