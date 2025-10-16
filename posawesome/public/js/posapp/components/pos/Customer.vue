<template>
  <!-- ===== TEMPLATE SECTION 1: MAIN CONTAINER ===== -->
  <div>
    <v-autocomplete
      density="compact"
      variant="outlined"
      color="primary"
      :label="'Customer'"
      v-model="customer"
      :items="customers"
      item-title="customer_name"
      item-value="name"
      :filter="customFilter"
      :disabled="readonly"
      append-icon="mdi-plus"
      @click:append="new_customer"
      prepend-inner-icon="mdi-account-edit"
      @click:prepend-inner="edit_customer"
      @focus="load_all_customers"
      :style="{ backgroundColor: quick_return ? '#EF9A9A' : 'white' }"
    >
      <template v-slot:item="{ props, item }">
        <v-list-item v-bind="props">
          <v-list-item-title
            class="primary--text subtitle-1"
            v-html="item.customer_name"
          ></v-list-item-title>
          <v-list-item-subtitle
            v-if="item.customer_name != item.name"
            v-html="'Customer ID: ' + item.name"
          ></v-list-item-subtitle>
          <v-list-item-subtitle
            v-if="item.tax_id"
            v-html="'Tax ID: ' + item.tax_id"
          ></v-list-item-subtitle>
          <v-list-item-subtitle
            v-if="item.email_id"
            v-html="'Email: ' + item.email_id"
          ></v-list-item-subtitle>
          <v-list-item-subtitle
            v-if="item.mobile_no"
            v-html="'Mobile: ' + item.mobile_no"
          ></v-list-item-subtitle>
          <v-list-item-subtitle
            v-if="item.primary_address"
            v-html="'Primary Address: ' + item.primary_address"
          ></v-list-item-subtitle>
        </v-list-item>
      </template>
    </v-autocomplete>

    <div class="mb-2">
      <UpdateCustomer />
    </div>
  </div>
</template>

<script>
// ===== SECTION 1: IMPORTS =====
import { evntBus } from "../../bus";
import UpdateCustomer from "./UpdateCustomer.vue";
// ===== SECTION 2: EXPORT DEFAULT =====
export default {
  // ===== SECTION 3: DATA =====
  data: () => {
    return {
      pos_profile: "",
      customers: [],
      customer: "",
      readonly: false,
      customer_info: {},
      quick_return: false,
    };
  },
  // ===== SECTION 4: COMPONENTS =====
  components: {
    UpdateCustomer,
  },
  // ===== SECTION 5: METHODS =====
  methods: {
    get_customer_names() {
      const vm = this;
      try {
        if (this.customers.length > 0) {
          return;
        }
        // Load only default customer initially
        this.load_default_customer();
      } catch (error) {
        console.log("Customer.vue(get_customer_names): Error", error);
        evntBus.emit("show_mesage", {
          message: "An unexpected error occurred while fetching customers",
          color: "error",
        });
      }
    },
    load_default_customer() {
      if (!this.pos_profile) {
        evntBus.emit("show_mesage", {
          message: "POS Profile not loaded",
          color: "error",
        });
        return;
      }

      // Use the already loaded POS Profile data
      const default_customer = this.pos_profile.pos_profile?.customer;
      if (default_customer) {
        console.log(
          "Customer.vue(load_default_customer): Loaded",
          default_customer
        );
        this.customer = default_customer;
        evntBus.emit("update_customer", default_customer);
      } else {
        evntBus.emit("show_mesage", {
          message: "Default customer not defined in POS Profile",
          color: "error",
        });
      }
    },
    load_all_customers() {
      frappe.call({
        method: "posawesome.posawesome.api.customer.customer_names.get_customer_names",
        args: {
          pos_profile: this.pos_profile.pos_profile,
        },
        callback: (r) => {
          if (r.message) {
            console.log(
              "Customer.vue(load_all_customers): Loaded",
              r.message.length
            );
            this.customers = r.message;
          }
        },
        error: (err) => {
          console.log("Customer.vue(load_all_customers): Error", err);
          evntBus.emit("show_mesage", {
            message: "Failed to fetch customers",
            color: "error",
          });
        },
      });
    },
    new_customer() {
      try {
        evntBus.emit("open_update_customer", null);
      } catch (error) {
        console.log("Customer.vue(new_customer): Error", error);
        evntBus.emit("show_mesage", {
          message: "Error opening new customer form",
          color: "error",
        });
      }
    },
    edit_customer() {
      try {
        evntBus.emit("open_update_customer", this.customer_info);
      } catch (error) {
        console.log("Customer.vue(edit_customer): Error", error);
        evntBus.emit("show_mesage", {
          message: "Error opening customer edit form",
          color: "error",
        });
      }
    },
    customFilter(item, queryText, itemText) {
      try {
        // custom filter for customer search
        const textOne = item.customer_name
          ? item.customer_name.toLowerCase()
          : "";
        const textTwo = item.tax_id ? item.tax_id.toLowerCase() : "";
        const textThree = item.email_id ? item.email_id.toLowerCase() : "";
        const textFour = item.mobile_no ? item.mobile_no.toLowerCase() : "";
        const textFifth = item.name.toLowerCase();
        const searchText = queryText.toLowerCase();
        const result =
          textOne.indexOf(searchText) > -1 ||
          textTwo.indexOf(searchText) > -1 ||
          textThree.indexOf(searchText) > -1 ||
          textFour.indexOf(searchText) > -1 ||
          textFifth.indexOf(searchText) > -1;
        return result;
      } catch (error) {
        console.log("Customer.vue(customFilter): Error", error);
        return false;
      }
    },
  },

  computed: {},

  created: function () {
    this.$nextTick(function () {
      try {
        evntBus.on("toggle_quick_return", (value) => {
          this.quick_return = value;
        });

        evntBus.on("register_pos_profile", (pos_profile) => {
          console.log(
            "Customer.vue(register_pos_profile): Registered",
            pos_profile?.pos_profile?.name
          );
          this.pos_profile = pos_profile;
          this.get_customer_names();
        });

        evntBus.on("payments_register_pos_profile", (pos_profile) => {
          this.pos_profile = pos_profile;
          this.get_customer_names();
        });

        evntBus.on("set_customer", (customer) => {
          console.log("Customer.vue(set_customer): Set", customer);
          this.customer = customer;
        });

        evntBus.on("add_customer_to_list", (customer) => {
          this.customers.push(customer);
        });

        evntBus.on("set_customer_readonly", (value) => {
          this.readonly = value;
        });

        evntBus.on("set_customer_info_to_edit", (data) => {
          this.customer_info = data;
        });

        evntBus.on("fetch_customer_details", () => {
          this.get_customer_names();
        });

        // Load all customers when dropdown is opened
        evntBus.on("customer_dropdown_opened", () => {
          this.load_all_customers();
        });
      } catch (error) {
        console.log("Customer.vue(created): Error", error);
        evntBus.emit("show_mesage", {
          message: "An error occurred during component initialization",
          color: "error",
        });
      }
    });
  },
  // ===== SECTION 6: WATCH =====
  watch: {
    customer() {
      console.log("Customer.vue(customer): Changed", this.customer);
      evntBus.emit("update_customer", this.customer);
    },
  },
};
</script>
