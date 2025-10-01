<template>
  <v-row justify="center">
    <v-dialog
      v-model="customerDialog"
      max-width="600px"
      @click:outside="clear_customer"
    >
      <v-card>
        <v-card-title>
          <span v-if="customer_id" class="headline primary--text">تحديث بيانات العميل</span>
          <span v-else class="headline primary--text">تسجيل عميل جديد</span>
        </v-card-title>
        <v-card-text class="pa-0">
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  dense
                  color="primary"
                  label="اسم العميل *"
                  background-color="white"
                  hide-details
                  v-model="customer_name"
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  dense
                  color="primary"
                  label="الرقم الضريبي"
                  background-color="white"
                  hide-details
                  v-model="tax_id"
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  dense
                  color="primary"
                  label="رقم الجوال"
                  background-color="white"
                  hide-details
                  v-model="mobile_no"
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  dense
                  color="primary"
                  label="البريد الإلكتروني"
                  background-color="white"
                  hide-details
                  v-model="email_id"
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-select
                  dense
                  label="الجنس"
                  :items="genders"
                  v-model="gender"
                ></v-select>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  dense
                  color="primary"
                  label="كود الإحالة"
                  background-color="white"
                  hide-details
                  v-model="referral_code"
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="birthday"
                  label="تاريخ الميلاد"
                  readonly
                  dense
                  clearable
                  hide-details
                  color="primary"
                  prepend-inner-icon="mdi-calendar"
                  @click="birthday_menu = true"
                ></v-text-field>
                
                <v-dialog
                  v-model="birthday_menu"
                  max-width="400px"
                >
                  <v-date-picker
                    v-model="birthday"
                    color="primary"
                    scrollable
                    :max="frappe.datetime.now_date()"
                    @input="birthday_menu = false"
                  >
                  </v-date-picker>
                </v-dialog>
              </v-col>
              <v-col cols="6">
                <v-autocomplete
                  clearable
                  dense
                  auto-select-first
                  color="primary"
                  label="مجموعة العملاء *"
                  v-model="group"
                  :items="groups"
                  background-color="white"
                  no-data-text="لم يتم العثور على المجموعة"
                  hide-details
                  required
                ></v-autocomplete>
              </v-col>
              <v-col cols="6">
                <v-autocomplete
                  clearable
                  dense
                  auto-select-first
                  color="primary"
                  label="المنطقة *"
                  v-model="territory"
                  :items="territorys"
                  background-color="white"
                  no-data-text="لم يتم العثور على المنطقة"
                  hide-details
                  required
                ></v-autocomplete>
              </v-col>
              <v-col cols="6" v-if="loyalty_program">
                <v-text-field
                  v-model="loyalty_program"
                  label="برنامج الولاء"
                  dense
                  readonly
                  hide-details
                ></v-text-field>
              </v-col>
              <v-col cols="6" v-if="loyalty_points">
                <v-text-field
                  v-model="loyalty_points"
                  label="نقاط الولاء"
                  dense
                  readonly
                  hide-details
                ></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_dialog">إغلاق</v-btn>
          <v-btn color="success" dark @click="submit_dialog">{{ customer_id ? 'تحديث بيانات العميل' : 'تسجيل العميل' }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import { evntBus } from '../../bus';
export default {
  data: () => ({
    customerDialog: false,
    pos_profile: '',
    customer_id: '',
    customer_name: '',
    tax_id: '',
    mobile_no: '',
    email_id: '',
    referral_code: '',
    birthday: null,
    birthday_menu: false,
    group: '',
    groups: [],
    territory: '',
    territorys: [],
    genders: [],
    customer_type: 'Individual',
    gender: '',
    loyalty_points: null,
    loyalty_program: null,
  }),
  watch: {},
  methods: {
    close_dialog() {
      this.customerDialog = false;
      this.clear_customer();
    },
    clear_customer() {
      this.customer_name = '';
      this.tax_id = '';
      this.mobile_no = '';
      this.email_id = '';
      this.referral_code = '';
      this.birthday = '';
      this.group = frappe.defaults.get_user_default('Customer Group');
      this.territory = frappe.defaults.get_user_default('Territory');
      this.customer_id = '';
      this.customer_type = 'Individual';
      this.gender = '';
      this.loyalty_points = null;
      this.loyalty_program = null;
    },
    getCustomerGroups() {
      if (this.groups.length > 0) return;
      const vm = this;
      frappe.db
        .get_list('Customer Group', {
          fields: ['name'],
          filters: { is_group: 0 },
          limit: 1000,
          order_by: 'name',
        })
        .then((data) => {
          if (data.length > 0) {
            data.forEach((el) => {
              vm.groups.push(el.name);
            });
          }
        })
        .catch((err) => {
          evntBus.emit('show_mesage', {
            text: 'خطأ في تحميل مجموعات العملاء',
            color: 'error',
          });
        });
    },
    getCustomerTerritorys() {
      if (this.territorys.length > 0) return;
      const vm = this;
      frappe.db
        .get_list('Territory', {
          fields: ['name'],
          filters: { is_group: 0 },
          limit: 5000,
          order_by: 'name',
        })
        .then((data) => {
          if (data.length > 0) {
            data.forEach((el) => {
              vm.territorys.push(el.name);
            });
          }
        })
        .catch((err) => {
          evntBus.emit('show_mesage', {
            text: 'خطأ في تحميل المناطق',
            color: 'error',
          });
        });
    },
    getGenders() {
      const vm = this;
      frappe.db
        .get_list('Gender', {
          fields: ['name'],
          page_length: 10,
        })
        .then((data) => {
          if (data.length > 0) {
            data.forEach((el) => {
              vm.genders.push(el.name);
            });
          }
        })
        .catch((err) => {
          evntBus.emit('show_mesage', {
            text: 'خطأ في تحميل الجنس',
            color: 'error',
          });
        });
    },
    submit_dialog() {
      // validate if all required fields are filled
      if (!this.customer_name) {
        evntBus.emit('show_mesage', {
          text: 'اسم العميل مطلوب.',
          color: 'error',
        });
        return;
      }
      if (!this.group) {
        evntBus.emit('show_mesage', {
          text: 'اسم مجموعة العملاء مطلوب.',
          color: 'error',
        });
        return;
      }
      if (!this.territory) {
        evntBus.emit('show_mesage', {
          text: 'اسم المنطقة مطلوب.',
          color: 'error',
        });
        return;
      }
      if (this.customer_name) {
        const vm = this;
        const args = {
          customer_id: this.customer_id,
          customer_name: this.customer_name,
          company: this.pos_profile.company,
          tax_id: this.tax_id,
          mobile_no: this.mobile_no,
          email_id: this.email_id,
          referral_code: this.referral_code,
          birthday: this.birthday,
          customer_group: this.group,
          territory: this.territory,
          customer_type: this.customer_type,
          gender: this.gender,
          method: this.customer_id ? 'update' : 'create',
          pos_profile_doc: this.pos_profile,
        };
        frappe.call({
          method: 'posawesome.posawesome.api.customer.create_customer',
          args: args,
          callback: (r) => {
            if (!r.exc && r.message.name) {
              let text = 'تم إنشاء العميل بنجاح.';
              if (vm.customer_id) {
                text = 'تم تحديث بيانات العميل بنجاح.';
              }
              evntBus.emit('show_mesage', {
                text: text,
                color: 'success',
              });
              args.name = r.message.name;
              frappe.utils.play_sound('submit');
              // إضافة العميل إلى القائمة فقط عند الإنشاء
              if (!vm.customer_id) {
                evntBus.emit('add_customer_to_list', args);
              }
              // لا نرسل set_customer عند التحديث لتجنب إعادة كتابة اسم العميل
              if (!vm.customer_id) {
                evntBus.emit('set_customer', r.message.name);
              }
              // لا نعيد جلب قائمة العملاء عند التحديث لتجنب التكرار
              if (!vm.customer_id) {
                evntBus.emit('fetch_customer_details');
              }
              this.close_dialog();
            } else {
              frappe.utils.play_sound('error');
              evntBus.emit('show_mesage', {
                text: 'فشل في إنشاء العميل.',
                color: 'error',
              });
            }
          },
        });
        this.customerDialog = false;
      }
    },
  },
  created: function () {
    evntBus.on('open_update_customer', (data) => {
      this.customerDialog = true;
      if (data) {
        this.customer_name = data.customer_name;
        this.customer_id = data.name;
        this.tax_id = data.tax_id;
        this.mobile_no = data.mobile_no;
        this.email_id = data.email_id;
        this.referral_code = data.referral_code;
        this.birthday = data.birthday;
        this.group = data.customer_group;
        this.territory = data.territory;
        this.loyalty_points = data.loyalty_points;
        this.loyalty_program = data.loyalty_program;
        this.gender = data.gender;
      }
    });
    evntBus.on('register_pos_profile', (data) => {
      this.pos_profile = data.pos_profile;
    });
    evntBus.on('payments_register_pos_profile', (data) => {
      this.pos_profile = data.pos_profile;
    });
    this.getCustomerGroups();
    this.getCustomerTerritorys();
    this.getGenders();
    // set default values for customer group and territory from user defaults
    this.group = frappe.defaults.get_user_default('Customer Group');
    this.territory = frappe.defaults.get_user_default('Territory');
  },
};
</script>
