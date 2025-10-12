<template>
  <div class="pos-container">
    <ClosingDialog></ClosingDialog>
    <Returns></Returns>
    <NewAddress></NewAddress>
    <OpeningDialog v-if="dialog" :dialog="dialog"></OpeningDialog>

    <div v-show="!dialog" class="pos-main-wrapper">
      <div class="pos-left-panel">
        <div v-show="!payment && !offers && !coupons" class="panel-content">
          <ItemsSelector></ItemsSelector>
        </div>
        <div v-show="offers" class="panel-content">
          <PosOffers></PosOffers>
        </div>
        <div v-show="coupons" class="panel-content">
          <PosCoupons></PosCoupons>
        </div>
        <div v-show="payment" class="panel-content">
          <Payments ref="payments" @request-print="onPrintRequest"></Payments>
        </div>
      </div>

      <div class="pos-right-panel">
        <div class="panel-content">
          <Invoice></Invoice>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// ===== SECTION 1: IMPORTS =====
import { evntBus } from "../../bus";
import ItemsSelector from "./ItemsSelector.vue";
import Invoice from "./Invoice.vue";
import OpeningDialog from "./OpeningDialog.vue";
import Payments from "./Payments.vue";
import PosOffers from "./PosOffers.vue";
import PosCoupons from "./PosCoupons.vue";
import ClosingDialog from "./ClosingDialog.vue";
import NewAddress from "./NewAddress.vue";
import Returns from "./Returns.vue";

// ===== SECTION 2: EXPORT DEFAULT =====
export default {
  // ===== SECTION 3: DATA =====
  data: function () {
    return {
      dialog: false,
      pos_profile: "",
      pos_opening_shift: "",
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
        .call(
          "posawesome.posawesome.api.pos_opening_shift.get_current_shift_name"
        )
        .then((r) => {
          if (r.message.success && r.message.data) {
            // وردية مفتوحة موجودة - احصل على بيانات البروفايل الكاملة
            this.get_full_profile_data(r.message.data.pos_profile);
          } else {
            evntBus.emit("show_mesage", {
              text:
                r.message.message ||
                "No opening shift found, a new opening entry will be created.",
              color: "info",
            });
            this.create_opening_voucher();
          }
        });
    },

    get_full_profile_data(pos_profile_name) {
      // احصل على بيانات البروفايل الكاملة
      frappe
        .call({
          method: "frappe.client.get",
          args: {
            doctype: "POS Profile",
            name: pos_profile_name,
          },
        })
        .then((profile_r) => {
          if (profile_r.message) {
            const pos_profile = profile_r.message;

            // احصل على بيانات الوردية المفتوحة
            frappe
              .call({
                method:
                  "posawesome.posawesome.api.pos_opening_shift.get_current_shift_name",
              })
              .then((shift_r) => {
                const shift_data = {
                  pos_profile: pos_profile,
                  pos_opening_shift: shift_r.message.success
                    ? shift_r.message.data
                    : null,
                  company: { name: pos_profile.company },
                  stock_settings: { allow_negative_stock: 0 },
                };

                console.log(
                  "Pos.vue(check_opening_entry): Profile loaded",
                  pos_profile.name
                );
                this.pos_profile = pos_profile;
                this.pos_opening_shift = shift_r.message.success
                  ? shift_r.message.data
                  : null;
                this.get_offers(pos_profile.name);
                evntBus.emit("register_pos_profile", shift_data);
                evntBus.emit("set_company", { name: pos_profile.company });
                // Also emit shift data separately to ensure it reaches Navbar
                evntBus.emit(
                  "set_pos_opening_shift",
                  shift_r.message.success ? shift_r.message.data : null
                );
              });
          }
        });
    },
    create_opening_voucher() {
      this.dialog = true;
    },
    get_closing_data() {
      return frappe
        .call(
          "posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.make_closing_shift_from_opening",
          {
            opening_shift: this.pos_opening_shift,
          }
        )
        .then((r) => {
          if (r.message) {
            evntBus.emit("open_ClosingDialog", r.message);
          } else {
            console.log("Pos.vue(get_closing_data): Failed to load");
            evntBus.emit("show_mesage", {
              text: "Failed to load closing data",
              color: "error",
            });
          }
        });
    },
    submit_closing_pos(data) {
      frappe
        .call(
          "posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.submit_closing_shift",
          {
            closing_shift: data,
          }
        )
        .then((r) => {
          if (r.message) {
            console.log("Pos.vue(submit_closing_pos): Success");
            evntBus.emit("show_mesage", {
              text: "Cashier shift closed successfully",
              color: "success",
            });
            this.check_opening_entry();
          } else {
            evntBus.emit("show_mesage", {
              text: "Failed to close cashier shift",
              color: "error",
            });
          }
        });
    },
    get_offers(pos_profile) {
      return frappe
        .call("posawesome.posawesome.api.pos_offer.get_offers_for_profile", {
          profile: pos_profile,
        })
        .then((r) => {
          if (r.message) {
            evntBus.emit("set_offers", r.message);
          } else {
            evntBus.emit("show_mesage", {
              text: "Failed to load offers",
              color: "error",
            });
          }
        });
    },
    get_pos_setting() {
      frappe.db.get_doc("POS Settings", undefined).then((doc) => {
        evntBus.emit("set_pos_settings", doc);
      });
    },
    onPrintRequest() {
      evntBus.emit("request_invoice_print");
    },
  },
  // ===== SECTION 6: LIFECYCLE HOOKS =====
  mounted: function () {
    this.$nextTick(function () {
      this.check_opening_entry();
      this.get_pos_setting();
      evntBus.on("close_opening_dialog", () => {
        this.dialog = false;
      });
      evntBus.on("register_pos_data", (data) => {
        this.pos_profile = data.pos_profile;
        this.get_offers(this.pos_profile.name);
        this.pos_opening_shift = data.pos_opening_shift;
        evntBus.emit("register_pos_profile", data);
      });
      evntBus.on("show_payment", (data) => {
        this.payment = true ? data === "true" : false;
        this.offers = false ? data === "true" : false;
        this.coupons = false ? data === "true" : false;
      });
      evntBus.on("show_offers", (data) => {
        this.offers = true ? data === "true" : false;
        this.payment = false ? data === "true" : false;
        this.coupons = false ? data === "true" : false;
      });
      evntBus.on("show_coupons", (data) => {
        this.coupons = true ? data === "true" : false;
        this.offers = false ? data === "true" : false;
        this.payment = false ? data === "true" : false;
      });
      evntBus.on("open_closing_dialog", () => {
        this.get_closing_data();
      });
      evntBus.on("submit_closing_pos", (data) => {
        this.submit_closing_pos(data);
      });
    });
  },
  beforeDestroy() {
    evntBus.$off("close_opening_dialog");
    evntBus.$off("register_pos_data");
    evntBus.$off("LoadPosProfile");
    evntBus.$off("show_offers");
    evntBus.$off("show_coupons");
    evntBus.$off("open_closing_dialog");
    evntBus.$off("submit_closing_pos");
  },
};
</script>

<style scoped>
/* ===== MAIN CONTAINER ===== */
.pos-container {
  padding: 3px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  min-height: 100vh;
  overflow: visible;
}

/* ===== MAIN WRAPPER - FLEXBOX LAYOUT ===== */
.pos-main-wrapper {
  display: flex;
  gap: 5px;
  min-height: calc(100vh - 130px) !important;
  width: 100%;
  margin-top: 10px;
}

/* ===== LEFT PANEL (Items/Offers/Coupons/Payments) ===== */
.pos-left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  position: relative;
}

/* ===== RIGHT PANEL (Invoice) ===== */
.pos-right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* ===== PANEL CONTENT WRAPPER ===== */
.panel-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.panel-content:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: rgba(25, 118, 210, 0.2);
}

/* ===== NESTED COMPONENT STYLING ===== */
.panel-content > * {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ===== RESPONSIVE DESIGN ===== */
@media (max-width: 1280px) {
  .pos-main-wrapper {
    gap: 3px;
  }

  .panel-content {
    border-radius: 6px;
  }
}

@media (max-width: 1024px) {
  .pos-container {
    padding: 2px;
  }

  .pos-main-wrapper {
    gap: 2px;
    min-height: calc(100vh - 48px);
  }

  .panel-content {
    border-radius: 6px;
  }
}

@media (max-width: 768px) {
  .pos-container {
    padding: 2px;
  }

  .pos-main-wrapper {
    flex-direction: column;
    gap: 3px;
  }

  .pos-left-panel,
  .pos-right-panel {
    flex: 1;
    min-height: 300px;
  }
}

/* ===== SMOOTH TRANSITIONS FOR PANEL SWITCHING ===== */
.pos-left-panel > div {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.25s ease, visibility 0.25s ease;
  pointer-events: none;
}

.pos-left-panel > div[style*="display: none"] {
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}

.pos-left-panel > div:not([style*="display: none"]) {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}

/* ===== LOADING ANIMATION SUPPORT ===== */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.panel-content {
  animation: fadeIn 0.3s ease;
}

/* ===== PROFESSIONAL SCROLLBAR STYLING ===== */
.panel-content ::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.panel-content ::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.panel-content ::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  border-radius: 3px;
  transition: background 0.2s ease;
}

.panel-content ::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
}

/* ===== ENHANCED FOCUS STATES ===== */
.panel-content:focus-within {
  box-shadow: 0 4px 16px rgba(25, 118, 210, 0.2);
  border-color: rgba(25, 118, 210, 0.3);
}
</style>
