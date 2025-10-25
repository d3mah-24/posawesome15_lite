<template>
  <div>
    <div class="autocomplete" :style="{ backgroundColor: quick_return ? '#EF9A9A' : 'white' }">
      <div class="autocomplete-input-wrapper">
        <input type="text" class="autocomplete-input" :placeholder="'Customer'" v-model="customer_search"
          :disabled="readonly" @focus="handleCustomerFocus" @input="performSearch" @keydown.enter="handleEnter"
          @keydown.down="navigateDown" @keydown.up="navigateUp" @keydown.esc="showDropdown = false" />

        <div class="autocomplete-icons">
          <button class="autocomplete-icon-btn" @click="edit_customer" :disabled="readonly" title="Edit Customer">
            <i class="mdi mdi-account-edit"></i>
          </button>
          <button class="autocomplete-icon-btn" @click="new_customer" :disabled="readonly" title="New Customer">
            <i class="mdi mdi-plus"></i>
          </button>
        </div>
      </div>

      <!-- Dropdown -->
      <div v-if="showDropdown && filteredCustomers.length > 0" class="autocomplete-dropdown" role="listbox">
        <div v-for="(item, index) in filteredCustomers" :key="item.name" class="autocomplete-item"
          :class="{ 'autocomplete-item--active': index === selectedIndex }" role="option"
          :aria-selected="index === selectedIndex" @click="selectCustomer(item)" @mouseenter="selectedIndex = index">
          <div class="autocomplete-item-title">
            {{ item.customer_name }}
          </div>
          <div v-if="item.mobile_no" class="autocomplete-item-subtitle">
            {{ item.mobile_no }}
          </div>
        </div>
      </div>

      <!-- Loading Indicator -->
      <div v-if="showDropdown && loading" class="autocomplete-loading">
        <div class="progress-linear">
          <div class="progress-bar"></div>
        </div>
      </div>
    </div>

    <div class="mb-2">
      <UpdateCustomer />
    </div>
  </div>
</template>

<script src="./Customer.js" />

<style scoped>
.autocomplete {
  position: relative;
  width: 100%;
}

.autocomplete-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.autocomplete-input {
  width: 100%;
  padding: 13px 40px 13px 12px;
  border: 1px solid var(--gray-300);
  border-radius: var(--radius-sm);
  font-size: 14px;
  background: white;
  transition: all 0.2s;
}

.autocomplete-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.1);
}

.autocomplete-input:disabled {
  background: var(--gray-100);
  color: var(--gray-500);
  cursor: not-allowed;
}

.autocomplete-icons {
  position: absolute;
  right: 4px;
  display: flex;
  gap: 4px;
}

.autocomplete-icon-btn {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: var(--gray-500);
  transition: color 0.15s;
}

.autocomplete-icon-btn:hover:not(:disabled) {
  color: var(--primary);
}

.autocomplete-icon-btn:disabled {
  color: var(--gray-300);
  cursor: not-allowed;
}

.autocomplete-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid var(--gray-300);
  border-top: none;
  border-radius: 0 0 var(--radius-sm) var(--radius-sm);
  box-shadow: var(--shadow-md);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.autocomplete-item {
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.15s;
  border-bottom: 1px solid var(--gray-200);
}

.autocomplete-item:hover,
.autocomplete-item--active {
  background: var(--gray-50);
}

.autocomplete-item:last-child {
  border-bottom: none;
}

.autocomplete-item-title {
  font-weight: 500;
  color: var(--primary);
  font-size: 14px;
}

.autocomplete-item-subtitle {
  font-size: 12px;
  color: var(--gray-600);
  margin-top: 2px;
}

.autocomplete-loading {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid var(--gray-300);
  border-top: none;
  border-radius: 0 0 var(--radius-sm) var(--radius-sm);
  padding: 8px;
}

.progress-linear {
  width: 100%;
  height: 4px;
  background: var(--gray-200);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: var(--primary);
  border-radius: 2px;
  animation: progressIndeterminate 1.5s infinite linear;
}

@keyframes progressIndeterminate {
  0% {
    transform: translateX(0) scaleX(0);
  }

  40% {
    transform: translateX(0) scaleX(0.4);
  }

  100% {
    transform: translateX(100%) scaleX(0.5);
  }
}
</style>
