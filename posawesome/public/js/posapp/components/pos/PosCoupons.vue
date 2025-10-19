<template>
  <div>
    <v-card
      class="selection mx-auto grey lighten-5"
      style="max-height: 80vh; height: 80vh"
    >
      <v-card-title>
        <v-row no-gutters align="center" justify="center">
          <v-col cols="6">
            <span class="text-h6 primary--text">Coupons</span>
          </v-col>
          <v-col cols="4">
            <v-text-field
              dense
              outlined
              color="primary"
              label="Coupons"
              background-color="white"
              hide-details
              v-model="new_coupon"
              class="mr-4"
            ></v-text-field>
          </v-col>
          <v-col cols="2">
            <v-btn
              class="pa-1"
              color="success"
              dark
              @click="add_coupon(new_coupon)"
              >Add</v-btn
            >
          </v-col>
        </v-row>
      </v-card-title>
      <div class="my-0 py-0 overflow-y-auto" style="max-height: 75vh">
        <template @mouseover="style = 'cursor: pointer'">
          <v-data-table
            :headers="items_headers"
            :items="posa_coupons"
            :single-expand="singleExpand"
            :expanded.sync="expanded"
            item-key="coupon"
            class="elevation-1"
            :items-per-page="itemsPerPage"
            hide-default-footer
          >
            <template v-slot:item.applied="{ item }">
              <v-checkbox
                v-model="item.applied"
                disabled
              ></v-checkbox>
            </template>
          </v-data-table>
        </template>
      </div>
    </v-card>

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
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script>
// IMPORTS & CONSTANTS
import { evntBus } from '../../bus';
import { API_MAP } from "../../api_mapper.js";

const EVENT_NAMES = {
  SHOW_COUPONS: 'show_coupons',
  SHOW_MESSAGE: 'show_mesage',
  UPDATE_INVOICE_COUPONS: 'update_invoice_coupons',
  UPDATE_COUPONS_COUNTERS: 'update_coupons_counters',
  REGISTER_POS_PROFILE: 'register_pos_profile',
  UPDATE_CUSTOMER: 'update_customer',
  UPDATE_POS_COUPONS: 'update_pos_coupons',
  SET_POS_COUPONS: 'set_pos_coupons',
};

const COUPON_TYPE = {
  PROMOTIONAL: 'Promotional',
};

const TABLE_HEADERS = [
  { title: 'Coupon', key: 'coupon_code', align: 'start' },
  { title: 'Type', key: 'type', align: 'start' },
  { title: 'POS Offer', key: 'pos_offer', align: 'start' },
  { title: 'Applied', key: 'applied', align: 'start' },
];

export default {
  name: 'PosCoupons',
  
  data() {
    return {
      loading: false,
      pos_profile: null,
      customer: '',
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
      evntBus.emit(EVENT_NAMES.SHOW_COUPONS, 'false');
    },

    showMessage(text, color) {
      evntBus.emit(EVENT_NAMES.SHOW_MESSAGE, { text, color });
    },

    add_coupon(coupon_code) {
      if (!this.customer || !coupon_code) {
        this.showMessage('Customer or coupon code is missing', 'error');
        return;
      }

      if (this.posa_coupons.some((el) => el.coupon_code === coupon_code)) {
        this.showMessage('This coupon is already used!', 'error');
        return;
      }

      frappe.call({
        method: API_MAP.POS_OFFER.GET_COUPON,
        args: {
          coupon: coupon_code,
          customer: this.customer,
          company: this.pos_profile.company,
        },
        callback: (r) => {
          if (r.message) {
            const { msg, coupon } = r.message;
            if (msg !== 'Apply' || !coupon) {
              this.showMessage(msg, 'error');
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
            this.showMessage('Failed to get coupon from server', 'error');
          }
        },
      });
    },

    setActiveGiftCoupons() {
      if (!this.customer?.trim()) return;

      frappe.call({
        method: API_MAP.POS_OFFER.GET_CUSTOMER_COUPONS,
        args: {
          customer_id: this.customer,
          company: this.pos_profile.company,
        },
        callback: (r) => {
          if (r.message) {
            r.message.forEach((coupon_code) => this.add_coupon(coupon_code));
          } else {
            this.showMessage('Failed to get active gift coupons', 'error');
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
};
</script>
