<template>
  <div class="coupons-wrapper">
    <!-- HEADER WITH STATS AND ADD COUPON -->
    <div class="coupons-header">
      <div class="header-content">
        <div class="header-left">
          <v-icon color="white" size="22">mdi-ticket-percent</v-icon>
          <h2 class="header-title">Coupons</h2>
        </div>
        <div class="header-stats">
          <div class="stat-badge">
            <span class="stat-label">Total</span>
            <span class="stat-value">{{ couponsCount }}</span>
          </div>
          <div class="stat-badge active">
            <span class="stat-label">Active</span>
            <span class="stat-value">{{ appliedCouponsCount }}</span>
          </div>
        </div>
      </div>

      <!-- ADD COUPON INPUT -->
      <div class="add-coupon-section">
        <div class="coupon-input-wrapper">
          <v-icon size="18" class="input-icon">mdi-ticket</v-icon>
          <input
            v-model="new_coupon"
            @keyup.enter="add_coupon(new_coupon)"
            placeholder="Enter coupon code..."
            class="coupon-input"
            type="text"
          />
        </div>
        <button class="add-button" @click="add_coupon(new_coupon)">
          <v-icon size="18">mdi-plus</v-icon>
          <span>Add</span>
        </button>
      </div>
    </div>

    <!-- COUPONS GRID -->
    <div class="coupons-grid">
      <div
        v-for="(coupon, idx) in posa_coupons"
        :key="idx"
        class="coupon-card-wrapper"
      >
        <div class="coupon-card" :class="{ 'coupon-active': coupon.applied }">
          <!-- COUPON ICON/TYPE BADGE -->
          <div class="coupon-icon-container">
            <div class="coupon-icon" :class="getCouponTypeClass(coupon.type)">
              <v-icon size="28" color="white">{{
                getCouponIcon(coupon.type)
              }}</v-icon>
            </div>
            <div v-if="coupon.applied" class="applied-badge">
              <v-icon size="14">mdi-check-circle</v-icon>
              <span>Active</span>
            </div>
          </div>

          <!-- COUPON CONTENT -->
          <div class="coupon-content">
            <!-- COUPON CODE -->
            <div class="coupon-code">
              {{ truncateText(coupon.coupon_code, 12) }}
            </div>

            <!-- COUPON TYPE -->
            <div class="coupon-type">
              <v-icon size="12">mdi-tag</v-icon>
              <span>{{ coupon.type }}</span>
            </div>

            <!-- POS OFFER NAME -->
            <div class="coupon-offer" v-if="coupon.pos_offer">
              <v-icon size="12">mdi-gift</v-icon>
              <span>{{ truncateText(coupon.pos_offer, 15) }}</span>
            </div>

            <!-- STATUS TOGGLE -->
            <div class="coupon-status">
              <label class="status-toggle">
                <input type="checkbox" :checked="coupon.applied" disabled />
                <span class="toggle-slider"></span>
              </label>
              <span class="status-text" :class="{ active: coupon.applied }">
                {{ coupon.applied ? "Applied" : "Not Applied" }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- EMPTY STATE -->
      <div v-if="posa_coupons.length === 0" class="empty-state">
        <v-icon size="64" color="#ccc">mdi-ticket-outline</v-icon>
        <p class="empty-text">No coupons added yet</p>
        <p class="empty-subtext">Enter a coupon code above to get started</p>
      </div>
    </div>

    <!-- FOOTER -->
    <div class="coupons-footer">
      <button class="back-button" @click="back_to_invoice">
        <v-icon size="18">mdi-arrow-left</v-icon>
        <span>Back to Invoice</span>
      </button>
    </div>
  </div>
</template>

<script>
// IMPORTS & CONSTANTS
import { evntBus } from "../../bus";
import { API_MAP } from "../../api_mapper.js";

const EVENT_NAMES = {
  SHOW_COUPONS: "show_coupons",
  SHOW_MESSAGE: "show_mesage",
  UPDATE_INVOICE_COUPONS: "update_invoice_coupons",
  UPDATE_COUPONS_COUNTERS: "update_coupons_counters",
  REGISTER_POS_PROFILE: "register_pos_profile",
  UPDATE_CUSTOMER: "update_customer",
  UPDATE_POS_COUPONS: "update_pos_coupons",
  SET_POS_COUPONS: "set_pos_coupons",
};

const COUPON_TYPE = {
  PROMOTIONAL: "Promotional",
};

const TABLE_HEADERS = [
  { title: "Coupon", key: "coupon_code", align: "start" },
  { title: "Type", key: "type", align: "start" },
  { title: "POS Offer", key: "pos_offer", align: "start" },
  { title: "Applied", key: "applied", align: "start" },
];

export default {
  name: "PosCoupons",

  data() {
    return {
      loading: false,
      pos_profile: null,
      customer: "",
      posa_coupons: [],
      new_coupon: null,
      itemsPerPage: 1000,
      singleExpand: true,
      expanded: [],
      items_headers: TABLE_HEADERS,
    };
  },

  computed: {
    couponsCount() {
      return this.posa_coupons.length;
    },
    appliedCouponsCount() {
      return this.posa_coupons.filter((el) => el.applied).length;
    },
  },

  watch: {
    posa_coupons: {
      deep: true,
      handler() {
        this.updateInvoice();
        this.updateCounters();
      },
    },
  },

  methods: {
    back_to_invoice() {
      evntBus.emit(EVENT_NAMES.SHOW_COUPONS, "false");
    },

    showMessage(text, color) {
      evntBus.emit(EVENT_NAMES.SHOW_MESSAGE, { text, color });
    },

    truncateText(text, maxLength) {
      return text && text.length > maxLength
        ? text.substring(0, maxLength) + "..."
        : text;
    },

    getCouponIcon(type) {
      const icons = {
        Promotional: "mdi-sale",
        "Gift Card": "mdi-gift",
        Referral: "mdi-account-multiple",
      };
      return icons[type] || "mdi-ticket-percent";
    },

    getCouponTypeClass(type) {
      const classes = {
        Promotional: "type-promotional",
        "Gift Card": "type-gift",
        Referral: "type-referral",
      };
      return classes[type] || "type-default";
    },

    add_coupon(coupon_code) {
      if (!this.customer || !coupon_code) {
        this.showMessage("Customer or coupon code is missing", "error");
        return;
      }

      if (this.posa_coupons.some((el) => el.coupon_code === coupon_code)) {
        this.showMessage("This coupon is already used!", "error");
        return;
      }

      frappe.call({
        method: API_MAP.CUSTOMER.GET_POS_COUPON,
        args: {
          coupon: coupon_code,
          customer: this.customer,
          company: this.pos_profile.company,
        },
        callback: (r) => {
          if (r.message) {
            const { msg, coupon } = r.message;
            if (msg !== "Apply" || !coupon) {
              this.showMessage(msg, "error");
            } else {
              this.new_coupon = null;
              this.posa_coupons.push({
                coupon: coupon.name,
                coupon_code: coupon.coupon_code,
                type: coupon.coupon_type,
                applied: 0,
                pos_offer: coupon.pos_offer,
                customer: coupon.customer || this.customer,
              });
            }
          } else {
            this.showMessage("Failed to get coupon from server", "error");
          }
        },
      });
    },

    setActiveGiftCoupons() {
      if (!this.customer?.trim()) return;

      frappe.call({
        method: API_MAP.CUSTOMER.GET_CUSTOMER_COUPONS,
        args: {
          customer_id: this.customer,
          company: this.pos_profile.company,
        },
        callback: (r) => {
          if (r.message) {
            r.message.forEach((coupon_code) => this.add_coupon(coupon_code));
          } else {
            this.showMessage("Failed to get active gift coupons", "error");
          }
        },
      });
    },

    updatePosCoupons(offers) {
      this.posa_coupons.forEach((coupon) => {
        const offer = offers.find(
          (el) => el.offer_applied && el.coupon === coupon.coupon
        );
        coupon.applied = offer ? 1 : 0;
      });
    },

    removeCoupon(remove_list) {
      this.posa_coupons = this.posa_coupons.filter(
        (coupon) => !remove_list.includes(coupon.coupon)
      );
    },

    updateInvoice() {
      evntBus.emit(EVENT_NAMES.UPDATE_INVOICE_COUPONS, this.posa_coupons);
    },

    updateCounters() {
      evntBus.emit(EVENT_NAMES.UPDATE_COUPONS_COUNTERS, {
        couponsCount: this.couponsCount,
        appliedCouponsCount: this.appliedCouponsCount,
      });
    },

    handleUpdateCustomer(customer) {
      if (this.customer === customer) return;

      const to_remove = [];
      this.posa_coupons.forEach((el) => {
        if (el.type === COUPON_TYPE.PROMOTIONAL) {
          el.customer = customer;
        } else {
          to_remove.push(el.coupon);
        }
      });

      this.customer = customer;

      if (to_remove.length) {
        this.removeCoupon(to_remove);
      }

      if (this.customer?.trim()) {
        this.setActiveGiftCoupons();
      }
    },
  },

  created() {
    this.$nextTick(() => {
      evntBus.on(EVENT_NAMES.REGISTER_POS_PROFILE, (data) => {
        this.pos_profile = data.pos_profile;
      });
      evntBus.on(EVENT_NAMES.UPDATE_CUSTOMER, this.handleUpdateCustomer);
      evntBus.on(EVENT_NAMES.UPDATE_POS_COUPONS, this.updatePosCoupons);
      evntBus.on(EVENT_NAMES.SET_POS_COUPONS, (data) => {
        this.posa_coupons = data;
      });
    });
  },

  beforeDestroy() {
    // Clean up all event listeners
    evntBus.$off(EVENT_NAMES.REGISTER_POS_PROFILE);
    evntBus.$off(EVENT_NAMES.UPDATE_CUSTOMER, this.handleUpdateCustomer);
    evntBus.$off(EVENT_NAMES.UPDATE_POS_COUPONS, this.updatePosCoupons);
    evntBus.$off(EVENT_NAMES.SET_POS_COUPONS);
  },
};
</script>

<style scoped>
.coupons-wrapper {
  display: flex;
  flex-direction: column;
  height: 91vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
}
.coupons-header {
  background: linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%);
  padding: 8px 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 6px;
}
.header-title {
  color: white;
  font: 600 1rem/1 sans-serif;
  margin: 0;
}
.header-stats {
  display: flex;
  gap: 6px;
}
.stat-badge {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 3px 10px;
  display: flex;
  gap: 6px;
  backdrop-filter: blur(10px);
}
.stat-badge.active {
  background: rgba(76, 175, 80, 0.9);
}
.stat-label,
.stat-value {
  font-size: 0.6rem;
  line-height: 1;
  color: white;
}
.stat-label {
  opacity: 0.9;
  text-transform: uppercase;
  font-weight: 500;
}
.stat-value {
  font-weight: 700;
}
.add-coupon-section {
  display: flex;
  gap: 8px;
}
.coupon-input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  background: white;
  border-radius: 6px;
  padding: 0 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.input-icon {
  color: #9c27b0;
  margin-right: 6px;
}
.coupon-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 8px 4px;
  font-size: 0.85rem;
}
.coupon-input::placeholder {
  color: #999;
}
.add-button,
.back-button {
  border: none;
  border-radius: 6px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  color: white;
}
.add-button {
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
  padding: 8px 16px;
  font-size: 0.85rem;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}
.add-button:hover {
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
  background: linear-gradient(135deg, #45a049 0%, #388e3c 100%);
}
.coupons-grid {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 10px;
  align-content: start;
}
.coupons-grid::-webkit-scrollbar {
  width: 6px;
}
.coupons-grid::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}
.coupons-grid::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}
.coupon-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  border: 2px solid transparent;
}
.coupon-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border-color: rgba(156, 39, 176, 0.3);
}
.coupon-card.coupon-active {
  border-color: #4caf50;
  box-shadow: 0 4px 16px rgba(76, 175, 80, 0.3);
  background: linear-gradient(135deg, #fff 0%, #f1f8f4 100%);
}
.coupon-icon-container {
  position: relative;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.coupon-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
.type-promotional {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
}
.type-gift {
  background: linear-gradient(135deg, #e91e63 0%, #c2185b 100%);
}
.type-referral {
  background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
}
.type-default {
  background: linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%);
}
.applied-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
  color: white;
  padding: 3px 8px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 3px;
  font: 600 0.65rem/1 sans-serif;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}
.coupon-content {
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}
.coupon-code {
  font: 700 0.95rem/1 "Courier New", monospace;
  color: #9c27b0;
  text-align: center;
  padding: 4px;
  background: rgba(156, 39, 176, 0.08);
  border-radius: 6px;
}
.coupon-type,
.coupon-offer {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.7rem;
  padding: 2px 0;
}
.coupon-type {
  color: #666;
}
.coupon-offer {
  color: #ff9800;
  font-weight: 500;
}
.coupon-status {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 0 2px;
  border-top: 1px solid #f0f0f0;
  margin-top: auto;
}
.status-toggle {
  position: relative;
  width: 32px;
  height: 16px;
}
.status-toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}
.toggle-slider {
  position: absolute;
  inset: 0;
  background: #ccc;
  transition: 0.3s;
  border-radius: 20px;
}
.toggle-slider:before {
  content: "";
  position: absolute;
  width: 11px;
  height: 11px;
  left: 2.5px;
  bottom: 2.5px;
  background: white;
  transition: 0.3s;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}
.status-toggle input:checked + .toggle-slider {
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
}
.status-text {
  font: 600 0.7rem/1 sans-serif;
  color: #999;
  transition: color 0.3s;
}
.status-text.active {
  color: #4caf50;
}
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 20px;
}
.empty-text {
  font: 600 1.1rem/1 sans-serif;
  color: #999;
  margin: 16px 0 4px;
}
.empty-subtext {
  font-size: 0.85rem;
  color: #bbb;
  margin: 0;
}
.coupons-footer {
  padding: 8px 12px;
  background: white;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.08);
}
.back-button {
  width: 100%;
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
  padding: 8px;
  font-size: 0.9rem;
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
  justify-content: center;
}
.back-button:hover {
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.4);
  background: linear-gradient(135deg, #f57c00 0%, #ef6c00 100%);
}
@media (min-width: 1200px) {
  .coupons-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}
</style>
