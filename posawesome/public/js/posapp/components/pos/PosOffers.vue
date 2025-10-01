<template>
  <!-- ===== TEMPLATE SECTION 1: MAIN CONTAINER ===== -->
  <div>
    {{ console.log({template: "main div", result: "main container rendered"}) }}
    <!-- ===== TEMPLATE SECTION 2: OFFERS CARD ===== -->
    <v-card
      class="selection mx-auto grey lighten-5"
      style="max-height: 80vh; height: 80vh"
    >
      <!-- ===== TEMPLATE SECTION 3: CARD TITLE ===== -->
      <v-card-title class="pb-2">
        <span class="text-h6 primary--text">Offers</span>
      </v-card-title>
      {{ console.log({template: "card title", result: "title rendered"}) }}
      
        <!-- ===== TEMPLATE SECTION 4: OFFERS CONTAINER ===== -->
        <div class="my-0 py-0 offers-container" style="max-height: 72vh; overflow-y: auto; overflow-x: hidden;">
          {{ console.log({template: "offers container", result: "offers container rendered"}) }}
          <!-- ===== TEMPLATE SECTION 5: OFFERS ROW ===== -->
          <v-row dense class="px-2">
            {{ console.log({template: "offers row", result: "offers row rendered"}) }}
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
              {{ console.log({template: "offer card", name: offer.name, result: "offer card rendered"}) }}
              <!-- ===== TEMPLATE SECTION 7: OFFER IMAGE ===== -->
              <v-img
                :src="offer.image || '/assets/posawesome/js/posapp/components/pos/placeholder-image.png'"
                class="white--text align-end"
                gradient="to bottom, rgba(0,0,0,0), rgba(0,0,0,0.6)"
                height="80px"
              >
                {{ console.log({template: "offer image", name: offer.name, result: "offer image rendered"}) }}
                <v-card-text class="text-caption px-1 pb-0" style="font-size: 0.65rem;">
                  <div class="font-weight-bold">{{ offer.name.length > 12 ? offer.name.substring(0, 12) + '...' : offer.name }}</div>
                </v-card-text>
              </v-img>
              <!-- ===== TEMPLATE SECTION 8: OFFER DETAILS ===== -->
              <v-card-text class="text--primary pa-1 d-flex flex-column justify-space-between" style="height: 100px;">
                {{ console.log({template: "offer details", name: offer.name, result: "offer details rendered"}) }}
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
                      @click="console.log({template: 'offer checkbox', name: offer.name})"
                      :disabled="
                        (offer.offer == 'Give Product' &&
                          !offer.give_item &&
                          (!offer.replace_cheapest_item || !offer.replace_item)) ||
                        (offer.offer == 'Grand Total' &&
                          discount_percentage_offer_name &&
                          discount_percentage_offer_name != offer.name)
                      "
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
      {{ console.log({template: "bottom card", result: "bottom card rendered"}) }}
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
          {{ console.log({template: "back button", result: "back button rendered"}) }}
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script>
// ===== SECTION 1: IMPORTS =====
console.log({script: "imports start"});
import { evntBus } from '../../bus';
import format from '../../format';
console.log({script: "imports end", result: "2 imports loaded successfully"});
// ===== SECTION 2: EXPORT DEFAULT =====
export default {
  mixins: [format],
  // ===== SECTION 3: DATA =====
  data: () => {
    console.log({script: "data start"});
    return {
      loading: false,
      pos_profile: '',
      pos_offers: [],
      allItems: [],
      discount_percentage_offer_name: null,
      itemsPerPage: 1000,
      expanded: [],
      singleExpand: true,
      items_headers: [
        { title: 'Name', key: 'name', align: 'start' },
        { title: 'Apply On', key: 'apply_on', align: 'start' },
        { title: 'Offer', key: 'offer', align: 'start' },
        { title: 'Applied', key: 'offer_applied', align: 'start' },
      ]
    };
    console.log({script: "data end", result: "data object initialized successfully"});
  },

  // ===== SECTION 4: COMPUTED =====
  computed: {
    offersCount() {
      return this.pos_offers.length;
    },
    appliedOffersCount() {
      return this.pos_offers.filter((el) => !!el.offer_applied).length;
    }
  },

  // ===== SECTION 5: METHODS =====
  methods: {
    back_to_invoice() {
      console.log('back_to_invoice called');
      evntBus.emit('show_offers', 'false');
    },
    forceUpdateItem() {
      console.log('forceUpdateItem called');
      let list_offers = [];
      list_offers = [...this.pos_offers];
      this.pos_offers = list_offers;
      // Check for overlapping offers during manual changes
      this.handleManualOfferChange();
    },
    handleManualOfferChange() {
      console.log('handleManualOfferChange called');
      try {
        // Find applied Grand Total offers
        const appliedGrandTotalOffers = this.pos_offers.filter(
          (offer) => offer.offer === 'Grand Total' && offer.offer_applied
        );
        if (appliedGrandTotalOffers.length > 1) {
          // If more than one offer is applied, apply only the best one
          this.applyBestGrandTotalOffer();
        } else if (appliedGrandTotalOffers.length === 1) {
          // Update the applied offer name
          this.discount_percentage_offer_name = appliedGrandTotalOffers[0].name;
          // Cancel remaining Grand Total offers
          this.pos_offers.forEach((offer) => {
            if (offer.offer === 'Grand Total' && offer.name !== appliedGrandTotalOffers[0].name) {
              offer.offer_applied = false;
            }
          });
        } else {
          // No offers applied
          this.discount_percentage_offer_name = null;
        }
      } catch (error) {
        evntBus.emit('show_mesage', {
          text: 'Error processing offer change',
          color: 'error'
        });
      }
    },
    makeid(length) {
      console.log('makeid called with length:', length);
      try {
        let result = '';
        const characters = 'abcdefghijklmnopqrstuvwxyz0123456789';
        const charactersLength = characters.length;
        for (var i = 0; i < length; i++) {
          result += characters.charAt(
            Math.floor(Math.random() * charactersLength)
          );
        }
        return result;
      } catch (error) {
        evntBus.emit('show_mesage', {
          text: 'Error creating ID',
          color: 'error'
        });
        return '';
      }
    },
    updatePosOffers(offers) {
      console.log('updatePosOffers called with offers:', offers);
      try {
        const toRemove = [];
        this.pos_offers.forEach((pos_offer) => {
          const offer = offers.find((offer) => offer.name === pos_offer.name);
          if (!offer) {
            toRemove.push(pos_offer.row_id);
          }
        });
        this.removeOffers(toRemove);
        offers.forEach((offer) => {
          const pos_offer = this.pos_offers.find(
            (pos_offer) => offer.name === pos_offer.name
          );
          if (pos_offer) {
            pos_offer.items = offer.items;
            pos_offer.min_amount = offer.min_amount;
            pos_offer.discount_percentage = offer.discount_percentage;
            pos_offer.discount_amount = offer.discount_amount;
            // Don't change application status for existing offers until we apply new logic
          } else {
            const newOffer = { ...offer };
            if (!offer.row_id) {
              newOffer.row_id = this.makeid(20);
            }
            if (offer.apply_type == 'Item Code') {
              newOffer.give_item = offer.apply_item_code || 'Nothing';
            }
            // Set initial application state
            if (offer.offer_applied) {
              newOffer.offer_applied = !!offer.offer_applied;
            } else {
              if (
                offer.apply_type == 'Item Group' &&
                offer.offer == 'Give Product' &&
                !offer.replace_cheapest_item &&
                !offer.replace_item
              ) {
                newOffer.offer_applied = false;
              } else {
                newOffer.offer_applied = !!offer.auto;
              }
            }
            if (newOffer.offer == 'Give Product' && !newOffer.give_item) {
              newOffer.give_item = this.get_give_items(newOffer)[0].item_code;
            }
            this.pos_offers.push(newOffer);
            evntBus.emit('show_mesage', {
              text: 'Offer applied to invoice',
              color: 'warning',
            });
          }
        });
        // Apply best offer logic for overlapping offers
        this.applyBestGrandTotalOffer();
      } catch (error) {
        evntBus.emit('show_mesage', {
          text: 'Error updating offers',
          color: 'error'
        });
      }
    },
    applyBestGrandTotalOffer() {
      console.log('applyBestGrandTotalOffer called');
      try {
        // Find all available Grand Total offers (applied or not)
        const grandTotalOffers = this.pos_offers.filter(
          (offer) => offer.offer === 'Grand Total'
        );
        if (grandTotalOffers.length > 1) {
          // Sort offers by discount percentage (highest to lowest)
          grandTotalOffers.sort((a, b) => {
            const discountA = parseFloat(a.discount_percentage || 0);
            const discountB = parseFloat(b.discount_percentage || 0);
            return discountB - discountA;
          });
          // Cancel all offers first
          grandTotalOffers.forEach((offer) => {
            offer.offer_applied = false;
          });
          // Apply only the best offer
          if (grandTotalOffers.length > 0) {
            grandTotalOffers[0].offer_applied = true;
            this.discount_percentage_offer_name = grandTotalOffers[0].name;
            evntBus.emit('show_mesage', {
              text: 'Best offer applied: ' + grandTotalOffers[0].name,
              color: 'success',
            });
          }
        } else if (grandTotalOffers.length === 1) {
          // Single offer only - apply it
          grandTotalOffers[0].offer_applied = true;
          this.discount_percentage_offer_name = grandTotalOffers[0].name;
        }
      } catch (error) {
        evntBus.emit('show_mesage', {
          text: 'Error applying best offer',
          color: 'error'
        });
      }
    },
    removeOffers(offers_id_list) {
      console.log('removeOffers called with offers_id_list:', offers_id_list);
      try {
        this.pos_offers = this.pos_offers.filter(
          (offer) => !offers_id_list.includes(offer.row_id)
        );
      } catch (error) {
        evntBus.emit('show_mesage', {
          text: 'Error removing offers',
          color: 'error'
        });
      }
    },
    handelOffers() {
      console.log('handelOffers called');
      try {
        const applyedOffers = this.pos_offers.filter(
          (offer) => offer.offer_applied
        );
        evntBus.emit('update_invoice_offers', applyedOffers);
      } catch (error) {
        evntBus.emit('show_mesage', {
          text: 'Error processing offers',
          color: 'error'
        });
      }
    },
    handleNewLine(str) {
      console.log('handleNewLine called with str:', str);
      try {
        if (str) {
          return str.replace(/(?:\r\n|\r|\n)/g, '<br />');
        } else {
          return '';
        }
      } catch (error) {
        evntBus.emit('show_mesage', {
          text: 'Error processing text',
          color: 'error'
        });
        return '';
      }
    },
    get_give_items(offer) {
      console.log('get_give_items called with offer:', offer);
      try {
        if (offer.apply_type == 'Item Code') {
          return [offer.apply_item_code];
        } else if (offer.apply_type == 'Item Group') {
          const items = this.allItems;
          let filterd_items = [];
          const filterd_items_1 = items.filter(
            (item) => item.item_group == offer.apply_item_group
          );
          if (offer.less_then > 0) {
            filterd_items = filterd_items_1.filter(
              (item) => item.rate < offer.less_then
            );
          } else {
            filterd_items = filterd_items_1;
          }
          return filterd_items;
        } else {
          return [];
        }
      } catch (error) {
        evntBus.emit('show_mesage', {
          text: 'Error getting free items',
          color: 'error'
        });
        return [];
      }
    },
    updateCounters() {
      console.log('updateCounters called');
      try {
        evntBus.emit('update_offers_counters', {
          offersCount: this.offersCount,
          appliedOffersCount: this.appliedOffersCount,
        });
      } catch (error) {
        evntBus.emit('show_mesage', {
          text: 'Error updating counters',
          color: 'error'
        });
      }
    },
    updatePosCoupuns() {
      console.log('updatePosCoupuns called');
      try {
        const applyedOffers = this.pos_offers.filter(
          (offer) => offer.offer_applied && offer.coupon_based
        );
        evntBus.emit('update_pos_coupons', applyedOffers);
      } catch (error) {
        evntBus.emit('show_mesage', {
          text: 'Error updating coupons',
          color: 'error'
        });
      }
    }
  },

  // ===== SECTION 6: WATCH =====
  watch: {
    pos_offers: {
      deep: true,
      handler(pos_offers) {
        this.handelOffers();
        this.updateCounters();
        this.updatePosCoupuns();
      }
    }
  },

  // ===== SECTION 7: CREATED =====
  created: function () {
    try {
      this.$nextTick(function () {
        evntBus.on('register_pos_profile', (data) => {
          this.pos_profile = data.pos_profile;
        });
      });
      evntBus.on('update_customer', (customer) => {
        if (this.customer != customer) {
          this.offers = [];
        }
      });
      evntBus.on('update_pos_offers', (data) => {
        this.updatePosOffers(data);
      });
      evntBus.on('update_discount_percentage_offer_name', (data) => {
        this.discount_percentage_offer_name = data.value;
      });
      evntBus.on('set_all_items', (data) => {
        this.allItems = data;
      });
    } catch (error) {
      evntBus.emit('show_mesage', {
        text: 'Error initializing offers',
        color: 'error'
      });
    }
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