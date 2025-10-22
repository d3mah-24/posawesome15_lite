<template>
  <nav>
    <div class="custom-navbar">
      <!-- Logo/Title -->
      <div class="nav-brand" @click="go_desk" title="Go to Desk">
        <i class="mdi mdi-point-of-sale" style="font-size: 16px; color: var(--primary);"></i>
      </div>

      <!-- Info Badges -->
      <div class="nav-badges">
        <div class="badge" :class="invoiceNumberClass">
          <i class="mdi mdi-receipt" :style="`font-size: 12px; color: ${invoiceIconColor};`"></i>
          <span>{{ invoiceNumberText }}</span>
        </div>

        <div class="badge" :class="shiftNumberClass">
          <i class="mdi mdi-clock-outline" :style="`font-size: 12px; color: ${shiftIconColor};`"></i>
          <span>{{ shiftNumberText }}</span>
        </div>

        <div class="badge user-badge">
          <i class="mdi mdi-account" style="font-size: 12px; color: var(--primary);"></i>
          <span>{{ currentUserName }}</span>
        </div>

        <div class="badge" :class="shiftStartClass">
          <i class="mdi mdi-clock-start" :style="`font-size: 12px; color: ${shiftStartIconColor};`"></i>
          <span>{{ shiftStartText }}</span>
        </div>

        <div class="badge totals-badge">
          <i class="mdi mdi-counter" style="font-size: 12px; color: var(--primary);"></i>
          <span>QTY: {{ totalInvoicesQty }}</span>
        </div>

        <div class="badge" :class="pingClass">
          <i class="mdi mdi-wifi" :style="`font-size: 12px; color: ${pingIconColor};`"></i>
          <span>{{ pingTime }}ms</span>
        </div>

        <div class="badge profile-badge">
          <i class="mdi mdi-briefcase" style="font-size: 12px; color: var(--primary);"></i>
          <span>{{ pos_profile.name }}</span>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="nav-actions">
        <button
          class="action-btn"
          :class="{ disabled: !last_invoice }"
          :disabled="!last_invoice"
          @click="print_last_invoice"
          :title="last_invoice ? 'Print Last Receipt' : 'No last receipt'"
        >
          <i class="mdi mdi-printer" :style="`font-size: 14px; color: ${last_invoice ? 'var(--primary)' : 'var(--gray-500)'};`"></i>
        </button>

        <button
          class="action-btn cache-btn"
          @click="clearCache"
          title="Clear Cache"
        >
          <i class="mdi mdi-cached" style="font-size: 14px; color: var(--warning);"></i>
        </button>

        <div class="menu-wrapper">
          <div class="dropdown">
            <button class="action-btn menu-btn" @click="toggleMenu">
              <i class="mdi mdi-menu" style="font-size: 14px;"></i>
              <span>Menu</span>
            </button>
            <div v-if="showMenu" class="dropdown-menu">
              <div class="menu-list">
                <div
                  class="menu-item"
                  @click="close_shift_dialog"
                  v-if="!pos_profile.posa_hide_closing_shift && menu_item == 0"
                >
                  <div class="menu-icon close-shift-icon">
                    <i class="mdi mdi-content-save-move-outline" style="font-size: 16px;"></i>
                  </div>
                  <div class="menu-text">Close Shift</div>
                </div>

                <div class="menu-item" @click="logOut">
                  <div class="menu-icon logout-icon">
                    <i class="mdi mdi-logout" style="font-size: 16px;"></i>
                  </div>
                  <div class="menu-text">Logout</div>
                </div>

                <div class="menu-item" @click="go_about">
                  <div class="menu-icon about-icon">
                    <i class="mdi mdi-information-outline" style="font-size: 16px;"></i>
                  </div>
                  <div class="menu-text">About System</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="snack" class="snackbar" :class="snackColor" @click="snack = false">
      {{ snackText }}
    </div>
    <div v-if="freeze" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">{{ freezeTitle }}</h3>
        </div>
        <div class="modal-body">
          {{ freezeMsg }}
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
// ===== SECTION 1: IMPORTS =====
import { evntBus } from "../bus";
// Import cache manager utility
import "../../utils/clearAllCaches.js";
import { API_MAP } from "../api_mapper.js";

// ===== SECTION 2: EXPORT DEFAULT =====
export default {
  // components: {MyPopup},
  // ===== SECTION 3: DATA =====
  data() {
    return {
      drawer: false,
      mini: true,
      item: 0,
      items: [{ text: "POS", icon: "mdi-network-pos" }],
      page: "",
      fav: true,
      menu: false,
      showMenu: false,
      message: false,
      hints: true,
      menu_item: 0,
      snack: false,
      snackColor: "",
      snackText: "",
      company_name: "",
      pos_profile: "",
      freeze: false,
      freezeTitle: "",
      freezeMsg: "",
      last_invoice: "",
      invoice_doc: null,
      pos_opening_shift: null,
      shift_invoice_count: 0,
      // Ping variables
      pingTime: "000",
      pingInterval: null,
    };
  },
  computed: {
    invoiceNumberText() {
      if (!this.invoice_doc || !this.invoice_doc.name) {
        return "Invoice not created yet";
      }
      return this.invoice_doc.name;
    },
    invoiceNumberClass() {
      if (!this.invoice_doc || !this.invoice_doc.name) {
        return "no-invoice";
      }
      return this.invoice_doc.is_return ? "return-invoice" : "regular-invoice";
    },
    invoiceIconColor() {
      if (!this.invoice_doc || !this.invoice_doc.name) {
        return "grey";
      }
      return this.invoice_doc.is_return ? "error" : "primary";
    },
    shiftNumberText() {
      if (!this.pos_opening_shift || !this.pos_opening_shift.name) {
        return "Shift not opened yet";
      }
      return this.pos_opening_shift.name;
    },
    shiftNumberClass() {
      if (!this.pos_opening_shift || !this.pos_opening_shift.name) {
        return "no-shift";
      }
      return this.pos_opening_shift.status === "Open"
        ? "open-shift"
        : "closed-shift";
    },
    shiftIconColor() {
      if (!this.pos_opening_shift || !this.pos_opening_shift.name) {
        return "grey";
      }
      return this.pos_opening_shift.status === "Open" ? "success" : "warning";
    },
    currentUserName() {
      return frappe.session.user || "Unknown User";
    },
    shiftStartText() {
      if (!this.pos_opening_shift || !this.pos_opening_shift.name) {
        return "Not opened";
      }
      if (!this.pos_opening_shift.period_start_date) {
        return "Unknown";
      }
      const startDate = new Date(this.pos_opening_shift.period_start_date);
      const timeString = startDate.toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: true,
      });
      return `${timeString}`;
    },
    shiftStartClass() {
      if (!this.pos_opening_shift || !this.pos_opening_shift.name) {
        return "no-shift-start";
      }
      return this.pos_opening_shift.status === "Open"
        ? "open-shift-start"
        : "closed-shift-start";
    },
    shiftStartIconColor() {
      if (!this.pos_opening_shift || !this.pos_opening_shift.name) {
        return "grey";
      }
      return this.pos_opening_shift.status === "Open" ? "success" : "warning";
    },
    totalInvoicesQty() {
      // Get total invoices count for current shift
      if (
        !this.pos_opening_shift ||
        !this.pos_opening_shift.name ||
        !this.pos_profile
      ) {
        return "000";
      }
      return this.shift_invoice_count || "000";
    },
    // Ping computed properties
    pingClass() {
      const ping = parseInt(this.pingTime);
      if (ping < 100) return "ping-excellent";
      if (ping < 300) return "ping-good";
      if (ping < 500) return "ping-fair";
      return "ping-poor";
    },
    pingIconColor() {
      const ping = parseInt(this.pingTime);
      if (ping < 100) return "success";
      if (ping < 300) return "primary";
      if (ping < 500) return "warning";
      return "error";
    },
  },
  // ===== SECTION 3.5: WATCHERS =====
  watch: {
    showMenu(newVal, oldVal) {
      // Menu visibility watcher - cleaned up debug logs
    }
  },
  // ===== SECTION 4: METHODS =====
  methods: {
    changePage(key) {
      this.$emit("changePage", key);
    },
    toggleMenu() {
      this.showMenu = !this.showMenu;
      
      // Add click outside handler when menu opens
      if (this.showMenu) {
        // Use setTimeout to avoid catching the same click that opened the menu
        setTimeout(() => {
          document.addEventListener('click', this.handleClickOutside);
        }, 50);

        // Position menu to stay within viewport
        this.$nextTick(() => {
          const menuElement = this.$el.querySelector('.dropdown-menu');
          const menuButton = this.$el.querySelector('.menu-btn');
          
          if (menuElement && menuButton) {
            const buttonRect = menuButton.getBoundingClientRect();
            const menuWidth = 200; // min-width from CSS
            const viewportWidth = window.innerWidth;
            
            // Check if menu would overflow on the right
            if (buttonRect.right < menuWidth) {
              // Not enough space on right, align to left edge of button
              menuElement.style.right = 'auto';
              menuElement.style.left = '0';
            } else {
              // Enough space, keep right alignment
              menuElement.style.right = '0';
              menuElement.style.left = 'auto';
            }
          }
        });
      } else {
        document.removeEventListener('click', this.handleClickOutside);
      }
    },
    handleClickOutside(event) {
      // Check if click is outside the menu wrapper
      const menuWrapper = this.$el.querySelector('.menu-wrapper');
      if (menuWrapper && !menuWrapper.contains(event.target)) {
        this.showMenu = false;
        document.removeEventListener('click', this.handleClickOutside);
      }
    },
    go_desk() {
      frappe.set_route("/");
      location.reload();
    },
    go_about() {
      this.showMenu = false; // Close menu after action
      const win = window.open("https://github.com/abdopcnet", "_blank");
      win.focus();
    },
    close_shift_dialog() {
      this.showMenu = false; // Close menu after action
      evntBus.emit("open_closing_dialog");
    },
    show_mesage(data) {
      this.snack = true;
      this.snackColor = data.color;
      this.snackText = data.text;
      
      // Auto-hide snackbar after 4 seconds
      setTimeout(() => {
        this.snack = false;
      }, 4000);
    },
    logOut() {
      this.showMenu = false; // Close menu after action
      var me = this;
      me.logged_out = true;
      return frappe.call({
        method: "logout",
        callback: function (r) {
          if (r.exc) {
            return;
          }
          // Instead of automatic reload, let the user manually reload
          me.show_mesage({
            color: "info",
            text: "Logged out successfully. Click to reload.",
          });
          // Only reload when user clicks on the message
          document.querySelector(".snackbar").addEventListener("click", function() {
            frappe.set_route("/login");
            location.reload();
          });
        },
      });
    },
    print_last_invoice() {
      if (!this.last_invoice) {
        return;
      }
      const print_format =
        this.pos_profile.print_format_for_online ||
        this.pos_profile.print_format;
      const letter_head = this.pos_profile.letter_head || 0;
      const url =
        frappe.urllib.get_base_url() +
        "/printview?doctype=Sales%20Invoice&name=" +
        this.last_invoice +
        "&trigger_print=1" +
        "&format=" +
        print_format +
        "&no_letterhead=" +
        letter_head;
      const printWindow = window.open(url, "Print");
      printWindow.addEventListener(
        "load",
        function () {
          printWindow.print();
        },
        true
      );
    },
    fetch_company_info() {
      if (this.pos_profile && this.pos_profile.company) {
        frappe.db
          .get_doc("Company", this.pos_profile.company)
          .then((company_doc) => {
            this.company_name = company_doc.company_name;
          })
          .catch(() => {
            // Error fetching company info
          });
      }
    },
    async clearCache() {
      try {
        // Show loading message
        this.show_mesage({
          color: "info",
          text: "Clearing cache...",
        });

        // Use the comprehensive cache manager
        if (window.cacheManager) {
          const success = await window.cacheManager.clearAllCaches();

          if (success) {
            this.show_mesage({
              color: "success",
              text: "Cache cleared successfully. Reloading...",
            });

            // Reload page after short delay
            setTimeout(() => {
              location.reload();
            }, 1000);
          } else {
            this.show_mesage({
              color: "error",
              text: "Error clearing cache",
            });
          }
        } else {
          // Fallback to basic cache clearing
          localStorage.clear();
          sessionStorage.clear();

          this.show_mesage({
            color: "success",
            text: "Basic cache cleared. Reloading...",
          });

          setTimeout(() => {
            location.reload();
          }, 1000);
        }
      } catch (error) {
        this.show_mesage({
          color: "error",
          text: "Error clearing cache: " + error.message,
        });
      }
    },
    async fetchShiftInvoiceCount() {
      if (!this.pos_profile || !this.pos_opening_shift) {
        return;
      }

      try {
        const response = await frappe.call({
          method: API_MAP.POS_OPENING_SHIFT.GET_USER_SHIFT_INVOICE_COUNT,
          args: {
            pos_profile: this.pos_profile.name,
            pos_opening_shift: this.pos_opening_shift.name,
          },
        });

        if (response.message !== undefined) {
          this.shift_invoice_count = response.message;
        }
      } catch (error) {
        this.shift_invoice_count = 0;
      }
    },
    // Ping methods
    async measurePing() {
      // Skip if connection issues might cause a reload
      if (navigator.onLine === false) {
        this.pingTime = "999";
        return;
      }
      
      const startTime = performance.now();
      try {
        await frappe.call({
          method: "frappe.ping",
          args: {},
          callback: () => {
            const endTime = performance.now();
            const ping = Math.round(endTime - startTime);
            this.pingTime = ping.toString().padStart(3, "0");
          },
          error: () => {
            // Silently handle error without triggering page reload
            this.pingTime = "999";
          },
          freeze: false,  // Don't freeze the UI
          show_spinner: false, // Don't show spinner
          async: true,  // Make sure it's async
        });
      } catch (error) {
        // Capture error without allowing it to affect the application
        this.pingTime = "999";
      }
    },
    startPingMonitoring() {
      // Safety check - if already monitoring, don't start another interval
      if (this.pingInterval) {
        return;
      }
      
      // Track that we're running (for visibility change handler)
      this._wasRunningBeforeHidden = true;
      
      // Initial ping
      this.measurePing();

      // Set up interval for continuous monitoring (every 5 seconds)
      this.pingInterval = setInterval(() => {
        this.measurePing();
      }, 5000);
    },
    stopPingMonitoring() {
      if (this.pingInterval) {
        clearInterval(this.pingInterval);
        this.pingInterval = null;
        // Track that monitoring is stopped
        this._wasRunningBeforeHidden = false;
      }
    },
    
    // Toggle ping monitoring (can be called via evntBus)
    togglePingMonitoring(enable) {
      if (enable) {
        sessionStorage.setItem('pos_enable_ping_monitoring', 'true');
        this.startPingMonitoring();
      } else {
        sessionStorage.setItem('pos_enable_ping_monitoring', 'false');
        this.stopPingMonitoring();
      }
    },
  },
  created: function () {
    this.$nextTick(function () {
      try {
        // Check if ping monitoring should be enabled
        // We can add a global setting to control this
        const enablePingMonitoring = sessionStorage.getItem('pos_enable_ping_monitoring') !== 'false';
        
        if (enablePingMonitoring) {
          // Start ping monitoring
          this.startPingMonitoring();
        }

        // Add page visibility handler to pause/resume ping monitoring for bfcache compatibility
        // Modified to prevent automatic reloads
        this.handleVisibilityChange = () => {
          if (document.hidden) {
            this.stopPingMonitoring();
          } else {
            // Only restart monitoring if it was previously running
            if (this._wasRunningBeforeHidden) {
              this.startPingMonitoring();
            }
          }
        };
        // Track ping monitor state before hiding
        this._wasRunningBeforeHidden = true; 
        document.addEventListener('visibilitychange', this.handleVisibilityChange);

        evntBus.on("show_mesage", (data) => {
          this.show_mesage(data);
        });
        evntBus.on("set_company", (data) => {
          this.company_name = data.name;
        });
        evntBus.on("register_pos_profile", (data) => {
          this.pos_profile = data.pos_profile;
          this.pos_opening_shift = data.pos_opening_shift;
          this.fetch_company_info();
          this.fetchShiftInvoiceCount();
          // External payments screen disabled - removed payments option
        });
        evntBus.on("set_last_invoice", (data) => {
          this.last_invoice = data;
        });
        evntBus.on("update_invoice_doc", (data) => {
          this.invoice_doc = data;
        });
        evntBus.on("set_pos_opening_shift", (data) => {
          this.pos_opening_shift = data;
          this.fetchShiftInvoiceCount();
        });
        evntBus.on("register_pos_data", (data) => {
          this.pos_opening_shift = data.pos_opening_shift;
        });
        evntBus.on("invoice_submitted", () => {
          // Refresh invoice count when a new invoice is submitted
          // Add delay to wait for background job to complete
          setTimeout(() => {
            this.fetchShiftInvoiceCount();
          }, 2000); // Wait 2 seconds for background job
        });
        evntBus.on("freeze", (data) => {
          this.freeze = true;
          this.freezeTitle = data.title;
          this.freezeMsg = data.msg;
        });
        evntBus.on("unfreeze", () => {
          this.freeze = false;
          this.freezTitle = "";
          this.freezeMsg = "";
        });
        
        // Add event listener for toggling ping monitoring
        evntBus.on("toggle_ping_monitoring", (enable) => {
          this.togglePingMonitoring(enable);
        });
      } catch (error) {
        this.show_mesage({
          color: "error",
          text: "An error occurred while loading the menu.",
        });
      }
    });
  },
  beforeUnmount() {
    // Clean up ping monitoring
    this.stopPingMonitoring();

    // Clean up click outside listener
    document.removeEventListener('click', this.handleClickOutside);
    
    // Clean up page visibility listener
    document.removeEventListener('visibilitychange', this.handleVisibilityChange);

    // Clean up all event listeners
    evntBus.off("show_mesage");
    evntBus.off("set_company");
    evntBus.off("register_pos_profile");
    evntBus.off("set_last_invoice");
    evntBus.off("update_invoice_doc");
    evntBus.off("set_pos_opening_shift");
    evntBus.off("register_pos_data");
    evntBus.off("invoice_submitted");
    evntBus.off("freeze");
    evntBus.off("unfreeze");
    evntBus.off("toggle_ping_monitoring");
  },
};
</script>

<style scoped>
/* Ultra-compact custom navbar */
.custom-navbar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 6px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  height: 32px;
  position: sticky;
  top: 0;
  z-index: 1100;
}

/* Brand/Logo */
.nav-brand {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px 8px;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
}

.nav-brand:hover {
  background: rgba(25, 118, 210, 0.08);
}

/* Badges Container */
.nav-badges {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 3px;
  overflow-x: auto;
  scrollbar-width: none;
}

.nav-badges::-webkit-scrollbar {
  display: none;
}

/* Badge Styles - Ultra Compact */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  background: #fff;
  font-size: 10px;
  font-weight: 600;
  white-space: nowrap;
  transition: all 0.2s;
  line-height: 1;
  height: 22px;
}

.badge span {
  white-space: nowrap;
}

/* Badge Variants */
.badge.regular-invoice {
  border-color: #1976d2;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  color: #1976d2;
}

.badge.return-invoice {
  border-color: #d32f2f;
  background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
  color: #d32f2f;
}

.badge.no-invoice {
  border-color: #bdbdbd;
  background: #f5f5f5;
  color: #757575;
  font-style: italic;
}

.badge.open-shift {
  border-color: #4caf50;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  color: #2e7d32;
}

.badge.closed-shift {
  border-color: #ff9800;
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  color: #f57c00;
}

.badge.no-shift {
  border-color: #bdbdbd;
  background: #f5f5f5;
  color: #757575;
  font-style: italic;
}

.badge.user-badge {
  border-color: #1976d2;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  color: #1976d2;
}

.badge.shift-active {
  border-color: #4caf50;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  color: #2e7d32;
}

.badge.no-shift-start {
  border-color: #bdbdbd;
  background: #f5f5f5;
  color: #757575;
}

.badge.totals-badge {
  border-color: #1976d2;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  color: #1976d2;
}

.badge.ping-excellent {
  border-color: #4caf50;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  color: #2e7d32;
}

.badge.ping-good {
  border-color: #2196f3;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  color: #1976d2;
}

.badge.ping-fair {
  border-color: #ff9800;
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  color: #f57c00;
}

.badge.ping-poor {
  border-color: #f44336;
  background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
  color: #d32f2f;
}

.badge.profile-badge {
  border-color: #1976d2;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  color: #1976d2;
  font-weight: 700;
}

/* Actions Container */
.nav-actions {
  display: flex;
  align-items: center;
  gap: 3px;
}

/* Action Buttons - Beautiful Custom Design */
.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 3px;
  padding: 3px 6px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 11px;
  font-weight: 600;
  height: 24px;
  min-width: 24px;
}

.action-btn:hover:not(.disabled) {
  background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%);
  border-color: #bdbdbd;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.action-btn:active:not(.disabled) {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}

.action-btn.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.cache-btn:hover {
  border-color: #ff9800;
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
}

.menu-btn {
  border-color: #1976d2;
  background: linear-gradient(135deg, #1976d2 0%, #1e88e5 100%);
  color: white;
}

.menu-btn:hover span,
.menu-btn:hover .v-icon {
  color: #1976d2;
}

.menu-btn span {
  color: white;
}

.menu-wrapper {
  display: flex;
}

/* Cache button rotation animation */
.cache-btn:active .v-icon {
  animation: spin 0.4s ease-in-out;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(180deg);
  }
}

/* ===== DROPDOWN MENU STYLES ===== */
.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1200;
  min-width: 200px;
  margin-top: 4px;
  overflow: hidden;
  display: block !important; /* Force display */
  /* Prevent overflow outside viewport */
  max-width: calc(100vw - 10px);
}

.menu-list {
  padding: 4px;
  background: white;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-radius: 6px;
  margin: 2px 0;
  min-height: 40px;
}

.menu-item:hover {
  background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%);
}

.menu-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  transition: all 0.2s ease;
}

.close-shift-icon {
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
  color: white;
}

.logout-icon {
  background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
  color: white;
}

.about-icon {
  background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
  color: white;
}

.menu-item:hover .menu-icon {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.menu-text {
  font-size: 0.875rem;
  font-weight: 600;
  color: #333;
  letter-spacing: 0.2px;
}

/* Responsive - tighter at small screens */
@media (max-width: 1024px) {
  .custom-navbar {
    gap: 2px;
    padding: 2px 4px;
  }

  .nav-badges {
    gap: 2px;
  }

  .badge {
    padding: 2px 4px;
    font-size: 10px;
  }
}

/* Legacy styles cleanup */
.margen-top {
  margin-top: 0px;
}

/* ===== SNACKBAR NOTIFICATION STYLES ===== */
.snackbar {
  position: fixed;
  top: 40px;
  left: 50%;
  transform: translateX(-50%);
  min-width: 300px;
  max-width: 500px;
  padding: 12px 20px;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  font-size: 14px;
  z-index: 2000;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideDown 0.3s ease-out;
  text-align: center;
}

.snackbar.success {
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
  border: 1px solid #4caf50;
}

.snackbar.error {
  background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
  border: 1px solid #f44336;
}

.snackbar.info {
  background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
  border: 1px solid #2196f3;
}

.snackbar.warning {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
  border: 1px solid #ff9800;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* Modal overlay styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
}

.modal {
  background: white;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-title {
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.modal-body {
  padding: 20px;
  color: #666;
  line-height: 1.5;
}
</style>
