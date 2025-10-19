<template>
  <nav>
    <div class="custom-navbar">
      <!-- Logo/Title -->
      <div class="nav-brand" @click="go_desk" title="Go to Desk">
        <v-icon size="16" color="primary">mdi-point-of-sale</v-icon>
      </div>

      <!-- Info Badges -->
      <div class="nav-badges">
        <div class="badge" :class="invoiceNumberClass">
          <v-icon size="12" :color="invoiceIconColor">mdi-receipt</v-icon>
          <span>{{ invoiceNumberText }}</span>
        </div>

        <div class="badge" :class="shiftNumberClass">
          <v-icon size="12" :color="shiftIconColor">mdi-clock-outline</v-icon>
          <span>{{ shiftNumberText }}</span>
        </div>

        <div class="badge user-badge">
          <v-icon size="12" color="primary">mdi-account</v-icon>
          <span>{{ currentUserName }}</span>
        </div>

        <div class="badge" :class="shiftStartClass">
          <v-icon size="12" :color="shiftStartIconColor">mdi-clock-start</v-icon>
          <span>{{ shiftStartText }}</span>
        </div>

        <div class="badge totals-badge">
          <v-icon size="12" color="primary">mdi-counter</v-icon>
          <span>QTY: {{ totalInvoicesQty }}</span>
        </div>

        <div class="badge" :class="pingClass">
          <v-icon size="12" :color="pingIconColor">mdi-wifi</v-icon>
          <span>{{ pingTime }}ms</span>
        </div>

        <div class="badge profile-badge">
          <v-icon size="12" color="primary">mdi-briefcase</v-icon>
          <span>{{ pos_profile.name }}</span>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="nav-actions">
        <button class="action-btn" :class="{ disabled: !last_invoice }" :disabled="!last_invoice"
          @click="print_last_invoice" :title="last_invoice ? 'Print Last Receipt' : 'No last receipt'">
          <v-icon size="14" :color="last_invoice ? 'primary' : 'grey'">mdi-printer</v-icon>
        </button>

        <button class="action-btn cache-btn" @click="clearCache" title="Clear Cache">
          <v-icon size="14" color="warning">mdi-cached</v-icon>
        </button>

        <div class="menu-wrapper">
          <v-menu offset="y">
            <template v-slot:activator="{ props }">
              <button class="action-btn menu-btn" v-bind="props">
                <v-icon size="14">mdi-menu</v-icon>
                <span>Menu</span>
              </button>
            </template>
            <v-card class="mx-auto" max-width="300" tile>
              <v-list density="compact" v-model="menu_item">
                <v-list-item @click="close_shift_dialog" v-if="!pos_profile.posa_hide_closing_shift && menu_item == 0">
                  <v-icon class="mr-2">mdi-content-save-move-outline</v-icon>
                  <span>Close Shift</span>
                </v-list-item>
                <v-divider class="my-0"></v-divider>
                <v-list-item @click="logOut">
                  <v-icon class="mr-2">mdi-logout</v-icon>
                  <span>Logout</span>
                </v-list-item>
                <v-list-item @click="go_about">
                  <v-icon class="mr-2">mdi-information-outline</v-icon>
                  <span>About System</span>
                </v-list-item>
                <v-divider class="my-0"></v-divider>
              </v-list>
            </v-card>
          </v-menu>
        </div>
      </div>
    </div>
    <v-snackbar v-model="snack" :timeout="5000" :color="snackColor" top right @click="snack = false">
      {{ snackText }}
    </v-snackbar>
    <v-dialog v-model="freeze" persistent max-width="290">
      <v-card>
        <v-card-title class="text-h5">{{ freezeTitle }}</v-card-title>
        <v-card-text>{{ freezeMsg }}</v-card-text>
      </v-card>
    </v-dialog>
  </nav>
</template>

<script>
// ===== SECTION 1: IMPORTS =====
import { evntBus } from '../bus';
// Import cache manager utility
import '../../utils/clearAllCaches.js';
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
      items: [
        { text: 'POS', icon: 'mdi-network-pos' }
      ],
      page: '',
      fav: true,
      menu: false,
      message: false,
      hints: true,
      menu_item: 0,
      snack: false,
      snackColor: '',
      snackText: '',
      company_name: '',
      pos_profile: '',
      freeze: false,
      freezeTitle: '',
      freezeMsg: '',
      last_invoice: '',
      invoice_doc: null,
      pos_opening_shift: null,
      shift_invoice_count: 0,
      // Ping variables
      pingTime: '000',
      pingInterval: null,
    };
  },
  computed: {
    invoiceNumberText() {
      if (!this.invoice_doc || !this.invoice_doc.name) {
        return 'Invoice not created yet';
      }
      return this.invoice_doc.name;
    },
    invoiceNumberClass() {
      if (!this.invoice_doc || !this.invoice_doc.name) {
        return 'no-invoice';
      }
      return this.invoice_doc.is_return ? 'return-invoice' : 'regular-invoice';
    },
    invoiceIconColor() {
      if (!this.invoice_doc || !this.invoice_doc.name) {
        return 'grey';
      }
      return this.invoice_doc.is_return ? 'error' : 'primary';
    },
    shiftNumberText() {
      if (!this.pos_opening_shift || !this.pos_opening_shift.name) {
        return 'Shift not opened yet';
      }
      return this.pos_opening_shift.name;
    },
    shiftNumberClass() {
      if (!this.pos_opening_shift || !this.pos_opening_shift.name) {
        return 'no-shift';
      }
      return this.pos_opening_shift.status === 'Open' ? 'open-shift' : 'closed-shift';
    },
    shiftIconColor() {
      if (!this.pos_opening_shift || !this.pos_opening_shift.name) {
        return 'grey';
      }
      return this.pos_opening_shift.status === 'Open' ? 'success' : 'warning';
    },
    currentUserName() {
      return frappe.session.user || 'Unknown User';
    },
    shiftStartText() {
      if (!this.pos_opening_shift || !this.pos_opening_shift.name) {
        return 'Not opened';
      }
      if (!this.pos_opening_shift.period_start_date) {
        return 'Unknown';
      }
      const startDate = new Date(this.pos_opening_shift.period_start_date);
      const timeString = startDate.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      });
      return `${timeString}`;
    },
    shiftStartClass() {
      if (!this.pos_opening_shift || !this.pos_opening_shift.name) {
        return 'no-shift-start';
      }
      return this.pos_opening_shift.status === 'Open' ? 'open-shift-start' : 'closed-shift-start';
    },
    shiftStartIconColor() {
      if (!this.pos_opening_shift || !this.pos_opening_shift.name) {
        return 'grey';
      }
      return this.pos_opening_shift.status === 'Open' ? 'success' : 'warning';
    },
    totalInvoicesQty() {
      // Get total invoices count for current shift
      if (!this.pos_opening_shift || !this.pos_opening_shift.name || !this.pos_profile) {
        return '000';
      }
      return this.shift_invoice_count || '000';
    },
    // Ping computed properties
    pingClass() {
      const ping = parseInt(this.pingTime);
      if (ping < 100) return 'ping-excellent';
      if (ping < 300) return 'ping-good';
      if (ping < 500) return 'ping-fair';
      return 'ping-poor';
    },
    pingIconColor() {
      const ping = parseInt(this.pingTime);
      if (ping < 100) return 'success';
      if (ping < 300) return 'primary';
      if (ping < 500) return 'warning';
      return 'error';
    }
  },
  // ===== SECTION 4: METHODS =====
  methods: {
    changePage(key) {
      this.$emit('changePage', key);
    },
    go_desk() {
      frappe.set_route('/');
      location.reload();
    },
    go_about() {
      const win = window.open(
        'https://github.com/abdopcnet',
        '_blank'
      );
      win.focus();
    },
    close_shift_dialog() {
      evntBus.emit('open_closing_dialog');
    },
    show_mesage(data) {
      this.snack = true;
      this.snackColor = data.color;
      this.snackText = data.text;
    },
    logOut() {
      var me = this;
      me.logged_out = true;
      return frappe.call({
        method: 'logout',
        callback: function (r) {
          if (r.exc) {
            return;
          }
          frappe.set_route('/login');
          location.reload();
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
        '/printview?doctype=Sales%20Invoice&name=' +
        this.last_invoice +
        '&trigger_print=1' +
        '&format=' +
        print_format +
        '&no_letterhead=' +
        letter_head;
      const printWindow = window.open(url, 'Print');
      printWindow.addEventListener(
        'load',
        function () {
          printWindow.print();
        },
        true
      );
    },
    fetch_company_info() {
      if (this.pos_profile && this.pos_profile.company) {
        frappe.db.get_doc('Company', this.pos_profile.company).then((company_doc) => {
          this.company_name = company_doc.company_name;
        }).catch(() => {
          // Error fetching company info
        });
      }
    },
    async clearCache() {
      try {
        // Show loading message
        this.show_mesage({
          color: 'info',
          text: 'Clearing cache...'
        });

        // Use the comprehensive cache manager
        if (window.cacheManager) {
          const success = await window.cacheManager.clearAllCaches();

          if (success) {
            this.show_mesage({
              color: 'success',
              text: 'Cache cleared successfully. Reloading...'
            });

            // Reload page after short delay
            setTimeout(() => {
              location.reload();
            }, 1000);
          } else {
            this.show_mesage({
              color: 'error',
              text: 'Error clearing cache'
            });
          }
        } else {
          // Fallback to basic cache clearing
          localStorage.clear();
          sessionStorage.clear();

          this.show_mesage({
            color: 'success',
            text: 'Basic cache cleared. Reloading...'
          });

          setTimeout(() => {
            location.reload();
          }, 1000);
        }

      } catch (error) {
        this.show_mesage({
          color: 'error',
          text: 'Error clearing cache: ' + error.message
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
            pos_opening_shift: this.pos_opening_shift.name
          }
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
      const startTime = performance.now();
      try {
        await frappe.call({
          method: 'frappe.ping',
          args: {},
          callback: () => {
            const endTime = performance.now();
            const ping = Math.round(endTime - startTime);
            this.pingTime = ping.toString().padStart(3, '0');
          }
        });
      } catch (error) {
        this.pingTime = '999';
      }
    },
    startPingMonitoring() {
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
      }
    },
  },
  created: function () {
    this.$nextTick(function () {
      try {
        // Start ping monitoring
        this.startPingMonitoring();

        evntBus.on('show_mesage', (data) => {
          this.show_mesage(data);
        });
        evntBus.on('set_company', (data) => {
          this.company_name = data.name;
        });
        evntBus.on('register_pos_profile', (data) => {
          this.pos_profile = data.pos_profile;
          this.pos_opening_shift = data.pos_opening_shift;
          this.fetch_company_info();
          this.fetchShiftInvoiceCount();
          // External payments screen disabled - removed payments option
        });
        evntBus.on('set_last_invoice', (data) => {
          this.last_invoice = data;
        });
        evntBus.on('update_invoice_doc', (data) => {
          this.invoice_doc = data;
        });
        evntBus.on('set_pos_opening_shift', (data) => {
          this.pos_opening_shift = data;
          this.fetchShiftInvoiceCount();
        });
        evntBus.on('register_pos_data', (data) => {
          this.pos_opening_shift = data.pos_opening_shift;
        });
        evntBus.on('invoice_submitted', () => {
          // Refresh invoice count when a new invoice is submitted
          // Add delay to wait for background job to complete
          setTimeout(() => {
            this.fetchShiftInvoiceCount();
          }, 2000); // Wait 2 seconds for background job
        });
        evntBus.on('freeze', (data) => {
          this.freeze = true;
          this.freezeTitle = data.title;
          this.freezeMsg = data.msg;
        });
        evntBus.on('unfreeze', () => {
          this.freeze = false;
          this.freezTitle = '';
          this.freezeMsg = '';
        });
      } catch (error) {
        this.show_mesage({
          color: 'error',
          text: 'An error occurred while loading the menu.'
        });
      }
    });
  },
  beforeDestroy() {
    // Clean up ping monitoring
    this.stopPingMonitoring();
  }
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
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.action-btn:active:not(.disabled) {
  transform: translateY(0);
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
</style>
