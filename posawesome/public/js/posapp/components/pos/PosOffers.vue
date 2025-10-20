<template>
  <div class="offers-wrapper">
    <!-- HEADER WITH STATS -->
    <div class="offers-header">
      <div class="header-content">
        <div class="header-left">
          <v-icon color="white" size="22">mdi-tag-multiple</v-icon>
          <h2 class="header-title">Special Offers</h2>
        </div>
        <div class="header-stats">
          <div class="stat-badge">
            <span class="stat-label">Total</span>
            <span class="stat-value">{{ offersCount }}</span>
          </div>
          <div class="stat-badge active">
            <span class="stat-label">Active</span>
            <span class="stat-value">{{ appliedOffersCount }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- OFFERS GRID -->
    <div class="offers-grid">
      <div
        v-for="(offer, idx) in pos_offers"
        :key="idx"
        class="offer-card-wrapper"
      >
        <div
          class="offer-card"
          :class="{ 'offer-active': offer.offer_applied }"
          @click="toggleOffer(offer)"
        >
          <!-- OFFER IMAGE WITH OVERLAY -->
          <div class="offer-image-container">
            <img
              :src="
                offer.image ||
                '/assets/posawesome/js/posapp/components/pos/placeholder-image.png'
              "
              class="offer-image"
              @error="handleImageError"
            />
            <div class="offer-overlay">
              <div class="offer-name">{{ truncateName(offer.name, 15) }}</div>
            </div>

            <!-- APPLIED BADGE -->
            <div v-if="offer.offer_applied" class="applied-badge">
              <v-icon size="14" color="white">mdi-check-circle</v-icon>
              <span>Active</span>
            </div>
          </div>

          <!-- OFFER CONTENT -->
          <div class="offer-content">
            <!-- DISCOUNT INFO -->
            <div class="discount-info">
              <div v-if="offer.discount_percentage" class="discount-main">
                <span class="discount-value"
                  >{{ offer.discount_percentage }}%</span
                >
                <span class="discount-label">OFF</span>
              </div>
              <div v-else-if="offer.discount_amount" class="discount-main">
                <span class="discount-value">{{
                  formatCurrency(offer.discount_amount)
                }}</span>
                <span class="discount-label">OFF</span>
              </div>
              <div v-else class="discount-main special">
                <v-icon size="18" color="#4CAF50">mdi-gift</v-icon>
                <span class="discount-label">Special Offer</span>
              </div>
            </div>

            <!-- WARNING MESSAGE -->
            <div
              v-if="
                offer.offer === 'Grand Total' &&
                !offer.offer_applied &&
                discount_percentage_offer_name &&
                discount_percentage_offer_name !== offer.name
              "
              class="warning-msg"
            >
              <v-icon size="12" color="warning">mdi-alert-circle</v-icon>
              <span>Another offer active</span>
            </div>

            <!-- APPLY TOGGLE -->
            <div class="offer-toggle">
              <label class="toggle-switch">
                <input
                  type="checkbox"
                  v-model="offer.offer_applied"
                  @change="forceUpdateItem"
                  :disabled="isOfferDisabled(offer)"
                />
                <span class="toggle-slider"></span>
              </label>
              <span class="toggle-text">{{
                offer.offer_applied ? "Applied" : "Apply"
              }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- FOOTER -->
    <div class="offers-footer">
      <button class="back-button" @click="back_to_invoice">
        <v-icon size="18">mdi-arrow-left</v-icon>
        <span>Back to Invoice</span>
      </button>
    </div>
  </div>
</template>

<script>
// ===== SECTION 1: IMPORTS =====
import { evntBus } from "../../bus";
import format from "../../format";

// CONSTANTS
const EVENT_NAMES = {
  SHOW_OFFERS: "show_offers",
  SHOW_MESSAGE: "show_mesage",
  UPDATE_INVOICE_OFFERS: "update_invoice_offers",
  UPDATE_OFFERS_COUNTERS: "update_offers_counters",
  UPDATE_POS_COUPONS: "update_pos_coupons",
  REGISTER_POS_PROFILE: "register_pos_profile",
  UPDATE_CUSTOMER: "update_customer",
  SET_OFFERS: "set_offers",
  UPDATE_POS_OFFERS: "update_pos_offers",
  UPDATE_DISCOUNT_PERCENTAGE_OFFER_NAME:
    "update_discount_percentage_offer_name",
  SET_ALL_ITEMS: "set_all_items",
};

const OFFER_TYPES = {
  GRAND_TOTAL: "Grand Total",
  GIVE_PRODUCT: "Give Product",
};

const APPLY_TYPES = {
  ITEM_CODE: "Item Code",
  ITEM_GROUP: "Item Group",
};

const ITEMS_HEADERS = [
  { title: "Name", key: "name", align: "start" },
  { title: "Apply On", key: "apply_on", align: "start" },
  { title: "Offer", key: "offer", align: "start" },
  { title: "Applied", key: "offer_applied", align: "start" },
];

// ===== SECTION 2: EXPORT DEFAULT =====
export default {
  mixins: [format],

  // ===== SECTION 3: DATA =====
  data() {
    return {
      loading: false,
      pos_profile: "",
      pos_offers: [],
      allItems: [],
      discount_percentage_offer_name: null,
      itemsPerPage: 1000,
      expanded: [],
      singleExpand: true,
      items_headers: ITEMS_HEADERS,
    };
  },

  // ===== SECTION 4: COMPUTED =====
  computed: {
    offersCount() {
      return this.pos_offers.length;
    },
    appliedOffersCount() {
      return this.pos_offers.filter((el) => el.offer_applied).length;
    },
  },

  // ===== SECTION 5: METHODS =====
  methods: {
    back_to_invoice() {
      evntBus.emit(EVENT_NAMES.SHOW_OFFERS, "false");
    },

    forceUpdateItem() {
      this.pos_offers = [...this.pos_offers];
      this.handleManualOfferChange();
    },

    toggleOffer(offer) {
      if (!this.isOfferDisabled(offer)) {
        console.log("Toggling offer:", offer);
        offer.offer_applied = !offer.offer_applied;
        this.forceUpdateItem();
      }
      if (offer.offer_applied) {
        console.log("Offer applied:", offer);
        this.$emit("offerApplied", offer);
      } else {
        console.log("Offer removed:", offer);
        this.$emit("offerRemoved", false);
      }
    },

    isOfferDisabled(offer) {
      return Boolean(
        (offer.offer === "Give Product" &&
          !offer.give_item &&
          (!offer.replace_cheapest_item || !offer.replace_item)) ||
          (offer.offer === "Grand Total" &&
            this.discount_percentage_offer_name &&
            this.discount_percentage_offer_name !== offer.name)
      );
    },

    truncateName(name, maxLength) {
      return name && name.length > maxLength
        ? name.substring(0, maxLength) + "..."
        : name;
    },

    handleImageError(event) {
      event.target.src =
        "/assets/posawesome/js/posapp/components/pos/placeholder-image.png";
    },

    handleManualOfferChange() {
      try {
        const appliedGrandTotalOffers = this.pos_offers.filter(
          (offer) =>
            offer.offer === OFFER_TYPES.GRAND_TOTAL && offer.offer_applied
        );

        if (appliedGrandTotalOffers.length > 1) {
          this.applyBestGrandTotalOffer();
        } else if (appliedGrandTotalOffers.length === 1) {
          this.discount_percentage_offer_name = appliedGrandTotalOffers[0].name;
          this.pos_offers.forEach((offer) => {
            if (
              offer.offer === OFFER_TYPES.GRAND_TOTAL &&
              offer.name !== appliedGrandTotalOffers[0].name
            ) {
              offer.offer_applied = false;
            }
          });
        } else {
          this.discount_percentage_offer_name = null;
        }
      } catch (error) {
        this.showMessage("Error processing offer change", "error");
      }
    },

    makeid(length) {
      const characters = "abcdefghijklmnopqrstuvwxyz0123456789";
      return Array.from({ length }, () =>
        characters.charAt(Math.floor(Math.random() * characters.length))
      ).join("");
    },

    updatePosOffers(appliedOffers) {
      try {
        this.pos_offers.forEach((pos_offer) => {
          pos_offer.offer_applied = appliedOffers.some(
            (offer) =>
              offer.name === pos_offer.name ||
              offer.offer_name === pos_offer.name ||
              offer.name === pos_offer.title
          );
        });
      } catch (error) {
        console.error("[PosOffers] error updating applied offers:", error);
      }
    },

    applyBestGrandTotalOffer() {
      try {
        const grandTotalOffers = this.pos_offers.filter(
          (offer) => offer.offer === OFFER_TYPES.GRAND_TOTAL
        );

        if (grandTotalOffers.length === 0) return;

        if (grandTotalOffers.length > 1) {
          grandTotalOffers.sort((a, b) => {
            const discountA = parseFloat(a.discount_percentage || 0);
            const discountB = parseFloat(b.discount_percentage || 0);
            return discountB - discountA;
          });

          grandTotalOffers.forEach((offer) => (offer.offer_applied = false));
          grandTotalOffers[0].offer_applied = true;
          this.discount_percentage_offer_name = grandTotalOffers[0].name;
          this.showMessage(
            "Best offer applied: " + grandTotalOffers[0].name,
            "success"
          );
        } else {
          grandTotalOffers[0].offer_applied = true;
          this.discount_percentage_offer_name = grandTotalOffers[0].name;
        }
      } catch (error) {
        this.showMessage("Error applying best offer", "error");
      }
    },

    removeOffers(offers_id_list) {
      try {
        this.pos_offers = this.pos_offers.filter(
          (offer) => !offers_id_list.includes(offer.row_id)
        );
      } catch (error) {
        this.showMessage("Error removing offers", "error");
      }
    },

    handelOffers() {
      try {
        const applyedOffers = this.pos_offers.filter(
          (offer) => offer.offer_applied
        );
        evntBus.emit(EVENT_NAMES.UPDATE_INVOICE_OFFERS, applyedOffers);
      } catch (error) {
        this.showMessage("Error processing offers", "error");
      }
    },

    handleNewLine(str) {
      return str ? str.replace(/(?:\r\n|\r|\n)/g, "<br />") : "";
    },

    get_give_items(offer) {
      try {
        if (offer.apply_type === APPLY_TYPES.ITEM_CODE) {
          return [offer.apply_item_code];
        }

        if (offer.apply_type === APPLY_TYPES.ITEM_GROUP) {
          let filterd_items = this.allItems.filter(
            (item) => item.item_group === offer.apply_item_group
          );

          if (offer.less_then > 0) {
            filterd_items = filterd_items.filter(
              (item) => item.rate < offer.less_then
            );
          }

          return filterd_items;
        }

        return [];
      } catch (error) {
        this.showMessage("Error getting free items", "error");
        return [];
      }
    },

    updateCounters() {
      try {
        evntBus.emit(EVENT_NAMES.UPDATE_OFFERS_COUNTERS, {
          offersCount: this.offersCount,
          appliedOffersCount: this.appliedOffersCount,
        });
      } catch (error) {
        this.showMessage("Error updating counters", "error");
      }
    },

    updatePosCoupuns() {
      try {
        const applyedOffers = this.pos_offers.filter(
          (offer) => offer.offer_applied && offer.coupon_based
        );
        evntBus.emit(EVENT_NAMES.UPDATE_POS_COUPONS, applyedOffers);
      } catch (error) {
        this.showMessage("Error updating coupons", "error");
      }
    },

    showMessage(text, color) {
      evntBus.emit(EVENT_NAMES.SHOW_MESSAGE, { text, color });
    },
  },

  // ===== SECTION 6: WATCH =====
  watch: {
    pos_offers: {
      deep: true,
      handler() {
        this.handelOffers();
        this.updateCounters();
        this.updatePosCoupuns();
      },
    },
  },

  // ===== SECTION 7: CREATED =====
  created() {
    this.$nextTick(() => {
      evntBus.on(EVENT_NAMES.REGISTER_POS_PROFILE, (data) => {
        this.pos_profile = data.pos_profile;
      });

      evntBus.on(EVENT_NAMES.UPDATE_CUSTOMER, (customer) => {
        if (this.customer !== customer) {
          this.offers = [];
        }
      });

      evntBus.on(EVENT_NAMES.SET_OFFERS, (data) => {
        this.pos_offers = data.map((offer) => ({
          ...offer,
          row_id: offer.row_id || this.makeid(20),
          offer_applied: !!offer.offer_applied,
        }));
      });

      evntBus.on(EVENT_NAMES.UPDATE_POS_OFFERS, (data) => {
        this.updatePosOffers(data);
      });

      evntBus.on(EVENT_NAMES.UPDATE_DISCOUNT_PERCENTAGE_OFFER_NAME, (data) => {
        this.discount_percentage_offer_name = data.value;
      });

      evntBus.on(EVENT_NAMES.SET_ALL_ITEMS, (data) => {
        this.allItems = data;
      });
    });
  },

  beforeDestroy() {
    // Clean up all event listeners
    evntBus.$off(EVENT_NAMES.REGISTER_POS_PROFILE);
    evntBus.$off(EVENT_NAMES.UPDATE_CUSTOMER);
    evntBus.$off(EVENT_NAMES.SET_OFFERS);
    evntBus.$off(EVENT_NAMES.UPDATE_POS_OFFERS);
    evntBus.$off(EVENT_NAMES.UPDATE_DISCOUNT_PERCENTAGE_OFFER_NAME);
    evntBus.$off(EVENT_NAMES.SET_ALL_ITEMS);
  },
};
</script>

<style scoped>
/* ===== WRAPPER ===== */
.offers-wrapper {
  display: flex;
  flex-direction: column;
  height: 91vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
}

/* ===== HEADER ===== */
.offers-header {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  padding: 8px 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 10;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.header-title {
  color: white;
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: 0.3px;
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
  align-items: center;
  min-width: 50px;
  backdrop-filter: blur(10px);
}

.stat-badge.active {
  background: rgba(76, 175, 80, 0.9);
}

.stat-label {
  font-size: 0.6rem;
  color: rgba(255, 255, 255, 0.9);
  text-transform: uppercase;
  font-weight: 500;
  line-height: 1;
}

.stat-value {
  font-size: 0.6rem;
  color: white;
  font-weight: 700;
  line-height: 1;
}

/* ===== OFFERS GRID ===== */
.offers-grid {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 8px;
  align-content: start;
}

/* Custom scrollbar */
.offers-grid::-webkit-scrollbar {
  width: 6px;
}

.offers-grid::-webkit-scrollbar-track {
  background: transparent;
}

.offers-grid::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.offers-grid::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

/* ===== OFFER CARD ===== */
.offer-card-wrapper {
  display: flex;
}

.offer-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  width: 100%;
  border: 2px solid transparent;
}

.offer-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border-color: rgba(25, 118, 210, 0.3);
}

.offer-card.offer-active {
  border-color: #4caf50;
  box-shadow: 0 4px 16px rgba(76, 175, 80, 0.3);
  background: linear-gradient(135deg, #ffffff 0%, #f1f8f4 100%);
}

/* ===== IMAGE CONTAINER ===== */
.offer-image-container {
  position: relative;
  height: 70px;
  overflow: hidden;
}

.offer-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.offer-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
  padding: 4px 6px 3px;
}

.offer-name {
  color: white;
  font-size: 0.65rem;
  font-weight: 600;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
  line-height: 1.2;
}

/* ===== APPLIED BADGE ===== */
.applied-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 0.6rem;
  font-weight: 600;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

/* ===== OFFER CONTENT ===== */
.offer-content {
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
}

/* ===== DISCOUNT INFO ===== */
.discount-info {
  flex: 1;
}

.discount-main {
  display: flex;
  align-items: baseline;
  gap: 3px;
  padding: 3px 0;
}

.discount-main.special {
  align-items: center;
  gap: 4px;
}

.discount-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1976d2;
  line-height: 1;
}

.discount-label {
  font-size: 0.6rem;
  color: #666;
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.3px;
}

/* ===== WARNING MESSAGE ===== */
.warning-msg {
  display: flex;
  align-items: center;
  gap: 3px;
  background: rgba(255, 152, 0, 0.1);
  padding: 3px 5px;
  border-radius: 4px;
  font-size: 0.6rem;
  color: #f57c00;
  border-left: 2px solid #ff9800;
}

/* ===== TOGGLE SWITCH ===== */
.offer-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 0 0;
  border-top: 1px solid #f0f0f0;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 32px;
  height: 16px;
  flex-shrink: 0;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  border-radius: 20px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 11px;
  width: 11px;
  left: 2.5px;
  bottom: 2.5px;
  background-color: white;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.toggle-switch input:checked + .toggle-slider {
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
}

.toggle-switch input:checked + .toggle-slider:before {
  transform: translateX(16px);
}

.toggle-switch input:disabled + .toggle-slider {
  background-color: #e0e0e0;
  cursor: not-allowed;
  opacity: 0.5;
}

.toggle-text {
  font-size: 0.65rem;
  font-weight: 600;
  color: #666;
}

.toggle-switch input:checked ~ .toggle-text {
  color: #4caf50;
}

/* ===== FOOTER ===== */
.offers-footer {
  padding: 8px 12px;
  background: white;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.08);
  z-index: 10;
}

.back-button {
  width: 100%;
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
}

.back-button:hover {
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.4);
  background: linear-gradient(135deg, #f57c00 0%, #ef6c00 100%);
}

@media (min-width: 1200px) {
  .offers-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style>
