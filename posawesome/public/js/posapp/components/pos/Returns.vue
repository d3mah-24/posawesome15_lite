<template>
  <!-- ===== TEMPLATE SECTION 1: MAIN CONTAINER ===== -->
  <v-row justify="center">
    {{ console.log({template: "main container", result: "main container rendered"}) }}
    <v-dialog v-model="invoicesDialog" max-width="800px" min-width="800px">
      <v-card>
        <v-card-title>
          <span class="headline primary--text">فاتورة مرتجع</span>
        </v-card-title>
        <v-container>
          <v-row class="mb-4">
            <v-text-field
              color="primary"
              :label="'رقم الفاتورة'"
              background-color="white"
              hide-details
              v-model="invoice_name"
              dense
              clearable
              class="mx-4"
              @keydown.enter="search_invoices"
            ></v-text-field>
            <v-btn text class="ml-2" color="primary" dark @click="search_invoices">
              بحث
            </v-btn>
          </v-row>
          <v-row>
            <v-col cols="12" class="pa-1">
              <v-data-table
                :headers="headers"
                :items="dialog_data"
                item-value="name"
                class="elevation-1"
                show-select
                v-model="selected"
                :loading="isLoading"
                loading-text="جاري تحميل الفواتير..."
                no-data-text="لم يتم العثور على فواتير"
              >
                <template v-slot:[`item.grand_total`]="{ item }">
                  {{ currencySymbol(item.currency) }} {{ formatCurrency(item.grand_total) }}
                </template>
              </v-data-table>
            </v-col>
          </v-row>
        </v-container>
        <v-card-actions class="mt-4">
          <v-spacer></v-spacer>
          <v-btn color="error mx-2" dark @click="close_dialog">إغلاق</v-btn>
          <v-btn color="success" dark @click="submit_dialog">
            اختيار
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
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
    invoicesDialog: false,
    selected: [],
    dialog_data: [],
    isLoading: false,
    company: '',
    invoice_name: '',
    pos_profile: null,
    pos_opening_shift: null,
    headers: [
      { title: 'العميل', key: 'customer', align: 'start', sortable: true },
      { title: 'التاريخ', key: 'posting_date', align: 'start', sortable: true },
      { title: 'رقم الفاتورة', key: 'name', align: 'start', sortable: true },
      { title: 'المبلغ', key: 'grand_total', align: 'end', sortable: false }
      ]
    };
    console.log({script: "data end", result: "data object initialized successfully"});
  },
  beforeUnmount() {
    evntBus.off('open_returns');
  },
  methods: {
    close_dialog() {
      this.$nextTick(() => {
        this.invoicesDialog = false;
        this.selected = [];
        this.dialog_data = [];
        this.invoice_name = '';
      });
    },
    search_invoices() {
                // تعيين الشركة من أحدث pos_profile أو pos_opening_shift إذا كان متاحاً
      this.company = this.pos_profile?.company || this.pos_opening_shift?.company || this.company;
      if (!this.company && !this.invoice_name) {
        evntBus.emit('show_mesage', {
          text: 'يرجى إدخال رقم الفاتورة أو اختيار الشركة أولاً',
          color: 'error'
        });
        return;
      }
      this.isLoading = true;
      frappe.call({
        method: 'posawesome.posawesome.api.invoice.search_invoices_for_return',
        args: {
          invoice_name: this.invoice_name,
          company: this.company
        },
        callback: (r) => {
          this.isLoading = false;
          if (r.message && r.message.length > 0) {
            this.dialog_data = r.message.map(item => ({
              name: item.name,
              customer: item.customer,
              posting_date: item.posting_date,
              grand_total: item.grand_total,
              currency: item.currency,
              items: item.items || []
            }));
          } else {
            this.dialog_data = [];
          }
          
          // عرض الرسائل المناسبة بناءً على نتائج البحث
          if (this.dialog_data.length === 0) {
            if (this.invoice_name) {
              evntBus.emit('show_mesage', {
                text: 'لم يتم العثور على فواتير مطابقة للبحث',
                color: 'info'
              });
            } else {
              evntBus.emit('show_mesage', {
                text: 'لا توجد فواتير متاحة للمرتجع في هذه الشركة',
                color: 'info'
              });
            }
          }
        },
        error: (err) => {
          this.isLoading = false;
          evntBus.emit('show_mesage', {
            text: 'فشل في البحث عن الفواتير',
            color: 'error'
          });
        }
      });
    },
    async submit_dialog() {
      if (!this.selected.length || !this.dialog_data.length) {
        evntBus.emit('show_mesage', {
          text: 'يرجى اختيار فاتورة صحيحة',
          color: 'error'
        });
        return;
      }
      const selectedItem = this.dialog_data.find(item => item.name === this.selected[0]);
      if (!selectedItem) {
        evntBus.emit('show_mesage', {
          text: 'الفاتورة المختارة غير موجودة',
          color: 'error'
        });
        return;
      }
      const return_doc = selectedItem;
      // جلب الفاتورة الأصلية من الخادم
      let original_invoice = null;
      try {
        const response = await frappe.call({
          method: 'frappe.client.get',
          args: {
            doctype: "Sales Invoice",
            name: return_doc.name
          }
        });
        original_invoice = response.message;
      } catch (e) {
        evntBus.emit('show_mesage', {
          text: 'فشل في جلب الفاتورة الأصلية',
          color: 'error'
        });
        return;
      }
      if (!original_invoice) {
        evntBus.emit('show_mesage', {
          text: 'الفاتورة الأصلية غير موجودة',
          color: 'error'
        });
        return;
      }
      const original_items = original_invoice.items.map(i => i.item_code);
      const invalid_items = return_doc.items.filter(item => !original_items.includes(item.item_code));
      if (invalid_items.length > 0) {
        evntBus.emit('show_mesage', {
          text: `الأصناف التالية غير موجودة في الفاتورة الأصلية: ${invalid_items.map(i => i.item_code).join(', ')}`,
          color: 'error'
        });
        return;
      }
      // حفظ الكائنات كاملة في المستند
      const invoice_doc = {
        items: return_doc.items.map(item => ({
          ...item,
          qty: item.qty * -1,
          stock_qty: item.stock_qty * -1,
          amount: item.amount * -1
        })),
        is_return: 1,
        company: (this.pos_opening_shift && this.pos_opening_shift.company) || (this.pos_profile && this.pos_profile.company) || '',
        customer: return_doc.customer,
        posa_pos_opening_shift: this.pos_opening_shift?.name,
        pos_opening_shift: this.pos_opening_shift || null, // حفظ الكائن كاملاً
        pos_profile: this.pos_profile || null // حفظ الكائن كاملاً
      };
      evntBus.emit('load_return_invoice', { invoice_doc, return_doc });
      this.invoicesDialog = false;
    }
  },
  created() {
    evntBus.on('open_returns', (data) => {
      this.invoicesDialog = true;
      this.pos_profile = data.pos_profile || null;
      this.pos_opening_shift = data.pos_opening_shift || null;
      // تعيين الشركة من pos_profile أو pos_opening_shift
      this.company = (this.pos_profile && this.pos_profile.company) || (this.pos_opening_shift && this.pos_opening_shift.company) || '';
      this.dialog_data = [];
      this.selected = [];
      // جلب الفواتير الأولية مع الفلترة المناسبة
      this.search_invoices();
    });
  }
};
</script>

<style scoped>
.v-data-table {
  font-size: 0.875rem;
}
</style>