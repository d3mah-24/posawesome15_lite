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
          <div class="card-body" style="max-height: 60vh; overflow-y: auto; display: flex; flex-direction: column;">
            <div class="search-row">
              <div class="text-field-wrapper">
                <input type="text" class="custom-text-field" v-model="invoice_name" placeholder="Invoice Number"
                  @keydown.enter="search_invoices" />
              </div>
              <button class="btn btn-primary btn-search" @click="search_invoices">
                Search
              </button>
            </div>
            <div class="table-row" style="flex: 1; min-height: 0;">
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
                            Select
                          </th>
                          <th v-for="header in headers" :key="header.key" :class="header.align">
                            {{ header.title }}
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="item in dialog_data" :key="item.name" class="table-row-item">
                          <td class="select-cell">
                            <input type="radio" :value="item.name" v-model="selected" name="invoice" />
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
          <div class="card-footer" style="flex-shrink: 0; margin-top: auto;">
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

<script src="./Returns.js" />

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
  padding: 12px;
  border-bottom: 1px solid #e0e0e0;
  background: #f5f5f5;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1976d2;
}

.card-body {
  padding: 12px;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid #e0e0e0;
  margin-top: 12px;
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
  margin-bottom: 12px;
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
  font-size: 0.8rem;
}

.data-table thead {
  background: #f5f5f5;
}

.data-table th,
.data-table td {
  padding: 8px 12px;
  border-bottom: 1px solid #e0e0e0;
  white-space: nowrap;
}

.data-table th {
  font-weight: 600;
  color: #333;
  text-align: left;
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
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
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
  margin: 0 8px;
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
  max-width: 775px;
  min-width: 750px;
  max-height: 90vh;
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

/* Add this small block */
.custom-modal.small-modal .card {
  display: flex;
  flex-direction: column;
  height: 100%;
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
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
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
