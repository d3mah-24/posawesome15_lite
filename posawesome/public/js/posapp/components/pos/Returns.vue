<template>
  <!-- ===== TEMPLATE SECTION 1: MAIN CONTAINER ===== -->
  <div class="dialog-row">
    <v-dialog v-model="invoicesDialog" max-width="800px" min-width="800px">
      <div class="card">
        <div class="card-header">
          <span class="card-title">Return Invoice</span>
        </div>
        <div class="card-body">
          <div class="search-row">
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
            <button class="btn btn-primary btn-search" @click="search_invoices">
              Search
            </button>
          </div>
          <div class="table-row">
            <div class="table-col-full">
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
            </div>
          </div>
        </div>
        <div class="card-footer">
          <div class="spacer"></div>
          <button class="btn btn-error" @click="close_dialog">Close</button>
          <button class="btn btn-success" @click="submit_dialog">
            Select
          </button>
        </div>
      </div>
    </v-dialog>
  </div>
</template>

<script>
// ===== SECTION 1: IMPORTS =====
import { evntBus } from '../../bus';
import format from '../../format';
import { API_MAP } from "../../api_mapper.js";

const EVENT_NAMES = {
  OPEN_RETURNS: 'open_returns',
  LOAD_RETURN_INVOICE: 'load_return_invoice',
  SHOW_MESSAGE: 'show_mesage'
};

const TABLE_HEADERS = [
  { title: 'Customer', key: 'customer', align: 'start', sortable: true },
  { title: 'Date', key: 'posting_date', align: 'start', sortable: true },
  { title: 'Invoice Number', key: 'name', align: 'start', sortable: true },
  { title: 'Amount', key: 'grand_total', align: 'end', sortable: false }
];

const DEFAULT_COMPANY = 'Khaleej Women';

// ===== SECTION 2: EXPORT DEFAULT =====
export default {
  mixins: [format],

  // ===== DATA =====
  data() {
    return {
      invoicesDialog: false,
      selected: [],
      dialog_data: [],
      isLoading: false,
      company: '',
      invoice_name: '',
      pos_profile: null,
      pos_opening_shift: null,
      headers: TABLE_HEADERS
    };
  },
  // ===== LIFECYCLE HOOKS =====
  beforeUnmount() {
    evntBus.off(EVENT_NAMES.OPEN_RETURNS);
  },

  created() {
    evntBus.on(EVENT_NAMES.OPEN_RETURNS, (data) => {
      this.invoicesDialog = true;
      this.pos_profile = data.pos_profile || null;
      this.pos_opening_shift = data.pos_opening_shift || null;
      this.company = this.getCompany();
      this.dialog_data = [];
      this.selected = [];
      this.search_invoices();
    });
  },

  // ===== METHODS =====
  methods: {
    showMessage(text, color) {
      evntBus.emit(EVENT_NAMES.SHOW_MESSAGE, { text, color });
    },

    getCompany() {
      return this.pos_profile?.company || this.pos_opening_shift?.company || this.company || DEFAULT_COMPANY;
    },

      // Close the returns dialog and reset state
    close_dialog() {
      this.$nextTick(() => {
        this.invoicesDialog = false;
        this.selected = [];
        this.dialog_data = [];
        this.invoice_name = '';
      });
    },

      // Search for invoices available for return
    search_invoices() {
      this.company = this.getCompany();
      
      console.log("Searching invoices with:", {
        invoice_name: this.invoice_name,
        company: this.company
      });
      
      this.isLoading = true;

      frappe.call({
        method: API_MAP.SALES_INVOICE.GET_INVOICES_FOR_RETURN,
        args: {
          invoice_name: this.invoice_name || '',
          company: this.company
        },
        callback: (r) => {
          this.isLoading = false;
          console.log("API Response:", r.message);
          
          this.dialog_data = r.message?.length > 0 
            ? r.message.map(item => ({
                name: item.name,
                customer: item.customer,
                posting_date: item.posting_date,
                grand_total: item.grand_total,
                currency: item.currency,
                items: item.items || []
              }))
            : [];
          
          this.displaySearchResultsMessage();
        },
        error: () => {
          this.isLoading = false;
          this.showMessage('Failed to search for invoices', 'error');
        }
      });
    },

    // Display appropriate message based on search results
    displaySearchResultsMessage() {
      if (this.dialog_data.length === 0) {
        const message = this.invoice_name
          ? 'No invoices found matching search'
          : `No submitted invoices available for return in company: ${this.company}`;
        this.showMessage(message, 'info');
      } else {
        this.showMessage(`Found ${this.dialog_data.length} invoices available for return`, 'success');
      }
    },

    async fetchOriginalInvoice(invoice_name) {
      try {
        const response = await frappe.call({
          method: API_MAP.FRAPPE.CLIENT_GET,
          args: {
            doctype: "Sales Invoice",
            name: invoice_name
          }
        });
        return response.message;
      } catch (e) {
        this.showMessage('Failed to fetch original invoice', 'error');
        return null;
      }
    },

    validateReturnItems(return_items, original_invoice) {
      const original_items = original_invoice.items.map(i => i.item_code);
      const invalid_items = return_items.filter(item => !original_items.includes(item.item_code));
      
      if (invalid_items.length > 0) {
        this.showMessage(
          `The following items are not in the original invoice: ${invalid_items.map(i => i.item_code).join(', ')}`,
          'error'
        );
        return false;
      }
      return true;
    },

    createReturnInvoiceDoc(return_doc) {
      return {
        items: return_doc.items.map(item => ({
          ...item,
          qty: Math.abs(item.qty) * -1,
          stock_qty: Math.abs(item.stock_qty || item.qty) * -1,
          amount: Math.abs(item.amount) * -1,
          posa_row_id: Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
          posa_offers: "[]",
          posa_offer_applied: 0,
          posa_is_offer: 0,
          posa_is_replace: 0,
          is_free_item: 0,
          sales_invoice_item: item.name,
          name: null
        })),
        is_return: 1,
        return_against: return_doc.name,
        company: this.getCompany(),
        customer: return_doc.customer,
        posa_pos_opening_shift: this.pos_opening_shift?.name,
        pos_opening_shift: this.pos_opening_shift || null,
        pos_profile: this.pos_profile || null
      };
    },

    // Submit selected invoice for return
    async submit_dialog() {
      if (!this.selected.length || !this.dialog_data.length) {
        this.showMessage('Please select a valid invoice', 'error');
        return;
      }

      const selectedItem = this.dialog_data.find(item => item.name === this.selected[0]);
      if (!selectedItem) {
        this.showMessage('Selected invoice not found', 'error');
        return;
      }

      const return_doc = selectedItem;
      const original_invoice = await this.fetchOriginalInvoice(return_doc.name);
      
      if (!original_invoice) {
        this.showMessage('Original invoice not found', 'error');
        return;
      }

      if (!this.validateReturnItems(return_doc.items, original_invoice)) {
        return;
      }

      const invoice_doc = this.createReturnInvoiceDoc(return_doc);
      
      console.log("Returns.vue emitting load_return_invoice with data:", {
        invoice_doc_customer: invoice_doc.customer,
        return_doc_customer: return_doc.customer,
        invoice_doc,
        return_doc
      });
      
      evntBus.emit(EVENT_NAMES.LOAD_RETURN_INVOICE, { invoice_doc, return_doc });
      this.invoicesDialog = false;
    }
  },

  beforeDestroy() {
    // Clean up event listener
    evntBus.$off(EVENT_NAMES.OPEN_RETURNS);
  }
};
</script>

<style scoped>
/* Dialog Row Container */
.dialog-row {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Card Components */
.card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
  background: #f5f5f5;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1976d2;
}

.card-body {
  padding: 16px;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding: 16px;
  border-top: 1px solid #e0e0e0;
  margin-top: 16px;
}

/* Spacer */
.spacer {
  flex: 1;
}

/* Button Styles */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid;
  transition: all 0.2s;
  line-height: 1.5;
  margin: 0 4px;
}

.btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn:active {
  transform: translateY(0);
}

.btn-primary {
  background: linear-gradient(135deg, #1976d2 0%, #1e88e5 100%);
  border-color: #1565c0;
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #1565c0 0%, #1976d2 100%);
}

.btn-error {
  background: linear-gradient(135deg, #f44336 0%, #e53935 100%);
  border-color: #d32f2f;
  color: white;
}

.btn-error:hover {
  background: linear-gradient(135deg, #d32f2f 0%, #c62828 100%);
}

.btn-success {
  background: linear-gradient(135deg, #4caf50 0%, #43a047 100%);
  border-color: #388e3c;
  color: white;
}

.btn-success:hover {
  background: linear-gradient(135deg, #388e3c 0%, #2e7d32 100%);
}

.btn-search {
  margin-left: 8px;
}

/* Search Row */
.search-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

/* Table Row */
.table-row {
  display: flex;
  width: 100%;
}

.table-col-full {
  flex: 1;
  padding: 4px;
}

.v-data-table {
  font-size: 0.875rem;
}
</style>