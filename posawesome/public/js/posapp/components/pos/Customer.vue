<template>
  <!-- ===== TEMPLATE SECTION 1: MAIN CONTAINER ===== -->
  <div>
    {{ console.log({template: "main container", result: "main container rendered"}) }}
    <v-autocomplete
      density="compact"
      variant="outlined"
      color="primary"
      :label="'العميل'"
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
      :style="{ backgroundColor: quick_return ? '#EF9A9A' : 'white' }"
    >
      <template v-slot:item="{ props, item }">
        <v-list-item v-bind="props">
          <v-list-item-title class="primary--text subtitle-1" v-html="item.customer_name"></v-list-item-title>
          <v-list-item-subtitle v-if="item.customer_name != item.name" v-html="'معرف العميل: ' + item.name"></v-list-item-subtitle>
          <v-list-item-subtitle v-if="item.tax_id" v-html="'معرف الضريبة: ' + item.tax_id"></v-list-item-subtitle>
          <v-list-item-subtitle v-if="item.email_id" v-html="'البريد الإلكتروني: ' + item.email_id"></v-list-item-subtitle>
          <v-list-item-subtitle v-if="item.mobile_no" v-html="'رقم الجوال: ' + item.mobile_no"></v-list-item-subtitle>
          <v-list-item-subtitle v-if="item.primary_address" v-html="'العنوان الرئيسي: ' + item.primary_address"></v-list-item-subtitle>
        </v-list-item>
      </template>
    </v-autocomplete>

    <div class="mb-8">
      <UpdateCustomer />
    </div>
  </div>
</template>

<script>
// ===== SECTION 1: IMPORTS =====
console.log({script: "imports start"});
import { evntBus } from '../../bus';
import UpdateCustomer from './UpdateCustomer.vue';
console.log({script: "imports end", result: "2 imports loaded successfully"});
// ===== SECTION 2: EXPORT DEFAULT =====
export default {
  // ===== SECTION 3: DATA =====
  data: () => {
    console.log({script: "data start"});
    return {
    pos_profile: '',
    customers: [],
    customer: '',
    readonly: false,
    customer_info: {},
    quick_return: false,
    };
    console.log({script: "data end", result: "data object initialized successfully"});
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
        // تفعيل Local Storage ثابت في الكود
        // posa_local_storage مفعل ثابت
        if (localStorage.customer_storage) {
          vm.customers = JSON.parse(localStorage.getItem('customer_storage'));
        }
        frappe.call({
          method: 'posawesome.posawesome.api.customer.get_customer_names',
          args: {
            pos_profile: this.pos_profile.pos_profile,
          },
          callback: function (r) {
            if (r.message) {
              vm.customers = r.message;
              // تفعيل Local Storage ثابت في الكود
              // posa_local_storage مفعل ثابت
              localStorage.setItem('customer_storage', '');
              localStorage.setItem(
                'customer_storage',
                JSON.stringify(r.message)
              );
            }
          },
          error: function (err) {
            evntBus.emit('show_mesage', {
              message: 'فشل في جلب العملاء',
              color: 'error',
            });
          }
        });
      } catch (error) {
        evntBus.emit('show_mesage', {
          message: 'حدث خطأ غير متوقع أثناء جلب العملاء',
          color: 'error',
        });
      }
    },
    new_customer() {
      try {
        evntBus.emit('open_update_customer', null);
      } catch (error) {
        evntBus.emit('show_mesage', {
          message: 'خطأ في فتح نموذج العميل الجديد',
          color: 'error',
        });
      }
    },
    edit_customer() {
      try {
        evntBus.emit('open_update_customer', this.customer_info);
      } catch (error) {
        evntBus.emit('show_mesage', {
          message: 'خطأ في فتح نموذج تعديل العميل',
          color: 'error',
        });
      }
    },
    customFilter(item, queryText, itemText) {
      try {
        // custom filter for customer search
        const textOne = item.customer_name
          ? item.customer_name.toLowerCase()
          : '';
        const textTwo = item.tax_id ? item.tax_id.toLowerCase() : '';
        const textThree = item.email_id ? item.email_id.toLowerCase() : '';
        const textFour = item.mobile_no ? item.mobile_no.toLowerCase() : '';
        const textFifth = item.name.toLowerCase();
        const searchText = queryText.toLowerCase();
        const result = (
          textOne.indexOf(searchText) > -1 ||
          textTwo.indexOf(searchText) > -1 ||
          textThree.indexOf(searchText) > -1 ||
          textFour.indexOf(searchText) > -1 ||
          textFifth.indexOf(searchText) > -1
        );
        return result;
      } catch (error) {
        return false;
      }
    },
  },

  computed: {},

  created: function () {
    this.$nextTick(function () {
      try {
      
        evntBus.on('toggle_quick_return', (value) => {
          this.quick_return = value;
        });
      
        evntBus.on('register_pos_profile', (pos_profile) => {
          this.pos_profile = pos_profile;
          this.get_customer_names();
        });
      
        evntBus.on('payments_register_pos_profile', (pos_profile) => {
          this.pos_profile = pos_profile;
          this.get_customer_names();
        });
      
        evntBus.on('set_customer', (customer) => {
          this.customer = customer;
        });
      
        evntBus.on('add_customer_to_list', (customer) => {
          this.customers.push(customer);
        });
      
        evntBus.on('set_customer_readonly', (value) => {
          this.readonly = value;
        });
      
        evntBus.on('set_customer_info_to_edit', (data) => {
          this.customer_info = data;
        });
      
        evntBus.on('fetch_customer_details', () => {
          this.get_customer_names();
        });
      
      } catch (error) {
        evntBus.emit('show_mesage', {
          message: 'حدث خطأ أثناء تهيئة المكون',
          color: 'error',
        });
      }
    });
  },
  // ===== SECTION 6: WATCH =====
  watch: {
    customer() {
      evntBus.emit('update_customer', this.customer);
    },
  }
};
</script>
