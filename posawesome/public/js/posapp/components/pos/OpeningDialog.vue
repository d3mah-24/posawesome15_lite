<template>
  <div class="dialog-row">
    <div v-if="isOpen" class="custom-modal-overlay persistent" @click="go_desk">
      <!-- Custom Beautiful Dialog -->
      <div class="beautiful-dialog" @click.stop>
        <!-- Compact Header -->
        <div class="dialog-header">
          <div class="header-content">
            <div class="header-icon">
              <i class="mdi mdi-cash-register cash-icon"></i>
            </div>
            <div class="header-text">
              <h3 class="dialog-title">POS Opening</h3>
            </div>
          </div>
          <button class="close-btn" @click="go_desk">
            <i class="mdi mdi-close close-icon"></i>
          </button>
        </div>

        <!-- Compact Content -->
        <div class="dialog-content">
          <!-- Company Selection -->
          <div class="form-section">
            <label class="field-label">Company</label>
            <select v-model="company" class="custom-select" required>
              <option v-for="comp in companies" :key="comp" :value="comp">{{ comp }}</option>
            </select>
          </div>

          <!-- POS Profile Selection -->
          <div class="form-section">
            <label class="field-label">POS Profile</label>
            <select v-model="pos_profile" class="custom-select" required>
              <option v-for="profile in pos_profiles" :key="profile" :value="profile">{{ profile }}</option>
            </select>
          </div>

          <!-- Payment Methods Table -->
          <div class="form-section">
            <label class="field-label">Payment Methods</label>
            <div class="payment-table">
              <div class="table-header">
                <div class="header-cell method-col">Payment Method</div>
                <div class="header-cell amount-col">Opening Amount</div>
              </div>

              <div class="table-body">
                <div v-for="(item, index) in payments_methods" :key="item.mode_of_payment" class="table-row">
                  <div class="table-cell method-col">
                    <div class="payment-method">
                      <i class="mdi payment-icon" :class="getPaymentIcon(item.mode_of_payment).icon"
                        :style="{ color: getPaymentIcon(item.mode_of_payment).color }"></i>
                      <span class="method-name">{{ item.mode_of_payment }}</span>
                    </div>
                  </div>

                  <div class="table-cell amount-col">
                    <div class="amount-input-wrapper">
                      <span class="currency">{{ currencySymbol(item.currency) }}</span>
                      <input v-model="item.amount" type="number" class="amount-input" placeholder="0.00" step="0.01"
                        min="0" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Compact Footer -->
        <div class="dialog-footer">
          <button class="action-btn cancel-btn" @click="go_desk">
            <i class="mdi mdi-close cancel-icon"></i>
            Cancel
          </button>
          <button v-if="isOpeningAllowed" class="action-btn submit-btn" @click="submit_dialog" :disabled="is_loading"
            :class="{ 'loading': is_loading }">
            <i class="mdi mdi-check submit-icon" v-if="!is_loading"></i>
            <i class="mdi mdi-loading rotating loading-icon" v-else></i>
            {{ is_loading ? 'Creating...' : 'Confirm' }}
          </button>
          <div v-else class="time-restriction-message">
            {{ openingTimeMessage }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script src="./OpeningDialog.js" />

<style scoped>
/* ===== CENTRALIZED POS STYLING ===== */
/* This file contains all POS opening dialog styling */
/* ERP forms use default Frappe styling */
/* Reports use simple HTML without custom CSS */

/* Dialog Row Container */
.dialog-row {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Enhanced Beautiful Dialog with Centralized POS Styling */
.beautiful-dialog {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  max-width: 450px;
  width: 100%;
  animation: dialogSlideIn 0.3s ease-out;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

@keyframes dialogSlideIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }

  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Enhanced Header with Centralized POS Styling */
.dialog-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
}

.dialog-header::before {
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

.header-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  width: 28px;
  height: 28px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cash-icon {
  color: white;
  font-size: 18px;
}

.close-icon {
  color: white;
  font-size: 14px;
}

.dialog-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 2;
}

.close-btn {
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 4px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.25);
}

/* Compact Content */
.dialog-content {
  padding: 12px;
  background: #fafbfc;
}

/* Form Sections */
.form-section {
  margin-bottom: 12px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.field-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Custom Select */
.custom-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  background: white;
  color: #374151;
  outline: none;
  transition: all 0.2s ease;
}

.custom-select:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

/* Compact Table */
.payment-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e8eaed;
  margin-top: 6px;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.header-cell {
  padding: 6px 8px;
  font-size: 10px;
  font-weight: 600;
  color: #475569;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.header-cell.amount-col {
  justify-content: flex-end;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 0.1s ease;
}

.table-row:hover {
  background: #f8fafc;
}

.table-row:last-child {
  border-bottom: none;
}

.table-cell {
  padding: 8px;
  display: flex;
  align-items: center;
  font-size: 12px;
  min-height: 36px;
}

.table-cell.method-col {
  justify-content: flex-start;
}

.table-cell.amount-col {
  justify-content: flex-end;
}

/* Payment Method Styling */
.payment-method {
  display: flex;
  align-items: center;
  gap: 6px;
}

.method-name {
  font-weight: 500;
  color: #334155;
  font-size: 11px;
}

.payment-icon {
  font-size: 14px;
}

/* Amount Input Styling */
.amount-input-wrapper {
  display: flex;
  align-items: center;
  gap: 4px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 2px 6px;
  transition: all 0.2s ease;
}

.amount-input-wrapper:focus-within {
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.currency {
  font-size: 10px;
  color: #64748b;
  font-weight: 500;
}

.amount-input {
  border: none;
  outline: none;
  font-size: 11px;
  font-weight: 600;
  font-family: monospace;
  width: 60px;
  text-align: right;
  background: transparent;
  color: #1e293b;
}

.amount-input::placeholder {
  color: #9ca3af;
}

/* Compact Footer */
.dialog-footer {
  background: #f8fafc;
  padding: 8px 12px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.cancel-btn {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #cbd5e1;
}

.cancel-btn:hover:not(:disabled) {
  background: #e2e8f0;
}

.submit-btn {
  background: #10b981;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-1px);
}

.submit-btn.loading {
  background: #6b7280;
}

.cancel-icon,
.submit-icon,
.loading-icon {
  font-size: 14px;
}

/* Time Restriction Message */
.time-restriction-message {
  font-size: 11px;
  color: #dc2626;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  padding: 6px 10px;
  display: flex;
  align-items: center;
  font-weight: 500;
}

/* Loading Animation */
@keyframes rotate {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

.rotating {
  animation: rotate 1s linear infinite;
}

/* Mobile Responsive */
@media (max-width: 600px) {
  .beautiful-dialog {
    margin: 8px;
    max-width: calc(100vw - 16px);
  }

  .dialog-header {
    padding: 8px 10px;
  }

  .dialog-title {
    font-size: 13px;
  }

  .dialog-content {
    padding: 10px;
  }

  .form-section {
    margin-bottom: 10px;
  }

  .table-header,
  .table-row {
    font-size: 10px;
  }

  .header-cell,
  .table-cell {
    padding: 6px;
  }

  .action-btn {
    padding: 5px 10px;
    font-size: 11px;
  }

  .amount-input {
    width: 50px;
  }
}

/* Enhanced Focus States */
.custom-select:focus,
.amount-input:focus {
  outline: none;
}

/* Improved Visual Hierarchy */
.payment-table {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.table-header {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

/* ===== CUSTOM MODAL ===== */
.custom-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: modal-fade-in 0.2s ease;
}

.custom-modal-overlay.persistent {
  background: rgba(0, 0, 0, 0.7);
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
</style>
