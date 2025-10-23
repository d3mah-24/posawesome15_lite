<template>
  <!-- ===== TEMPLATE SECTION 1: MAIN CONTAINER ===== -->
  <div class="dialog-row">
    <div v-if="invoicesDialog" class="custom-modal-overlay" @click="invoicesDialog = false">
      <div class="custom-modal small-modal" @click.stop>
        <div class="card">
          <div class="card-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <span class="card-title" style="color: white; display: flex; align-items: center; gap: 8px;">
              <i class="mdi mdi-keyboard-return" style="font-size: 18px;"></i>
              Return Invoice
            </span>
            <button class="modal-close-btn" @click="invoicesDialog = false" style="color: white;">×</button>
          </div>
          <div class="card-body">
          <div class="search-row">
            <div class="text-field-wrapper">
              <input
                type="text"
                class="custom-text-field"
                v-model="invoice_name"
                placeholder="Invoice Number"
                @keydown.enter="search_invoices"
              />
            </div>
            <button class="btn btn-primary btn-search" @click="search_invoices">
              Search
            </button>
          </div>
          <div class="table-row">
          <div class="table-col-full" style="max-height: 60vh; overflow-y: auto;">
              <div class="custom-data-table">
                <!-- Loading State -->
                <div v-if="isLoading" class="table-loading">
                  <div class="loading-spinner"></div>
                  <span>Loading invoices...</span>
                </div>
                
                <!-- Table Content -->
                <div v-else>
                  <!-- No Data State -->
                  <div v-if="dialog_data.length === 0" class="no-data">
                    No invoices found
                  </div>
                  
                  <!-- Table -->
                  <table v-else class="data-table">
                    <thead>
                      <tr>
                        <th class="select-header">
                          <input 
                            type="checkbox" 
                            :checked="selected.length === dialog_data.length && dialog_data.length > 0"
                            @change="toggleSelectAll"
                          />
                        </th>
                        <th v-for="header in headers" :key="header.key" :class="header.align">
                          {{ header.title }}
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="item in dialog_data" :key="item.name" class="table-row-item">
                        <td class="select-cell">
                          <input 
                            type="checkbox" 
                            :value="item.name"
                            v-model="selected"
                          />
                        </td>
                        <td class="text-start">{{ item.customer }}</td>
                        <td class="text-start">{{ item.posting_date }}</td>
                        <td class="text-start">{{ item.name }}</td>
                        <td class="text-end">
                          {{ currencySymbol(item.currency) }} {{ formatCurrency(item.grand_total) }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
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
      </div>
    </div>
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

    toggleSelectAll(event) {
      if (event.target.checked) {
        this.selected = this.dialog_data.map(item => item.name);
      } else {
        this.selected = [];
      }
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
      
      this.isLoading = true;

      frappe.call({
        method: API_MAP.SALES_INVOICE.GET_INVOICES_FOR_RETURN,
        args: {
          invoice_name: this.invoice_name || '',
          company: this.company
        },
        callback: (r) => {
          this.isLoading = false;
          
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

/* ===== CUSTOM DATA TABLE ===== */
.custom-data-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.data-table thead {
  background: #f5f5f5;
}

.data-table th,
.data-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
}

.data-table th {
  font-weight: 600;
  color: #333;
  text-align: left;
  white-space: nowrap;
}

.data-table td {
  color: #666;
}

.data-table tbody tr:hover {
  background: #f9f9f9;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

/* Table alignment classes */
.text-start {
  text-align: left;
}

.text-end {
  text-align: right;
}

.text-center {
  text-align: center;
}

/* Select column styles */
.select-header,
.select-cell {
  width: 40px;
  text-align: center;
  padding: 8px;
}

.select-cell input[type="checkbox"],
.select-header input[type="checkbox"] {
  cursor: pointer;
  transform: scale(1.1);
}

/* Loading state */
.table-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #666;
  gap: 16px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e0e0e0;
  border-top: 3px solid #1976d2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* No data state */
.no-data {
  text-align: center;
  padding: 40px;
  color: #999;
  font-style: italic;
}

/* Responsive table */
@media (max-width: 768px) {
  .data-table {
    font-size: 0.75rem;
  }
  
  .data-table th,
  .data-table td {
    padding: 8px 12px;
  }
}

/* ===== CUSTOM TEXT FIELD ===== */
.text-field-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin: 0 16px;
}

.custom-text-field {
  width: 100%;
  padding: 8px 12px;
  font-size: 0.85rem;
  color: #333;
  background: white;
  border: 1px solid #d0d0d0;
  border-radius: 6px;
  outline: none;
  transition: all 0.2s ease;
}

.custom-text-field:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.custom-text-field:hover:not(:disabled):not(:focus) {
  border-color: #999;
}

.custom-text-field::placeholder {
  color: #999;
  font-size: 0.8rem;
}

/* ===== CUSTOM MODAL ===== */
.custom-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: modal-fade-in 0.2s ease;
}

.custom-modal {
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow: hidden;
  animation: modal-slide-in 0.3s ease;
}

/* .custom-modal.large-modal {
  max-width: 800px;
  min-width: 600px;
} */

.custom-modal.small-modal {
  max-width: 575px;
  min-width: 550px;
  max-height: 80vh;
}

.modal-close-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #999;
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.modal-close-btn:hover {
  background: #f5f5f5;
  color: #333;
}

@keyframes modal-fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes modal-slide-in {
  from {
    transform: translateY(-20px) scale(0.95);
    opacity: 0;
  }
  to {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

/* Responsive modal */
@media (max-width: 900px) {
  .custom-modal.small-modal {
    width: 95%;
    min-width: auto;
    margin: 20px;
  }
}

.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  position: relative;
}

.card-header::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  transform: rotate(45deg);
  pointer-events: none;
}

.card-title {
  color: white !important;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-close-btn {
  color: white !important;
}


</style>