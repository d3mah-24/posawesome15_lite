<template>
  <!-- ===== TEMPLATE SECTION 1: MAIN CONTAINER ===== -->
  <v-row justify="center">
    {{ console.log({template: "main container", result: "main container rendered"}) }}
    <v-dialog v-model="invoicesDialog" max-width="800px" min-width="800px">
      <v-card>
        <v-card-title>
          <span class="headline primary--text">Return Invoice</span>
        </v-card-title>
        <v-container>
          <v-row class="mb-4">
            <v-text-field
              color="primary"
              :label="'Invoice Number'"
              background-color="white"
              hide-details
              v-model="invoice_name"
              dense
              clearable
              class="mx-4"
              @keydown.enter="search_invoices"
            ></v-text-field>
            <v-btn text class="ml-2" color="primary" dark @click="search_invoices">
              Search
            </v-btn>
          </v-row>
          <v-row>
            <v-col cols="12" class="pa-1">
              <v-data-table
                :headers="headers"
                :items="dialog_data"
                item-value="name"
                class="elevation-1"
                show-select
                v-model="selected"
                :loading="isLoading"
                loading-text="Loading invoices..."
                no-data-text="No invoices found"
              >
                <template v-slot:[`item.grand_total`]="{ item }">
                  {{ currencySymbol(item.currency) }} {{ formatCurrency(item.grand_total) }}
                </template>
              </v-data-table>
            </v-col>
          </v-row>
        </v-container>
        <v-card-actions class="mt-4">
          <v-spacer></v-spacer>
          <v-btn color="error mx-2" dark @click="close_dialog">Close</v-btn>
          <v-btn color="success" dark @click="submit_dialog">
            Select
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
// ===== SECTION 1: IMPORTS =====
console.log({script: "imports start"});
import { evntBus } from '../../bus';
import format from '../../format';
console.log({script: "imports end", result: "2 imports loaded successfully"});

// ===== SECTION 2: EXPORT DEFAULT =====
export default {
  mixins: [format],
  // ===== SECTION 3: DATA =====
  data: () => {
    console.log({script: "data start"});
    return {
    invoicesDialog: false,
    selected: [],
    dialog_data: [],
    isLoading: false,
    company: '',
    invoice_name: '',
    pos_profile: null,
    pos_opening_shift: null,
    headers: [
      { title: 'Customer', key: 'customer', align: 'start', sortable: true },
      { title: 'Date', key: 'posting_date', align: 'start', sortable: true },
      { title: 'Invoice Number', key: 'name', align: 'start', sortable: true },
      { title: 'Amount', key: 'grand_total', align: 'end', sortable: false }
      ]
    };
    console.log({script: "data end", result: "data object initialized successfully"});
  },
  beforeUnmount() {
    evntBus.off('open_returns');
  },
  methods: {
    close_dialog() {
      this.$nextTick(() => {
        this.invoicesDialog = false;
        this.selected = [];
        this.dialog_data = [];
        this.invoice_name = '';
      });
    },
    search_invoices() {
                // Set company from latest pos_profile or pos_opening_shift if available
      this.company = this.pos_profile?.company || this.pos_opening_shift?.company || this.company;
      if (!this.company && !this.invoice_name) {
        evntBus.emit('show_mesage', {
          text: 'Please enter invoice number or select company first',
          color: 'error'
        });
        return;
      }
      this.isLoading = true;
      frappe.call({
        method: 'posawesome.posawesome.api.invoice.search_invoices_for_return',
        args: {
          invoice_name: this.invoice_name,
          company: this.company
        },
        callback: (r) => {
          this.isLoading = false;
          if (r.message && r.message.length > 0) {
            this.dialog_data = r.message.map(item => ({
              name: item.name,
              customer: item.customer,
              posting_date: item.posting_date,
              grand_total: item.grand_total,
              currency: item.currency,
              items: item.items || []
            }));
          } else {
            this.dialog_data = [];
          }
          
          // Display appropriate messages based on search results
          if (this.dialog_data.length === 0) {
            if (this.invoice_name) {
              evntBus.emit('show_mesage', {
                text: 'No invoices found matching search',
                color: 'info'
              });
            } else {
              evntBus.emit('show_mesage', {
                text: 'No invoices available for return in this company',
                color: 'info'
              });
            }
          }
        },
        error: (err) => {
          this.isLoading = false;
          evntBus.emit('show_mesage', {
            text: 'Failed to search for invoices',
            color: 'error'
          });
        }
      });
    },
    async submit_dialog() {
      if (!this.selected.length || !this.dialog_data.length) {
        evntBus.emit('show_mesage', {
          text: 'Please select a valid invoice',
          color: 'error'
        });
        return;
      }
      const selectedItem = this.dialog_data.find(item => item.name === this.selected[0]);
      if (!selectedItem) {
        evntBus.emit('show_mesage', {
          text: 'Selected invoice not found',
          color: 'error'
        });
        return;
      }
      const return_doc = selectedItem;
      // Fetch original invoice from server
      let original_invoice = null;
      try {
        const response = await frappe.call({
          method: 'frappe.client.get',
          args: {
            doctype: "Sales Invoice",
            name: return_doc.name
          }
        });
        original_invoice = response.message;
      } catch (e) {
        evntBus.emit('show_mesage', {
          text: 'Failed to fetch original invoice',
          color: 'error'
        });
        return;
      }
      if (!original_invoice) {
        evntBus.emit('show_mesage', {
          text: 'Original invoice not found',
          color: 'error'
        });
        return;
      }
      const original_items = original_invoice.items.map(i => i.item_code);
      const invalid_items = return_doc.items.filter(item => !original_items.includes(item.item_code));
      if (invalid_items.length > 0) {
        evntBus.emit('show_mesage', {
          text: `The following items are not in the original invoice: ${invalid_items.map(i => i.item_code).join(', ')}`,
          color: 'error'
        });
        return;
      }
      // Save complete objects in document
      const invoice_doc = {
        items: return_doc.items.map(item => ({
          ...item,
          qty: item.qty * -1,
          stock_qty: item.stock_qty * -1,
          amount: item.amount * -1
        })),
        is_return: 1,
        company: (this.pos_opening_shift && this.pos_opening_shift.company) || (this.pos_profile && this.pos_profile.company) || '',
        customer: return_doc.customer,
        posa_pos_opening_shift: this.pos_opening_shift?.name,
        pos_opening_shift: this.pos_opening_shift || null, // Save complete object
        pos_profile: this.pos_profile || null // Save complete object
      };
      evntBus.emit('load_return_invoice', { invoice_doc, return_doc });
      this.invoicesDialog = false;
    }
  },
  created() {
    evntBus.on('open_returns', (data) => {
      this.invoicesDialog = true;
      this.pos_profile = data.pos_profile || null;
      this.pos_opening_shift = data.pos_opening_shift || null;
      // Set company from pos_profile or pos_opening_shift
      this.company = (this.pos_profile && this.pos_profile.company) || (this.pos_opening_shift && this.pos_opening_shift.company) || '';
      this.dialog_data = [];
      this.selected = [];
      // Fetch initial invoices with proper filtering
      this.search_invoices();
    });
  }
};
</script>

<style scoped>
.v-data-table {
  font-size: 0.875rem;
}
</style>