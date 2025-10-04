<template>
  <!-- ===== TEMPLATE SECTION 1: MAIN CONTAINER ===== -->
  <nav>
    <v-app-bar app height="40" class="elevation-2">
      <!-- <v-app-bar-nav-icon
        @click.stop="drawer = !drawer"
        class="grey--text"
      ></v-app-bar-nav-icon> -->
      <v-img
        :src="company_logo || '/assets/posawesome/js/posapp/components/pos/pos.png'"
        alt="Company Logo"
        max-width="32"
        class="mr-2"
        color="primary"
      ></v-img>
      <v-toolbar-title
        @click="go_desk"
        style="cursor: pointer"
        class="text-uppercase primary--text"
      >
        <span>{{ company_name || 'POS Awesome' }}</span>
      </v-toolbar-title>

      <div class="invoice-number-badge" :class="invoiceNumberClass">
        <v-icon size="18" :color="invoiceIconColor">mdi-receipt</v-icon>
        <span class="invoice-number-text">
          {{ invoiceNumberText }}
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
      if (!this.last_invoice) return;
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
  },
  created: function () {
    this.$nextTick(function () {
      try {
        evntBus.on('show_mesage', (data) => {
          this.show_mesage(data);
        });
        evntBus.on('set_company', (data) => {
          this.company_name = data.name;
          this.company_logo = data.company_logo || '';
        });
        evntBus.on('register_pos_profile', (data) => {
          this.pos_profile = data.pos_profile;
          this.fetch_company_info();
          // External payments screen disabled - removed payments option
        });
        evntBus.on('set_last_invoice', (data) => {
          this.last_invoice = data;
        });
        evntBus.on('update_invoice_doc', (data) => {
          this.invoice_doc = data;
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
  }
};
</script>

<style scoped>
.margen-top {
  margin-top: 0px;
}

.elevation-2 {
  width: 1024px;
  height: 768px;
  z-index: 0 !important;
}

.invoice-number-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  background: #f9f9f9;
  margin-left: 16px;
  font-size: 0.8rem;
  line-height: 1;
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
</style>