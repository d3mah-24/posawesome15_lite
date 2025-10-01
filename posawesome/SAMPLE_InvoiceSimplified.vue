<template>
  <div class="invoice-container">
    <!-- Customer Section -->
    <v-card class="mb-2">
      <Customer />
    </v-card>

    <!-- Items Table -->
    <v-card class="items-section">
      <v-data-table
        :headers="headers"
        :items="items"
        :loading="loading"
        density="compact"
      >
        <!-- Quantity Column -->
        <template v-slot:item.qty="{ item }">
          <div class="qty-controls">
            <v-btn size="small" @click="updateQty(item, -1)">−</v-btn>
            <input 
              type="number" 
              v-model.number="item.qty"
              @change="updateQty(item, item.qty)"
            />
            <v-btn size="small" @click="updateQty(item, 1)">+</v-btn>
          </div>
        </template>

        <!-- Discount Column -->
        <template v-slot:item.discount_percentage="{ item }">
          <input
            type="number"
            v-model.number="item.discount_percentage"
            @change="applyDiscount(item)"
          />
        </template>

        <!-- Delete Column -->
        <template v-slot:item.actions="{ item }">
          <v-btn icon size="small" @click="removeItem(item)">
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- Totals Section -->
    <v-card class="totals-section">
      <v-row>
        <v-col cols="6">
          <v-text-field
            label="Total Quantity"
            :value="invoiceData.total_qty"
            readonly
          />
        </v-col>
        <v-col cols="6">
          <v-text-field
            label="Invoice Total"
            :value="formatCurrency(invoiceData.grand_total)"
            readonly
          />
        </v-col>
      </v-row>

      <!-- Action Buttons -->
      <v-row>
        <v-col cols="4">
          <v-btn block color="primary" @click="printInvoice">
            Print
          </v-btn>
        </v-col>
        <v-col cols="4">
          <v-btn block color="success" @click="showPayment">
            Pay
          </v-btn>
        </v-col>
        <v-col cols="4">
          <v-btn block color="error" @click="cancelInvoice">
            Cancel
          </v-btn>
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script>
import { evntBus } from "../../bus";
import format from "../../format";
import Customer from "./Customer.vue";

export default {
  mixins: [format],
  components: { Customer },
  
  data() {
    return {
      // UI State
      loading: false,
      
      // Core Data (from backend)
      invoiceData: {
        name: null,
        items: [],
        total_qty: 0,
        total: 0,
        discount_amount: 0,
        tax_amount: 0,
        grand_total: 0,
      },
      
      // Config
      pos_profile: null,
      pos_opening_shift: null,
      
      // Table headers
      headers: [
        { title: "Item Name", key: "item_name" },
        { title: "Qty", key: "qty", align: "center" },
        { title: "Price", key: "rate", align: "center" },
        { title: "Disc. %", key: "discount_percentage", align: "center" },
        { title: "Amount", key: "amount", align: "center" },
        { title: "Delete", key: "actions", align: "center" },
      ],
    };
  },

  computed: {
    items() {
      return this.invoiceData.items || [];
    },
  },

  methods: {
    /**
     * Add item to invoice - Backend handles all calculations
     */
    async addItem(item) {
      // Optimistic update
      this.invoiceData.items.push(item);
      
      try {
        const response = await frappe.call({
          method: "posawesome.posawesome.api.invoice.add_item_to_invoice",
          args: {
            invoice_name: this.invoiceData.name,
            item_code: item.item_code,
            qty: item.qty || 1,
          },
        });
        
        // Update with backend response
        this.invoiceData = response.message;
      } catch (error) {
        // Rollback optimistic update
        this.invoiceData.items.pop();
        evntBus.emit("show_mesage", {
          text: "Failed to add item",
          color: "error",
        });
      }
    },

    /**
     * Update quantity - Backend recalculates everything
     */
    async updateQty(item, delta) {
      const oldQty = item.qty;
      
      // Optimistic update
      if (typeof delta === 'number' && delta !== item.qty) {
        item.qty = Math.max(0, oldQty + delta);
      } else {
        item.qty = delta;
      }
      
      try {
        const response = await frappe.call({
          method: "posawesome.posawesome.api.invoice.update_item_quantity",
          args: {
            invoice_name: this.invoiceData.name,
            item_row_id: item.posa_row_id,
            new_qty: item.qty,
          },
        });
        
        // Update with backend response
        this.invoiceData = response.message;
      } catch (error) {
        // Rollback
        item.qty = oldQty;
        evntBus.emit("show_mesage", {
          text: "Failed to update quantity",
          color: "error",
        });
      }
    },

    /**
     * Remove item - Backend handles cleanup
     */
    async removeItem(item) {
      const index = this.invoiceData.items.indexOf(item);
      
      // Optimistic update
      this.invoiceData.items.splice(index, 1);
      
      try {
        const response = await frappe.call({
          method: "posawesome.posawesome.api.invoice.remove_item_from_invoice",
          args: {
            invoice_name: this.invoiceData.name,
            item_row_id: item.posa_row_id,
          },
        });
        
        // Update with backend response
        this.invoiceData = response.message;
      } catch (error) {
        // Rollback
        this.invoiceData.items.splice(index, 0, item);
        evntBus.emit("show_mesage", {
          text: "Failed to remove item",
          color: "error",
        });
      }
    },

    /**
     * Apply discount - Backend validates and calculates
     */
    async applyDiscount(item) {
      const oldDiscount = item.old_discount_percentage || 0;
      
      try {
        const response = await frappe.call({
          method: "posawesome.posawesome.api.invoice.apply_item_discount",
          args: {
            invoice_name: this.invoiceData.name,
            item_row_id: item.posa_row_id,
            discount_percentage: item.discount_percentage,
          },
        });
        
        // Update with backend response
        this.invoiceData = response.message;
      } catch (error) {
        // Rollback
        item.discount_percentage = oldDiscount;
        evntBus.emit("show_mesage", {
          text: error.message || "Failed to apply discount",
          color: "error",
        });
      }
    },

    /**
     * Show payment screen
     */
    async showPayment() {
      try {
        // Backend validates before allowing payment
        const response = await frappe.call({
          method: "posawesome.posawesome.api.invoice.validate_for_payment",
          args: {
            invoice_name: this.invoiceData.name,
          },
        });
        
        if (response.message.valid) {
          evntBus.emit("show_payment", "true");
        } else {
          evntBus.emit("show_mesage", {
            text: response.message.error,
            color: "error",
          });
        }
      } catch (error) {
        evntBus.emit("show_mesage", {
          text: "Cannot proceed to payment",
          color: "error",
        });
      }
    },

    /**
     * Cancel invoice
     */
    async cancelInvoice() {
      try {
        await frappe.call({
          method: "posawesome.posawesome.api.invoice.cancel_draft_invoice",
          args: {
            invoice_name: this.invoiceData.name,
          },
        });
        
        // Reset
        this.invoiceData = { items: [], grand_total: 0 };
        evntBus.emit("new_invoice", "false");
      } catch (error) {
        evntBus.emit("show_mesage", {
          text: "Failed to cancel invoice",
          color: "error",
        });
      }
    },

    /**
     * Print invoice
     */
    printInvoice() {
      if (!this.invoiceData.name) return;
      
      const url = `/printview?doctype=Sales%20Invoice&name=${this.invoiceData.name}`;
      window.open(url, 'Print').print();
    },
  },

  mounted() {
    // Listen for events
    evntBus.on("add_item", this.addItem);
    evntBus.on("update_customer", (customer) => {
      this.invoiceData.customer = customer;
    });
  },

  beforeDestroy() {
    // Cleanup
    evntBus.$off("add_item");
    evntBus.$off("update_customer");
  },
};
</script>

<style scoped>
.invoice-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.items-section {
  flex: 1;
  overflow: auto;
}

.totals-section {
  padding: 16px;
}

.qty-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.qty-controls input {
  width: 60px;
  text-align: center;
}
</style>

<!-- 
COMPARISON:
- Old Invoice.vue: ~3900 lines
- New Invoice.vue: ~300 lines
- Reduction: 92%!

All business logic moved to invoice.py backend
Frontend is now just a display layer
-->

