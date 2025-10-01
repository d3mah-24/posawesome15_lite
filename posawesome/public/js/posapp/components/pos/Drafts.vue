<template>
  <!-- ===== TEMPLATE SECTION 1: MAIN CONTAINER ===== -->
  <v-row justify="center">
    {{ console.log({template: "main container", result: "main container rendered"}) }}
    <v-dialog v-model="draftsDialog" max-width="900px">
      <v-card>
        <v-card-title>
          <span class="headline primary--text">اختيار الفواتير المحفوظة</span>
        </v-card-title>
        <v-card-text class="pa-0">
          <v-container>
            <v-row no-gutters>
              <v-col cols="12" class="pa-1">
                <v-data-table
                  :headers="headers"
                  :items="dialog_data"
                  item-value="name"
                  class="elevation-1"
                  show-select
                  v-model="selected"
                  single-select
                >
                  <template v-slot:[`item.posting_time`]="{ item }">
                    {{ item.posting_time.split('.')[0] }}
                  </template>
                  <template v-slot:[`item.grand_total`]="{ item }">
                    {{ currencySymbol(item.currency) }}
                    {{ formatCurrency(item.grand_total) }}
                  </template>
                </v-data-table>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_dialog">إغلاق</v-btn>
          <v-btn color="success" dark @click="submit_dialog">اختيار</v-btn>
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
  // props: ["draftsDialog"],
  mixins: [format],
  // ===== SECTION 3: DATA =====
  data: () => {
    console.log({script: "data start"});
    return {
      draftsDialog: false,
      singleSelect: true,
      selected: [],
      dialog_data: {},
      headers: [
        {
          title: 'العميل',
          key: 'customer_name',
          align: 'start',
          sortable: true,
        },
        {
          title: 'التاريخ',
          align: 'start',
          sortable: true,
          key: 'posting_date',
        },
        {
          title: 'الوقت',
          align: 'start',
          sortable: true,
          key: 'posting_time',
        },
        {
          title: 'رقم الفاتورة',
          key: 'name',
          align: 'start',
          sortable: true,
        },
        {
          title: 'المبلغ',
          key: 'grand_total',
          align: 'end',
          sortable: false,
        },
      ]
    };
  },
  // ===== SECTION 4: WATCH =====
  watch: {},
  // ===== SECTION 5: METHODS =====
  methods: {
    close_dialog() {
      this.draftsDialog = false;
    },

    submit_dialog() {
      var me = this;
      if (this.selected.length == 1) {
        $.each(this.dialog_data || [], function(i,v){
          if(v.name == me.selected[0]){
            evntBus.emit('load_invoice', v);
            me.draftsDialog = false;
          }
        });
      }
      else{
        evntBus.emit("show_mesage", {
          text: "يرجى اختيار فاتورة واحدة فقط",
          color: "error",
        });
      }
    },
  },
  // ===== SECTION 6: LIFECYCLE HOOKS =====
  created: function () {
    evntBus.on('open_drafts', (data) => {
      this.draftsDialog = true;
      this.dialog_data = data;
    });
  }
};
</script>