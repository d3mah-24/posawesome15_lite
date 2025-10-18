<template>
  <div>
    <v-card
      class="selection mx-auto grey lighten-5"
      style="max-height: 80vh; height: 80vh"
    >
      <!-- ===== TEMPLATE SECTION 3: CARD TITLE ===== -->
      <v-card-title class="pb-2">
        <span class="text-h6 primary--text">Offers</span>
      </v-card-title>
      
        <!-- ===== TEMPLATE SECTION 4: OFFERS CONTAINER ===== -->
        <div class="my-0 py-0 offers-container" style="max-height: 72vh; overflow-y: auto; overflow-x: hidden;">
          <!-- ===== TEMPLATE SECTION 5: OFFERS ROW ===== -->
          <v-row dense class="px-2">
          <v-col
            v-for="(offer, idx) in pos_offers"
            :key="idx"
            xl="2"
            lg="3"
            md="4"
            sm="6"
            cols="6"
            class="d-flex"
          >
            <!-- ===== TEMPLATE SECTION 6: OFFER CARD ===== -->
            <v-card hover="hover" class="mb-2 offer-card flex-grow-1" :class="{ 'border-primary': offer.offer_applied }" style="height: 180px; width: 100%;">
              <!-- ===== TEMPLATE SECTION 7: OFFER IMAGE ===== -->
              <v-img
                :src="offer.image || '/assets/posawesome/js/posapp/components/pos/placeholder-image.png'"
                class="white--text align-end"
                gradient="to bottom, rgba(0,0,0,0), rgba(0,0,0,0.6)"
                height="80px"
              >
                <v-card-text class="text-caption px-1 pb-0" style="font-size: 0.65rem;">
                  <div class="font-weight-bold">{{ offer.name.length > 12 ? offer.name.substring(0, 12) + '...' : offer.name }}</div>
                </v-card-text>
              </v-img>
              <!-- ===== TEMPLATE SECTION 8: OFFER DETAILS ===== -->
              <v-card-text class="text--primary pa-1 d-flex flex-column justify-space-between" style="height: 100px;">
                <div>
                  <div class="text-xs mb-1" v-if="offer.discount_percentage">
                    Discount %: {{ offer.discount_percentage }}%
                  </div>
                  <div class="text-xs mb-1" v-if="offer.discount_amount">
                    Discount Amount: {{ formatCurrency(offer.discount_amount) }}
                  </div>
                                      <div class="text-xs mb-1 warning--text" 
                         v-if="offer.offer === 'Grand Total' && !offer.offer_applied && 
                               discount_percentage_offer_name && discount_percentage_offer_name !== offer.name">
                      Another offer currently applied
                    </div>
                </div>
                <v-row no-gutters align="center">
                  <v-col>
                    <v-checkbox
                      v-model="offer.offer_applied"
                      @change="forceUpdateItem"
                      color="primary"
                      label="Applied"
                      hide-details
                      dense
                      class="mt-0 pt-0"
                      :disabled="Boolean(
                        (offer.offer == 'Give Product' &&
                          !offer.give_item &&
                          (!offer.replace_cheapest_item || !offer.replace_item)) ||
                        (offer.offer == 'Grand Total' &&
                          discount_percentage_offer_name &&
                          discount_percentage_offer_name != offer.name)
                      )"
                    ></v-checkbox>
                  </v-col>
                  <v-col cols="auto" v-if="offer.offer_applied">
                    <v-icon color="success" x-small>mdi-check-circle</v-icon>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </v-card>

    <!-- ===== TEMPLATE SECTION 9: BOTTOM CARD ===== -->
    <v-card
      flat
      style="max-height: 11vh; height: 11vh"
      class="cards mb-0 mt-3 py-0"
    >
      <v-row align="start" no-gutters>
        <v-col cols="12">
          <v-btn
            block
            class="pa-1"
            large
            color="warning"
            dark
            @click="back_to_invoice"
            >Back</v-btn
          >
          <!-- ===== TEMPLATE SECTION 10: BACK BUTTON ===== -->
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script>
// ===== SECTION 1: IMPORTS =====
import { evntBus } from '../../bus';
import format from '../../format';

// CONSTANTS
const EVENT_NAMES = {
  SHOW_OFFERS: 'show_offers',
  SHOW_MESSAGE: 'show_mesage',
  UPDATE_INVOICE_OFFERS: 'update_invoice_offers',
  UPDATE_OFFERS_COUNTERS: 'update_offers_counters',
  UPDATE_POS_COUPONS: 'update_pos_coupons',
  REGISTER_POS_PROFILE: 'register_pos_profile',
  UPDATE_CUSTOMER: 'update_customer',
  SET_OFFERS: 'set_offers',
  UPDATE_POS_OFFERS: 'update_pos_offers',
  UPDATE_DISCOUNT_PERCENTAGE_OFFER_NAME: 'update_discount_percentage_offer_name',
  SET_ALL_ITEMS: 'set_all_items'
};

const OFFER_TYPES = {
  GRAND_TOTAL: 'Grand Total',
  GIVE_PRODUCT: 'Give Product'
};

const APPLY_TYPES = {
  ITEM_CODE: 'Item Code',
  ITEM_GROUP: 'Item Group'
};

const ITEMS_HEADERS = [
  { title: 'Name', key: 'name', align: 'start' },
  { title: 'Apply On', key: 'apply_on', align: 'start' },
  { title: 'Offer', key: 'offer', align: 'start' },
  { title: 'Applied', key: 'offer_applied', align: 'start' }
];

// ===== SECTION 2: EXPORT DEFAULT =====
export default {
  mixins: [format],

  // ===== SECTION 3: DATA =====
  data() {
    return {
      loading: false,
      pos_profile: '',
      pos_offers: [],
      allItems: [],
      discount_percentage_offer_name: null,
      itemsPerPage: 1000,
      expanded: [],
      singleExpand: true,
      items_headers: ITEMS_HEADERS
    };
  },

  // ===== SECTION 4: COMPUTED =====
  computed: {
    offersCount() {
      return this.pos_offers.length;
    },
    appliedOffersCount() {
      return this.pos_offers.filter(el => el.offer_applied).length;
    }
  },

  // ===== SECTION 5: METHODS =====
  methods: {
    back_to_invoice() {
      evntBus.emit(EVENT_NAMES.SHOW_OFFERS, 'false');
    },

    forceUpdateItem() {
      this.pos_offers = [...this.pos_offers];
      this.handleManualOfferChange();
    },

    handleManualOfferChange() {
      try {
        const appliedGrandTotalOffers = this.pos_offers.filter(
          offer => offer.offer === OFFER_TYPES.GRAND_TOTAL && offer.offer_applied
        );

        if (appliedGrandTotalOffers.length > 1) {
          this.applyBestGrandTotalOffer();
        } else if (appliedGrandTotalOffers.length === 1) {
          this.discount_percentage_offer_name = appliedGrandTotalOffers[0].name;
          this.pos_offers.forEach(offer => {
            if (offer.offer === OFFER_TYPES.GRAND_TOTAL && offer.name !== appliedGrandTotalOffers[0].name) {
              offer.offer_applied = false;
            }
          });
        } else {
          this.discount_percentage_offer_name = null;
        }
      } catch (error) {
        this.showMessage('Error processing offer change', 'error');
      }
    },

    makeid(length) {
      const characters = 'abcdefghijklmnopqrstuvwxyz0123456789';
      return Array.from({ length }, () => 
        characters.charAt(Math.floor(Math.random() * characters.length))
      ).join('');
    },

    updatePosOffers(appliedOffers) {
      try {
        this.pos_offers.forEach(pos_offer => {
          pos_offer.offer_applied = appliedOffers.some(offer =>
            offer.name === pos_offer.name ||
            offer.offer_name === pos_offer.name ||
            offer.name === pos_offer.title
          );
        });
      } catch (error) {
        console.error('[PosOffers] error updating applied offers:', error);
      }
    },

    applyBestGrandTotalOffer() {
      try {
        const grandTotalOffers = this.pos_offers.filter(
          offer => offer.offer === OFFER_TYPES.GRAND_TOTAL
        );

        if (grandTotalOffers.length === 0) return;

        if (grandTotalOffers.length > 1) {
          grandTotalOffers.sort((a, b) => {
            const discountA = parseFloat(a.discount_percentage || 0);
            const discountB = parseFloat(b.discount_percentage || 0);
            return discountB - discountA;
          });

          grandTotalOffers.forEach(offer => offer.offer_applied = false);
          grandTotalOffers[0].offer_applied = true;
          this.discount_percentage_offer_name = grandTotalOffers[0].name;
          this.showMessage('Best offer applied: ' + grandTotalOffers[0].name, 'success');
        } else {
          grandTotalOffers[0].offer_applied = true;
          this.discount_percentage_offer_name = grandTotalOffers[0].name;
        }
      } catch (error) {
        this.showMessage('Error applying best offer', 'error');
      }
    },

    removeOffers(offers_id_list) {
      try {
        this.pos_offers = this.pos_offers.filter(
          offer => !offers_id_list.includes(offer.row_id)
        );
      } catch (error) {
        this.showMessage('Error removing offers', 'error');
      }
    },

    handelOffers() {
      try {
        const applyedOffers = this.pos_offers.filter(offer => offer.offer_applied);
        evntBus.emit(EVENT_NAMES.UPDATE_INVOICE_OFFERS, applyedOffers);
      } catch (error) {
        this.showMessage('Error processing offers', 'error');
      }
    },

    handleNewLine(str) {
      return str ? str.replace(/(?:\r\n|\r|\n)/g, '<br />') : '';
    },

    get_give_items(offer) {
      try {
        if (offer.apply_type === APPLY_TYPES.ITEM_CODE) {
          return [offer.apply_item_code];
        }

        if (offer.apply_type === APPLY_TYPES.ITEM_GROUP) {
          let filterd_items = this.allItems.filter(
            item => item.item_group === offer.apply_item_group
          );

          if (offer.less_then > 0) {
            filterd_items = filterd_items.filter(item => item.rate < offer.less_then);
          }

          return filterd_items;
        }

        return [];
      } catch (error) {
        this.showMessage('Error getting free items', 'error');
        return [];
      }
    },

    updateCounters() {
      try {
        evntBus.emit(EVENT_NAMES.UPDATE_OFFERS_COUNTERS, {
          offersCount: this.offersCount,
          appliedOffersCount: this.appliedOffersCount
        });
      } catch (error) {
        this.showMessage('Error updating counters', 'error');
      }
    },

    updatePosCoupuns() {
      try {
        const applyedOffers = this.pos_offers.filter(
          offer => offer.offer_applied && offer.coupon_based
        );
        evntBus.emit(EVENT_NAMES.UPDATE_POS_COUPONS, applyedOffers);
      } catch (error) {
        this.showMessage('Error updating coupons', 'error');
      }
    },

    showMessage(text, color) {
      evntBus.emit(EVENT_NAMES.SHOW_MESSAGE, { text, color });
    }
  },

  // ===== SECTION 6: WATCH =====
  watch: {
    pos_offers: {
      deep: true,
      handler() {
        this.handelOffers();
        this.updateCounters();
        this.updatePosCoupuns();
      }
    }
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
        this.pos_offers = data.map(offer => ({
          ...offer,
          row_id: offer.row_id || this.makeid(20),
          offer_applied: !!offer.offer_applied
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
  }
};
</script>

<style scoped>
.border-primary {
  border: 3px solid #1976d2 !important;
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.4) !important;
}

.offer-card {
  transition: all 0.3s ease-in-out;
  height: 180px !important;
  width: 100% !important;
  display: flex !important;
  flex-direction: column !important;
}

.offer-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15) !important;
}

.text-xs {
  font-size: 0.6rem !important;
  line-height: 1.2;
}

.v-card__text {
  padding: 4px 8px !important;
}

.v-input--checkbox .v-input__control {
  min-height: 20px !important;
}

.v-input--checkbox .v-label {
  font-size: 0.65rem !important;
}

/* Force cards to same size */
.d-flex {
  display: flex !important;
}

.flex-grow-1 {
  flex-grow: 1 !important;
}

/* Vertical scrollbar only when needed */
.offers-container {
  scrollbar-width: thin;
  scrollbar-color: #ccc transparent;
}

.offers-container::-webkit-scrollbar {
  width: 6px;
}

.offers-container::-webkit-scrollbar-track {
  background: transparent;
}

.offers-container::-webkit-scrollbar-thumb {
  background-color: #ccc;
  border-radius: 3px;
}

.offers-container::-webkit-scrollbar-thumb:hover {
  background-color: #999;
}

/* Hide horizontal scrollbar */
.offers-container::-webkit-scrollbar-horizontal {
  display: none;
}

.v-row {
  overflow-x: hidden !important;
}

/* Improve applied card appearance */
.border-primary .v-img {
  border-bottom: 2px solid #1976d2;
}

.border-primary .v-card__text {
  background: linear-gradient(135deg, rgba(25, 118, 210, 0.05) 0%, rgba(25, 118, 210, 0.1) 100%);
}
</style>