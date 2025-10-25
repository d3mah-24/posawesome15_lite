<template>
  <div class="dialog-row">
    <div v-if="addressDialog" class="custom-modal-overlay" @click="addressDialog = false">
      <div class="custom-modal" @click.stop>
        <div class="card compact-dialog">
          <div class="card-header">
            <span class="card-title">Add New Address</span>
            <button class="modal-close-btn" @click="addressDialog = false">×</button>
          </div>
          <div class="card-body">
            <div class="form-container">
              <div class="form-row">
                <div class="form-col form-col-12">
                  <div class="text-field-wrapper">
                    <label class="text-field-label">Address Title</label>
                    <input type="text" class="custom-text-field compact" v-model="address.name"
                      placeholder="Enter address title" />
                  </div>
                </div>
                <div class="form-col form-col-12">
                  <div class="text-field-wrapper">
                    <label class="text-field-label">Address Line 1</label>
                    <input type="text" class="custom-text-field compact" v-model="address.address_line1"
                      placeholder="Enter address line 1" />
                  </div>
                </div>
                <div class="form-col form-col-12">
                  <div class="text-field-wrapper">
                    <label class="text-field-label">Address Line 2</label>
                    <input type="text" class="custom-text-field compact" v-model="address.address_line2"
                      placeholder="Enter address line 2" />
                  </div>
                </div>
                <div class="form-col form-col-6">
                  <div class="text-field-wrapper">
                    <label class="text-field-label">City</label>
                    <input type="text" class="custom-text-field compact" v-model="address.city"
                      placeholder="Enter city" />
                  </div>
                </div>
                <div class="form-col form-col-6">
                  <div class="text-field-wrapper">
                    <label class="text-field-label">State</label>
                    <input type="text" class="custom-text-field compact" v-model="address.state"
                      placeholder="Enter state" />
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="card-footer">
            <div class="spacer"></div>
            <button class="btn btn-outlined btn-cancel compact-btn" @click="close_dialog">
              Cancel
            </button>
            <button class="btn btn-primary compact-btn" @click="submit_dialog">
              Confirm
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script src="./NewAddress.js" />

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
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
  background: #f5f5f5;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1976d2;
}

.card-body {
  padding: 8px;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px 0;
  border-top: 1px solid #e0e0e0;
}

/* Spacer */
.spacer {
  flex: 1;
}

/* Form Container */
.form-container {
  padding: 8px;
}

/* Form Row */
.form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: -4px;
}

/* Form Columns */
.form-col {
  padding: 4px;
}

.form-col-12 {
  flex: 0 0 100%;
  max-width: 100%;
}

.form-col-6 {
  flex: 0 0 calc(50% - 4px);
  max-width: calc(50% - 4px);
}

.compact-dialog {
  border-radius: 12px !important;
}

.compact-dialog .v-card__title {
  border-bottom: 1px solid #e0e0e0;
}

.compact-field {
  margin-bottom: 4px !important;
}

.compact-field .v-input__control {
  min-height: 40px !important;
}

.compact-field .v-text-field__details {
  margin-top: 2px !important;
  padding-top: 0 !important;
}

.compact-btn {
  text-transform: none !important;
  font-weight: 500 !important;
  letter-spacing: 0.5px !important;
  min-width: 80px !important;
  height: 36px !important;
}

.v-input--dense .v-input__control {
  min-height: 40px !important;
}

.v-text-field--outlined.v-input--dense .v-input__control {
  min-height: 40px !important;
}

.v-text-field--outlined .v-input__control {
  min-height: 40px !important;
}

/* Custom styling for better visual hierarchy */
.v-card__title .text-h6 {
  font-size: 1.1rem !important;
  line-height: 1.3 !important;
}

/* Reduce spacing in rows */
.row.dense {
  margin: -2px !important;
}

.row.dense>.col {
  padding: 2px !important;
}

/* Better button styling */
/* Button Styles */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 16px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid;
  transition: all 0.2s ease;
  line-height: 1.5;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.btn:active {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  background: linear-gradient(135deg, #1976d2 0%, #1e88e5 100%);
  border-color: #1565c0;
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #1565c0 0%, #1976d2 100%);
}

.btn-outlined {
  background: white;
  border-color: #9e9e9e;
  color: #616161;
}

.btn-outlined:hover {
  background: #f5f5f5;
  border-color: #757575;
}

.btn-cancel {
  margin-right: 8px;
}

.compact-btn {
  padding: 4px 12px;
  height: 26px;
  font-size: 11px;
}

/* Outlined text fields styling */
.v-text-field--outlined>.v-input__control>.v-input__slot {
  border-radius: 6px !important;
}

.v-select--outlined>.v-input__control>.v-input__slot {
  border-radius: 6px !important;
}

/* ===== CUSTOM TEXT FIELD ===== */
.text-field-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
}

.text-field-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #555;
  margin-bottom: 2px;
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

/* Compact variant */
.custom-text-field.compact {
  padding: 6px 10px;
  font-size: 0.8rem;
  min-height: 36px;
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
  max-width: 480px;
  width: 90%;
  max-height: 90vh;
  overflow: hidden;
  animation: modal-slide-in 0.3s ease;
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
@media (max-width: 600px) {
  .custom-modal {
    width: 95%;
    margin: 20px;
  }
}
</style>
