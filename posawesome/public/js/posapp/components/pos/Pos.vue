<template>
  <!-- ===== TEMPLATE SECTION 1: MAIN CONTAINER ===== -->
  <div fluid class="mt-1">
    <ClosingDialog></ClosingDialog>
    <Drafts></Drafts>
    <Returns></Returns>
    <NewAddress></NewAddress>
    <OpeningDialog v-if="dialog" :dialog="dialog"></OpeningDialog>
    <v-row v-show="!dialog">
      <v-col
        v-show="!payment && !offers && !coupons"
        xl="6"
        lg="6"
        md="6"
        sm="6"
        cols="12"
        class="pos pr-0"
      >
        <ItemsSelector></ItemsSelector>
      </v-col>
      <v-col
        v-show="offers"
        xl="6"
        lg="6"
        md="6"
        sm="6"
        cols="12"
        class="pos pr-0"
      >
        <PosOffers></PosOffers>
      </v-col>
      <v-col
        v-show="coupons"
        xl="6"
        lg="6"
        md="6"
        sm="6"
        cols="12"
        class="pos pr-0"
      >
        <PosCoupons></PosCoupons>
      </v-col>
      <v-col
        v-show="payment"
        xl="6"
        lg="6"
        md="6"
        sm="6"
        cols="12"
        class="pos pr-0"
      >
        <Payments ref="payments" @request-print="onPrintRequest"></Payments>
      </v-col>

      <v-col xl="6" lg="6" md="6" sm="6" cols="12" class="pos">
        <Invoice></Invoice>
      </v-col>
    </v-row>
  </div>
</template>

<script>
// ===== SECTION 1: IMPORTS =====
import { evntBus } from '../../bus';
import ItemsSelector from './ItemsSelector.vue';
import Invoice from './Invoice.vue';
import OpeningDialog from './OpeningDialog.vue';
import Payments from './Payments.vue';
import PosOffers from './PosOffers.vue';
import PosCoupons from './PosCoupons.vue';
import Drafts from './Drafts.vue';
import ClosingDialog from './ClosingDialog.vue';
import NewAddress from './NewAddress.vue';
import Returns from './Returns.vue';

// ===== SECTION 2: EXPORT DEFAULT =====
export default {
  // ===== SECTION 3: DATA =====
  data: function () {
    return {
      dialog: false,
      pos_profile: '',
      pos_opening_shift: '',
      payment: false,
      offers: false,
      coupons: false,
    };
  },
  // ===== SECTION 4: COMPONENTS =====
  components: {
    ItemsSelector,
    Invoice,
    OpeningDialog,
    Payments,
    Drafts,
    ClosingDialog,
    Returns,
    PosOffers,
    PosCoupons,
    NewAddress,
  },
  // ===== SECTION 5: METHODS =====
  methods: {
    check_opening_entry() {
      return frappe
        .call('posawesome.posawesome.api.pos_opening_shift.get_current_shift_name')
        .then((r) => {
          if (r.message.success && r.message.data) {
            // وردية مفتوحة موجودة - احصل على بيانات البروفايل الكاملة
            this.get_full_profile_data(r.message.data.pos_profile);
          } else {
            evntBus.emit('show_mesage', {
              text: r.message.message || 'No opening shift found, a new opening entry will be created.',
              color: 'info'
            });
            this.create_opening_voucher();
          }
        });
    },
    
    get_full_profile_data(pos_profile_name) {
      // احصل على بيانات البروفايل الكاملة
      frappe.call({
        method: 'frappe.client.get',
        args: {
          doctype: 'POS Profile',
          name: pos_profile_name
        }
      }).then((profile_r) => {
        if (profile_r.message) {
          const pos_profile = profile_r.message;
          
          // احصل على بيانات الوردية المفتوحة
          frappe.call({
            method: 'posawesome.posawesome.api.pos_opening_shift.get_current_shift_name'
          }).then((shift_r) => {
            const shift_data = {
              pos_profile: pos_profile,
              pos_opening_shift: shift_r.message.success ? shift_r.message.data : null,
              company: { name: pos_profile.company },
              stock_settings: { allow_negative_stock: 0 }
            };
            
            console.log('[Pos] pos profile loaded', pos_profile.name);
            this.pos_profile = pos_profile;
            this.pos_opening_shift = shift_r.message.success ? shift_r.message.data : null;
            this.get_offers(pos_profile.name);
            evntBus.emit('register_pos_profile', shift_data);
            evntBus.emit('set_company', { name: pos_profile.company });
            // Also emit shift data separately to ensure it reaches Navbar
            evntBus.emit('set_pos_opening_shift', shift_r.message.success ? shift_r.message.data : null);
          });
        }
      });
    },
    create_opening_voucher() {
      console.log('[Pos] creating opening voucher');
      this.dialog = true;
    },
    get_closing_data() {
      return frappe
        .call(
          'posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.make_closing_shift_from_opening',
          {
            opening_shift: this.pos_opening_shift,
          }
        )
        .then((r) => {
          if (r.message) {
            console.log('[Pos] opening closing dialog');
            evntBus.emit('open_ClosingDialog', r.message);
          } else {
            console.log('[Pos] failed to load closing data');
            evntBus.emit('show_mesage', {
              text: 'Failed to load closing data',
              color: 'error'
            });
          }
        });
    },
    submit_closing_pos(data) {
      console.log('[Pos] submitting closing pos');
      frappe
        .call(
          'posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.submit_closing_shift',
          {
            closing_shift: data,
          }
        )
        .then((r) => {
          if (r.message) {
            console.log('[Pos] cashier shift closed successfully');
            evntBus.emit('show_mesage', {
              text: 'Cashier shift closed successfully',
              color: 'success',
            });
            this.check_opening_entry();
          } else {
            evntBus.emit('show_mesage', {
              text: 'Failed to close cashier shift',
              color: 'error'
            });
          }
        });
    },
    get_offers(pos_profile) {
      console.log('[Pos] getting offers for profile', pos_profile);
      return frappe
        .call('posawesome.posawesome.api.pos_offer.get_offers_for_profile', {
          profile: pos_profile,
        })
        .then((r) => {
          if (r.message) {
            console.log('[Pos] offers loaded', r.message.length);
            evntBus.emit('set_offers', r.message);
          } else {
            evntBus.emit('show_mesage', {
              text: 'Failed to load offers',
              color: 'error'
            });
          }
        });
    },
    get_pos_setting() {
      console.log('[Pos] getting pos settings');
      frappe.db.get_doc('POS Settings', undefined).then((doc) => {
        console.log('[Pos] pos settings loaded');
        evntBus.emit('set_pos_settings', doc);
      });
    },
    onPrintRequest() {
      console.log('[Pos] print request received');
      evntBus.emit("request_invoice_print");
    },
  },
  // ===== SECTION 6: LIFECYCLE HOOKS =====
  mounted: function () {
    console.log('[Pos] component mounted');
    this.$nextTick(function () {
      this.check_opening_entry();
      this.get_pos_setting();
      evntBus.on('close_opening_dialog', () => {
        console.log('[Pos] opening dialog closed');
        this.dialog = false;
      });
      evntBus.on('register_pos_data', (data) => {
        this.pos_profile = data.pos_profile;
        this.get_offers(this.pos_profile.name);
        this.pos_opening_shift = data.pos_opening_shift;
        evntBus.emit('register_pos_profile', data);
      });
      evntBus.on('show_payment', (data) => {
        this.payment = true ? data === 'true' : false;
        this.offers = false ? data === 'true' : false;
        this.coupons = false ? data === 'true' : false;
      });
      evntBus.on('show_offers', (data) => {
        this.offers = true ? data === 'true' : false;
        this.payment = false ? data === 'true' : false;
        this.coupons = false ? data === 'true' : false;
      });
      evntBus.on('show_coupons', (data) => {
        this.coupons = true ? data === 'true' : false;
        this.offers = false ? data === 'true' : false;
        this.payment = false ? data === 'true' : false;
      });
      evntBus.on('open_closing_dialog', () => {
        this.get_closing_data();
      });
      evntBus.on('submit_closing_pos', (data) => {
        this.submit_closing_pos(data);
      });
    });
  },
  beforeDestroy() {
    evntBus.$off('close_opening_dialog');
    evntBus.$off('register_pos_data');
    evntBus.$off('LoadPosProfile');
    evntBus.$off('show_offers');
    evntBus.$off('show_coupons');
    evntBus.$off('open_closing_dialog');
    evntBus.$off('submit_closing_pos');
  }
};
</script>

<style scoped></style>