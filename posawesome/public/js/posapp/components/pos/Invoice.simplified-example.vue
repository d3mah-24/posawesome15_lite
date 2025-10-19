<template>
  <div class="invoice-wrapper">
    <!-- Customer Section -->
    <CustomerSection 
      v-model="customer"
      :pos-profile="pos_profile"
    />

    <!-- Items Table -->
    <ItemsTable
      v-model:items="items"
      :headers="tableHeaders"
      :readonly="readonly"
      @item-change="handleItemChange"
    />

    <!-- Financial Summary -->
    <FinancialSummary
      :summary="invoiceSummary"
      :currency="pos_profile?.currency"
      v-model:additional-discount="additional_discount_percentage"
    />

    <!-- Action Buttons -->
    <ActionButtons
      :can-pay="canPay"
      :can-print="canPrint"
      @pay="handlePay"
      @print="handlePrint"
      @return="handleReturn"
      @cancel="handleCancel"
    />
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue';
import { useInvoice } from '@/composables/useInvoice';
import { useInvoiceEvents } from '@/composables/useInvoiceEvents';
import CustomerSection from './CustomerSection.vue';
import ItemsTable from './ItemsTable.vue';
import FinancialSummary from './FinancialSummary.vue';
import ActionButtons from './ActionButtons.vue';

export default {
  name: "Invoice",
  components: { CustomerSection, ItemsTable, FinancialSummary, ActionButtons },
  
  props: {
    is_payment: Boolean,
  },

  setup() {
    // ═══════════════════════════════════════════
    // Composables (Business Logic)
    // ═══════════════════════════════════════════
    const {
      // State
      items,
      invoice_doc,
      customer,
      pos_profile,
      additional_discount_percentage,
      
      // Actions
      addItem,
      removeItem,
      updateItemQty,
      updateItemPricing,
      syncInvoice,
      resetInvoice,
      
      // Payment
      showPayment,
      printInvoice,
      
      // Computed
      invoiceSummary,
      canPay,
      canPrint,
      readonly,
    } = useInvoice();
    
    // Events
    useInvoiceEvents({ addItem, customer, resetInvoice });
    
    // ═══════════════════════════════════════════
    // Local Logic (UI-specific)
    // ═══════════════════════════════════════════
    
    const tableHeaders = computed(() => {
      const base = [
        { title: "Item", key: "item_name", width: "25%" },
        { title: "Qty", key: "qty", width: "10%" },
        { title: "UOM", key: "uom", width: "8%" },
        { title: "Price", key: "price_list_rate", width: "12%" },
        { title: "Rate", key: "rate", width: "12%" },
        { title: "Total", key: "amount", width: "15%" },
        { title: "", key: "actions", width: "8%" },
      ];
      
      // Show discount columns based on settings
      if (pos_profile.value?.posa_display_discount_percentage) {
        base.splice(5, 0, { 
          title: "Disc %", 
          key: "discount_percentage", 
          width: "10%" 
        });
      }
      
      return base;
    });
    
    // Debounced sync
    let syncTimer = null;
    const handleItemChange = () => {
      clearTimeout(syncTimer);
      syncTimer = setTimeout(() => {
        syncInvoice();
      }, 1000);
    };
    
    // Action handlers
    const handlePay = async () => {
      await showPayment();
    };
    
    const handlePrint = async () => {
      await printInvoice();
    };
    
    const handleReturn = () => {
      evntBus.emit('open_returns', {
        pos_profile: pos_profile.value,
      });
    };
    
    const handleCancel = () => {
      if (confirm('Cancel invoice?')) {
        resetInvoice();
      }
    };
    
    return {
      // State
      items,
      customer,
      pos_profile,
      additional_discount_percentage,
      
      // Computed
      invoiceSummary,
      tableHeaders,
      canPay,
      canPrint,
      readonly,
      
      // Actions
      handleItemChange,
      handlePay,
      handlePrint,
      handleReturn,
      handleCancel,
    };
  }
};
</script>

<style src="./Invoice.css" scoped></style>
