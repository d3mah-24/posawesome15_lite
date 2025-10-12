<template>
  <!-- ===== TEMPLATE SECTION 1: MAIN CONTAINER ===== -->
  <nav>
    <v-app-bar app height="40" class="elevation-2 app-navbar">
      <!-- <v-app-bar-nav-icon
        @click.stop="drawer = !drawer"
        class="grey--text"
      ></v-app-bar-nav-icon> -->
      <v-toolbar-title
        @click="go_desk"
        style="cursor: pointer"
        class="text-uppercase primary--text"
      >
      </v-toolbar-title>

      <div class="company-name-badge">
        <v-icon size="14" color="primary">mdi-domain</v-icon>
        <span class="company-name-text">
          {{ company_name }}
        </span>
      </div>

      <div class="invoice-number-badge" :class="invoiceNumberClass">
        <v-icon size="14" :color="invoiceIconColor">mdi-receipt</v-icon>
        <span class="invoice-number-text">
          {{ invoiceNumberText }}
        </span>
      </div>

      <div class="shift-number-badge" :class="shiftNumberClass">
        <v-icon size="14" :color="shiftIconColor">mdi-clock-outline</v-icon>
        <span class="shift-number-text">
          {{ shiftNumberText }}
        </span>
      </div>

      <div class="user-name-badge">
        <v-icon size="14" color="primary">mdi-account</v-icon>
        <span class="user-name-text">
          {{ currentUserName }}
        </span>
      </div>

      <div class="shift-start-badge" :class="shiftStartClass">
        <v-icon size="14" :color="shiftStartIconColor">mdi-clock-start</v-icon>
        <span class="shift-start-text">
          {{ shiftStartText }}
        </span>
      </div>

      <div class="totals-badge">
        <v-icon size="14" color="primary">mdi-counter</v-icon>
        <span class="totals-text">
          SINV_QTY: {{ totalInvoicesQty }}
        </span>
      </div>

      <div class="ping-badge" :class="pingClass">
        <v-icon size="14" :color="pingIconColor">mdi-wifi</v-icon>
        <span class="ping-text">
          Connection: {{ pingTime }}ms
        </span>
      </div>

      <v-spacer></v-spacer>
      <v-btn style="cursor: unset" variant="text" color="primary">
        <span right>{{ pos_profile.name }}</span>
      </v-btn>
      <v-btn icon variant="text"
             :color="last_invoice ? 'primary' : 'grey'"
             :disabled="!last_invoice"
             @click="print_last_invoice"
             :title="last_invoice ? 'Print Last Receipt' : 'No last receipt'">
        <v-icon>mdi-printer</v-icon>
      </v-btn>
      <v-btn icon variant="text"
             color="warning"
             @click="clearCache">
        <v-icon>mdi-cached</v-icon>
      </v-btn>
      <div class="text-center">
        <v-menu offset="y">
          <template v-slot:activator="{ props }">
            <v-btn color="primary" dark variant="text" v-bind="props">
              Menu
            </v-btn>
          </template>
          <v-card class="mx-auto" max-width="300" tile>
            <v-list density="compact" v-model="menu_item">
              <v-list-item
                @click="close_shift_dialog"
                v-if="!pos_profile.posa_hide_closing_shift && menu_item == 0"
              >
                <v-icon class="mr-2">mdi-content-save-move-outline</v-icon>
                <span>Close Shift</span>
              </v-list-item>
              <!-- Removed Print Last Receipt from menu -->
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
    </v-app-bar>
    <!-- <v-navigation-drawer
      v-model="drawer"
      :mini-variant.sync="mini"
      app
      class="primary margen-top"
      width="170"
    >
      <v-list>
        <v-list-item class="px-2">
          <v-avatar>
            <v-img :src="company_img"></v-img>
          </v-avatar>
          <span class="ml-2">{{ company }}</span>
          <v-btn icon @click.stop="mini = !mini">
            <v-icon>mdi-chevron-left</v-icon>
          </v-btn>
        </v-list-item>
        <v-list v-model="item">
          <v-list-item
            v-for="(listItem, index) in items"
            :key="listItem.text"
            @click="changePage(listItem.text)"
          >
            <v-icon class="mr-2">{{ listItem.icon }}</v-icon>
            <span>{{ listItem.text == 'POS' ? 'Point of Sale' : listItem.text == 'Payments' ? 'Payments' : listItem.text }}</span>
          </v-list-item>
        </v-list>
      </v-list>
    </v-navigation-drawer> -->
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
      company_logo: '',
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
        return 'Shift start: Not opened';
      }
      if (!this.pos_opening_shift.period_start_date) {
        return 'Shift start: Unknown';
      }
      const startDate = new Date(this.pos_opening_shift.period_start_date);
      const timeString = startDate.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      });
      return `Shift start: ${timeString}`;
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
          this.company_logo = company_doc.company_logo;
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
          method: 'posawesome.posawesome.api.pos_opening_shift.get_user_shift_invoice_count',
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
          this.company_logo = data.company_logo || '';
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
.margen-top {
  margin-top: 0px;
}

.app-navbar {
  /* Keep navbar pinned while scrolling */
  width: 100%;
  height: 40px;
  position: sticky;
  top: 0;
  left: 0;
  z-index: 1100 !important;
}

/* Invoice Number Badge Styles */
.invoice-number-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  background: #f9f9f9;
  margin-left: 16px;
  font-size: 0.5rem;
  line-height: 1;
  /* ✅ Prevent Layout Shift */
  min-width: 150px;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.invoice-number-text {
  font-weight: 600;
}

.regular-invoice {
  color: #1976d2;
}

.regular-invoice .invoice-number-text {
  color: #1976d2;
}

.return-invoice {
  color: #d32f2f;
}

.return-invoice .invoice-number-text {
  color: #d32f2f;
}

.no-invoice {
  color: #757575;
  font-style: italic;
}

.no-invoice .invoice-number-text {
  color: #757575;
}

/* Company Name Badge Styles */
.company-name-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  background: #f9f9f9;
  margin-left: 8px;
  font-size: 0.5rem;
  line-height: 1;
  /* ✅ Prevent Layout Shift */
  min-width: 180px;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.company-name-text {
  font-weight: 600;
  color: #1976d2;
}

/* Shift Number Badge Styles */
.shift-number-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  background: #f9f9f9;
  margin-left: 8px;
  font-size: 0.5rem;
  line-height: 1;
  /* ✅ Prevent Layout Shift */
  min-width: 120px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.shift-number-text {
  font-weight: 600;
}

.open-shift {
  color: #2e7d32;
}

.open-shift .shift-number-text {
  color: #2e7d32;
}

.closed-shift {
  color: #f57c00;
}

.closed-shift .shift-number-text {
  color: #f57c00;
}

.no-shift {
  color: #757575;
  font-style: italic;
}

.no-shift .shift-number-text {
  color: #757575;
}

/* User Name Badge Styles */
.user-name-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  background: #f9f9f9;
  margin-left: 8px;
  font-size: 0.5rem;
  line-height: 1;
  /* ✅ Prevent Layout Shift */
  min-width: 150px;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-name-text {
  font-weight: 600;
  color: #1976d2;
}

/* Shift Start Badge Styles */
.shift-start-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  background: #f9f9f9;
  margin-left: 8px;
  font-size: 0.5rem;
  line-height: 1;
  /* ✅ Prevent Layout Shift */
  min-width: 200px;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.shift-start-text {
  font-weight: 600;
  color: #1976d2;
}

.open-shift-start {
  border-color: #4caf50;
  background: #e8f5e8;
}

.open-shift-start .shift-start-text {
  color: #2e7d32;
}

.closed-shift-start {
  border-color: #ff9800;
  background: #fff3e0;
}

.closed-shift-start .shift-start-text {
  color: #f57c00;
}

.no-shift-start {
  color: #757575;
  font-style: italic;
}

.no-shift-start .shift-start-text {
  color: #757575;
}

/* Totals Badge Styles */
.totals-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  background: #f9f9f9;
  margin-left: 8px;
  font-size: 0.5rem;
  line-height: 1;
  /* ✅ Prevent Layout Shift */
  min-width: 140px;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.totals-text {
  font-weight: 600;
  color: #1976d2;
}

/* Ping Badge Styles */
.ping-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  background: #f9f9f9;
  margin-left: 8px;
  font-size: 0.5rem;
  line-height: 1;
  /* ✅ Prevent Layout Shift */
  min-width: 180px;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ping-text {
  font-weight: 600;
  color: #1976d2;
}

/* Ping Status Classes */
.ping-excellent {
  border-color: #4caf50;
  background: #e8f5e8;
}

.ping-excellent .ping-text {
  color: #2e7d32;
}

.ping-good {
  border-color: #2196f3;
  background: #e3f2fd;
}

.ping-good .ping-text {
  color: #1976d2;
}

.ping-fair {
  border-color: #ff9800;
  background: #fff3e0;
}

.ping-fair .ping-text {
  color: #f57c00;
}

.ping-poor {
  border-color: #f44336;
  background: #ffebee;
}

.ping-poor .ping-text {
  color: #d32f2f;
}

/* Clear Cache Button Styles */
.v-list-item:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.v-list-item:active {
  background-color: rgba(0, 0, 0, 0.08);
}

/* Cache button animation */
.v-btn[color="warning"]:hover .v-icon {
  animation: rotate 0.5s ease-in-out;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(180deg); }
}
</style>