# POSAwesome Application - Architecture Diagrams

**Version:** 18.7.2025  
**Repository:** [https://github.com/abdopcnet/posawesome15_lite](https://github.com/abdopcnet/posawesome15_lite)  
**Date:** October 12, 2025

---

## 📊 System Architecture Overview

```mermaid
graph TB
    subgraph "Client Layer - Browser"
        UI[User Interface]
        Browser[Web Browser]
    end

    subgraph "Frontend Layer - Vue.js 3"
        App[Home.vue - Root Component]
        Navbar[Navbar.vue - Navigation]
        POS[Pos.vue - Main Container]
        
        subgraph "POS Components"
            Items[ItemsSelector.vue]
            Invoice[Invoice.vue - 3,125 lines]
            Payments[Payments.vue]
            Offers[PosOffers.vue]
            Coupons[PosCoupons.vue]
            Customer[Customer.vue]
        end
        
        subgraph "Shared Components"
            OpenDialog[OpeningDialog.vue]
            CloseDialog[ClosingDialog.vue]
            Drafts[Drafts.vue]
            Returns[Returns.vue]
            UpdateCust[UpdateCustomer.vue]
            NewAddr[NewAddress.vue]
        end
        
        EventBus[Event Bus - mitt]
    end

    subgraph "Backend Layer - Frappe/ERPNext"
        subgraph "API Endpoints"
            SalesAPI[sales_invoice.py<br/>697 lines]
            ItemAPI[item.py<br/>256 lines]
            CustomerAPI[customer.py<br/>512 lines]
            OfferAPI[pos_offer.py<br/>519 lines]
            ShiftAPI[pos_opening_shift.py<br/>205 lines]
            ProfileAPI[pos_profile.py]
            BatchAPI[batch.py]
        end
        
        subgraph "Document Hooks"
            ValidateHook[validate hooks]
            SubmitHook[before_submit hooks]
            CancelHook[before_cancel hooks]
            InsertHook[after_insert hooks]
        end
    end

    subgraph "Database Layer - MariaDB"
        subgraph "ERPNext Core"
            SITable[Sales Invoice]
            ItemTable[Item]
            CustomerTable[Customer]
            ItemPrice[Item Price]
            Batch[Batch]
        end
        
        subgraph "POS Custom"
            POSOffer[POS Offer]
            POSCoupon[POS Coupon]
            POSProfile[POS Profile]
            POSOpen[POS Opening Shift]
            POSClose[POS Closing Shift]
            Referral[Referral Code]
        end
    end

    %% Connections
    UI --> Browser
    Browser --> App
    App --> Navbar
    App --> POS
    
    POS --> Items
    POS --> Invoice
    POS --> Payments
    POS --> Offers
    POS --> Coupons
    
    Invoice --> Customer
    POS --> OpenDialog
    POS --> CloseDialog
    POS --> Drafts
    POS --> Returns
    Customer --> UpdateCust
    Customer --> NewAddr
    
    Items -.-> EventBus
    Invoice -.-> EventBus
    Payments -.-> EventBus
    Offers -.-> EventBus
    Coupons -.-> EventBus
    Customer -.-> EventBus
    
    EventBus ==> SalesAPI
    EventBus ==> ItemAPI
    EventBus ==> CustomerAPI
    EventBus ==> OfferAPI
    EventBus ==> ShiftAPI
    EventBus ==> ProfileAPI
    EventBus ==> BatchAPI
    
    SalesAPI --> ValidateHook
    SalesAPI --> SubmitHook
    SalesAPI --> CancelHook
    CustomerAPI --> ValidateHook
    CustomerAPI --> InsertHook
    
    SalesAPI --> SITable
    ItemAPI --> ItemTable
    ItemAPI --> ItemPrice
    ItemAPI --> Batch
    CustomerAPI --> CustomerTable
    OfferAPI --> POSOffer
    ShiftAPI --> POSOpen
    ShiftAPI --> POSClose
    CustomerAPI --> Referral
    
    %% Styling
    classDef frontend fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef backend fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef database fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef event fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef critical fill:#ffebee,stroke:#c62828,stroke-width:3px
    
    class App,Navbar,POS,Items,Invoice,Payments,Offers,Coupons,Customer frontend
    class OpenDialog,CloseDialog,Drafts,Returns,UpdateCust,NewAddr frontend
    class SalesAPI,ItemAPI,CustomerAPI,OfferAPI,ShiftAPI,ProfileAPI,BatchAPI backend
    class ValidateHook,SubmitHook,CancelHook,InsertHook backend
    class SITable,ItemTable,CustomerTable,ItemPrice,Batch database
    class POSOffer,POSCoupon,POSProfile,POSOpen,POSClose,Referral database
    class EventBus event
    class Invoice critical
```

---

## 🔄 Component Communication Flow

```mermaid
sequenceDiagram
    participant User
    participant ItemsSelector
    participant EventBus
    participant Invoice
    participant SalesAPI
    participant Database

    User->>ItemsSelector: Click Item / Scan Barcode
    ItemsSelector->>ItemsSelector: Prepare item data
    ItemsSelector->>EventBus: emit('add_item', item)
    EventBus->>Invoice: receive 'add_item' event
    Invoice->>Invoice: Add item to local state
    Invoice->>Invoice: Generate posa_row_id
    Invoice->>Invoice: Calculate totals
    Invoice->>EventBus: emit('update_invoice_debounced')
    EventBus->>Invoice: (after 200ms delay)
    Invoice->>SalesAPI: update_invoice(data)
    SalesAPI->>Database: Save invoice (docstatus=0)
    Database-->>SalesAPI: Return saved invoice
    SalesAPI->>SalesAPI: Apply offers automatically
    SalesAPI->>SalesAPI: Calculate taxes & totals
    SalesAPI-->>Invoice: Return minimal response
    Invoice->>Invoice: Update UI with server data
    Invoice->>User: Show updated invoice
```

---

## 📦 Data Flow Architecture

```mermaid
flowchart LR
    subgraph "User Actions"
        A1[Scan Barcode]
        A2[Search Item]
        A3[Add to Cart]
        A4[Apply Offer]
        A5[Enter Payment]
        A6[Submit Invoice]
    end

    subgraph "Frontend State"
        S1[Items Array]
        S2[Invoice Doc]
        S3[Customer]
        S4[Offers]
        S5[Payments]
    end

    subgraph "Event Bus Events"
        E1[add_item]
        E2[update_customer]
        E3[apply_offer]
        E4[payment_complete]
        E5[invoice_submitted]
    end

    subgraph "API Calls"
        API1[get_items]
        API2[search_items_barcode]
        API3[update_invoice]
        API4[get_applicable_offers]
        API5[submit_invoice]
    end

    subgraph "Database Operations"
        DB1[Read Items]
        DB2[Read/Write Invoice]
        DB3[Read Offers]
        DB4[Write Payments]
        DB5[Submit Transaction]
    end

    A1 --> E1
    A2 --> API1
    A3 --> E1
    A4 --> E3
    A5 --> E4
    A6 --> E5

    E1 --> S1
    S1 --> S2
    E2 --> S3
    E3 --> S4
    E4 --> S5

    S2 --> API3
    API3 --> DB2
    
    E1 --> API2
    API2 --> DB1
    
    S4 --> API4
    API4 --> DB3
    
    E5 --> API5
    API5 --> DB5

    style E1 fill:#fff3e0
    style E2 fill:#fff3e0
    style E3 fill:#fff3e0
    style E4 fill:#fff3e0
    style E5 fill:#fff3e0
```

---

## 🎯 POS Checkout Workflow

```mermaid
stateDiagram-v2
    [*] --> OpenShift: Start Day
    
    OpenShift --> SelectCustomer: Open POS
    
    SelectCustomer --> BrowseItems: Customer Selected
    
    BrowseItems --> AddItem: Search/Scan
    AddItem --> UpdateInvoice: Item Added
    UpdateInvoice --> BrowseItems: Continue Shopping
    UpdateInvoice --> ApplyOffers: Check Offers
    
    ApplyOffers --> UpdateInvoice: Offer Applied
    ApplyOffers --> ProcessPayment: Ready to Pay
    
    ProcessPayment --> SubmitInvoice: Payment Entered
    
    SubmitInvoice --> PrintInvoice: Invoice Submitted
    
    PrintInvoice --> SelectCustomer: Next Customer
    PrintInvoice --> CloseShift: End Day
    
    CloseShift --> [*]: Shift Closed

    note right of OpenShift
        Creates POS Opening Shift
        Records cash denomination
    end note

    note right of AddItem
        Events: add_item
        Debounced: 200ms
        Auto-save to server
    end note

    note right of ApplyOffers
        Automatic offer detection
        Coupon validation
        Discount calculation
    end note

    note right of SubmitInvoice
        Payment validation
        Stock update
        Accounting entries
    end note
```

---

## 🗄️ Database Schema Relationships

```mermaid
erDiagram
    SALES_INVOICE ||--o{ SALES_INVOICE_ITEM : contains
    SALES_INVOICE ||--o{ SALES_INVOICE_PAYMENT : has
    SALES_INVOICE ||--o{ POS_OFFER_APPLIED : applies
    SALES_INVOICE }o--|| CUSTOMER : "billed to"
    SALES_INVOICE }o--|| POS_OPENING_SHIFT : "belongs to"
    
    POS_OPENING_SHIFT ||--|| POS_CLOSING_SHIFT : "closes with"
    POS_OPENING_SHIFT ||--o{ SALES_INVOICE : "tracks"
    
    SALES_INVOICE_ITEM }o--|| ITEM : references
    SALES_INVOICE_ITEM }o--o| BATCH : "may have"
    
    ITEM ||--o{ ITEM_PRICE : "has prices"
    ITEM ||--o{ ITEM_BARCODE : "has barcodes"
    
    POS_OFFER ||--o{ POS_OFFER_DETAIL : "applies to"
    POS_OFFER ||--o{ POS_OFFER_APPLIED : "creates"
    
    POS_COUPON }o--|| POS_OFFER : references
    POS_COUPON }o--o| CUSTOMER : "assigned to"
    POS_COUPON }o--o| REFERRAL_CODE : "created from"
    
    CUSTOMER ||--o{ REFERRAL_CODE : "has"
    CUSTOMER ||--o{ POS_COUPON : receives
    CUSTOMER ||--o{ SALES_INVOICE : generates

    SALES_INVOICE {
        string name PK
        string customer FK
        string pos_opening_shift FK
        datetime posting_date
        float grand_total
        int docstatus
    }

    SALES_INVOICE_ITEM {
        string parent FK
        string item_code FK
        float qty
        float rate
        float amount
    }

    ITEM {
        string name PK
        string item_name
        string stock_uom
        int has_batch_no
        int has_serial_no
    }

    POS_OFFER {
        string name PK
        string title
        string apply_on
        string discount_type
        float discount_percentage
        date valid_from
        date valid_upto
    }

    POS_OPENING_SHIFT {
        string name PK
        string user
        string pos_profile FK
        datetime period_start_date
        int docstatus
    }
```

---

## 🔐 Security & Permission Flow

```mermaid
flowchart TD
    User[User Login] --> Auth{Authenticated?}
    Auth -->|No| Login[Redirect to Login]
    Auth -->|Yes| CheckRole{Has POS Role?}
    
    CheckRole -->|No| Deny[Access Denied]
    CheckRole -->|Yes| LoadProfile[Load POS Profile]
    
    LoadProfile --> CheckShift{Shift Open?}
    CheckShift -->|No| OpenShift[Open Shift Dialog]
    CheckShift -->|Yes| AccessPOS[Access POS Interface]
    
    AccessPOS --> Action{User Action}
    
    Action --> CreateInvoice[Create Invoice]
    Action --> UpdateInvoice[Update Invoice]
    Action --> SubmitInvoice[Submit Invoice]
    
    CreateInvoice --> BypassPerm[ignore_permissions=True]
    UpdateInvoice --> BypassPerm
    SubmitInvoice --> BypassPerm
    
    BypassPerm --> Whitelist{API Whitelisted?}
    Whitelist -->|No| Error[Permission Error]
    Whitelist -->|Yes| ValidateData[Validate Data]
    
    ValidateData --> BusinessLogic[Execute Business Logic]
    BusinessLogic --> SaveDB[(Save to Database)]
    
    SaveDB --> AuditLog[Record in Audit Trail]
    AuditLog --> Success[Return Success]

    style BypassPerm fill:#ffebee,stroke:#c62828
    style Whitelist fill:#fff3e0,stroke:#e65100
    style AuditLog fill:#e8f5e9,stroke:#1b5e20
```

---

## 🎨 Frontend Component Tree

```mermaid
graph TD
    Root[Home.vue - Root App]
    
    Root --> Nav[Navbar.vue]
    Root --> Main[Main Content - Dynamic]
    
    Main --> POS[Pos.vue - POS Container]
    
    POS --> Left{Left Panel - Dynamic}
    POS --> Right[Invoice.vue - Always Visible]
    
    Left -->|Default| Items[ItemsSelector.vue]
    Left -->|Offers Mode| Offers[PosOffers.vue]
    Left -->|Coupons Mode| Coupons[PosCoupons.vue]
    Left -->|Payment Mode| Payments[Payments.vue]
    
    POS --> Dialogs{Dialog Overlays}
    
    Dialogs --> OpenDlg[OpeningDialog.vue]
    Dialogs --> CloseDlg[ClosingDialog.vue]
    Dialogs --> DraftsDlg[Drafts.vue]
    Dialogs --> ReturnsDlg[Returns.vue]
    Dialogs --> AddrDlg[NewAddress.vue]
    
    Right --> Cust[Customer.vue]
    Cust --> UpdateCust[UpdateCustomer.vue]
    
    %% Component Details
    Items -.->|Search & Select| ItemCard[Item Cards/List]
    Items -.->|Barcode Scan| BarcodeInput[Barcode Input]
    Items -.->|Filter| GroupFilter[Item Group Filter]
    
    Right -.->|Date Picker| DatePicker[Posting Date Picker]
    Right -.->|Items Table| ItemsTable[v-data-table]
    Right -.->|Totals| TotalsSection[Totals Display]
    Right -.->|Actions| ActionButtons[Action Buttons]
    
    Payments -.->|Payment Methods| PaymentModes[Payment Mode List]
    Payments -.->|Amount Input| AmountInputs[Amount Fields]
    
    %% Styling
    classDef container fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef component fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef dialog fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef critical fill:#ffebee,stroke:#c62828,stroke-width:3px
    
    class Root,POS container
    class Nav,Items,Offers,Coupons,Payments,Cust component
    class OpenDlg,CloseDlg,DraftsDlg,ReturnsDlg,AddrDlg dialog
    class Right critical
```

---

## 📡 Event Bus Architecture

```mermaid
graph LR
    subgraph "Event Emitters"
        ItemsSel[ItemsSelector.vue]
        Inv[Invoice.vue]
        Pay[Payments.vue]
        Off[PosOffers.vue]
        Coup[PosCoupons.vue]
        Cust[Customer.vue]
        Nav[Navbar.vue]
    end

    subgraph "Event Bus - mitt"
        Bus((Event Bus<br/>mitt - 200 bytes))
    end

    subgraph "Event Listeners"
        InvListen[Invoice Listeners]
        ItemsListen[Items Listeners]
        PayListen[Payment Listeners]
        NavListen[Nav Listeners]
        PosListen[Pos Listeners]
    end

    subgraph "Key Events"
        E1[add_item]
        E2[update_customer]
        E3[apply_offer]
        E4[apply_coupon]
        E5[payment_complete]
        E6[invoice_submitted]
        E7[open_closing_dialog]
        E8[show_message]
        E9[LoadPosProfile]
        E10[item_updated]
    end

    ItemsSel --> Bus
    Inv --> Bus
    Pay --> Bus
    Off --> Bus
    Coup --> Bus
    Cust --> Bus
    Nav --> Bus

    Bus --> E1
    Bus --> E2
    Bus --> E3
    Bus --> E4
    Bus --> E5
    Bus --> E6
    Bus --> E7
    Bus --> E8
    Bus --> E9
    Bus --> E10

    E1 --> InvListen
    E2 --> InvListen
    E3 --> InvListen
    E4 --> InvListen
    E5 --> ItemsListen
    E6 --> NavListen
    E7 --> PosListen
    E8 --> NavListen
    E9 --> PosListen
    E10 --> ItemsListen

    style Bus fill:#fff3e0,stroke:#e65100,stroke-width:3px
```

---

## 🔧 API Request/Response Flow

```mermaid
sequenceDiagram
    participant FE as Frontend (Vue)
    participant EB as Event Bus
    participant API as API Layer (Python)
    participant Hook as Document Hooks
    participant ERP as ERPNext Core
    participant DB as Database

    FE->>EB: emit('add_item', item)
    EB->>FE: Invoice receives event
    
    Note over FE: Add to local state<br/>Debounce 200ms
    
    FE->>API: frappe.call('update_invoice', data)
    
    API->>API: Parse JSON data
    API->>API: Get/Create invoice doc
    API->>API: Update items array
    
    API->>Hook: validate(doc)
    Hook->>Hook: Custom validation logic
    Hook-->>API: Validation passed
    
    API->>ERP: doc.set_missing_values()
    ERP->>ERP: Fill default fields
    ERP->>ERP: Get price if missing
    ERP-->>API: Defaults set
    
    API->>ERP: doc.calculate_taxes_and_totals()
    ERP->>DB: Fetch tax templates
    DB-->>ERP: Tax rules
    ERP->>ERP: Calculate line totals
    ERP->>ERP: Calculate tax amounts
    ERP->>ERP: Calculate grand total
    ERP-->>API: Calculations complete
    
    API->>API: Check for applicable offers
    API->>DB: Query POS Offers
    DB-->>API: Matching offers
    API->>API: Apply offer discounts
    
    API->>API: Save with ignore_permissions=True
    API->>DB: INSERT/UPDATE Sales Invoice
    DB-->>API: Saved successfully
    
    API->>API: get_minimal_invoice_response()
    API-->>FE: Return {name, items, totals, ...}
    
    FE->>FE: Update UI with server data
    FE->>EB: emit('invoice_updated')
```

---

## 🚀 Performance Optimization Points

```mermaid
flowchart TD
    Start[User Action] --> Check1{Cached?}
    
    Check1 -->|Yes| UseCache[Use Cached Data]
    Check1 -->|No| Debounce{Debounced?}
    
    Debounce -->|Yes| Wait[Wait 200ms]
    Debounce -->|No| Direct[Direct Call]
    
    Wait --> Merge{Can Merge?}
    Merge -->|Yes| BatchCall[Batch API Call]
    Merge -->|No| SingleCall[Single API Call]
    
    Direct --> SingleCall
    
    SingleCall --> Query{N+1 Query?}
    Query -->|Fixed| JoinQuery[JOIN Query]
    Query -->|Issue| MultiQuery[Multiple Queries]
    
    BatchCall --> JoinQuery
    
    JoinQuery --> MinimalResp[Minimal Response]
    MultiQuery --> FullResp[Full Response]
    
    UseCache --> Render[Render UI]
    MinimalResp --> Render
    FullResp --> Render
    
    Render --> End[Display to User]
    
    style Check1 fill:#e8f5e9,stroke:#1b5e20
    style UseCache fill:#c8e6c9,stroke:#2e7d32
    style Wait fill:#fff3e0,stroke:#e65100
    style JoinQuery fill:#e1f5fe,stroke:#01579b
    style MultiQuery fill:#ffebee,stroke:#c62828
```

---

## 📊 Invoice State Machine

```mermaid
stateDiagram-v2
    [*] --> Empty: New Invoice
    
    Empty --> Draft: Add First Item
    
    Draft --> Draft: Add/Remove Items
    Draft --> Draft: Update Quantity
    Draft --> Draft: Change Customer
    Draft --> Draft: Apply Discount
    
    Draft --> WithOffers: Apply Offer
    WithOffers --> Draft: Remove Offer
    
    Draft --> WithPayment: Enter Payment
    WithPayment --> Draft: Clear Payment
    
    WithPayment --> Submitting: Click Submit
    
    Submitting --> Submitted: Success
    Submitting --> Draft: Validation Error
    
    Submitted --> Printing: Click Print
    Submitted --> Returning: Create Return
    
    Returning --> ReturnInvoice: Return Created
    
    Submitted --> Cancelled: Cancel Invoice
    
    Printing --> [*]: Complete
    ReturnInvoice --> [*]: Complete
    Cancelled --> [*]: Complete
    
    Draft --> Empty: Clear All Items
    
    note right of Draft
        docstatus = 0
        Auto-saved every 200ms
        Can be modified freely
    end note
    
    note right of Submitted
        docstatus = 1
        Immutable
        Creates accounting entries
        Updates inventory
    end note
    
    note right of Cancelled
        docstatus = 2
        Reverses all entries
        Cannot be edited
    end note
```

---

## 🎯 Critical Performance Issues

```mermaid
mindmap
  root((Performance<br/>Issues))
    N+1 Queries
      Item Fetching
        50 items = 51 queries
        Solution: JOIN query
      Price Fetching
        Separate query per item
        Solution: Single JOIN
    Large Components
      Invoice.vue
        3,125 lines
        Solution: Split into 8-10 components
      Monolithic structure
        Hard to maintain
        Slow to load
    Runtime Assets
      CSS Loading
        Blocks rendering
        Solution: Build-time inclusion
      External Fonts
        Google Fonts CDN
        Solution: Self-host
    No Code Splitting
      Large Bundle
        ~2MB initial load
        Solution: Lazy loading
      All components upfront
        Slow first paint
    Event Bus Memory
      No Cleanup
        Memory leaks
        Solution: beforeUnmount cleanup
      Keep-Alive unlimited
        All pages in memory
        Solution: Max limit
```

---

## 📈 Recommended Architecture Improvements

```mermaid
graph TB
    subgraph "Current Architecture"
        C1[Large Components]
        C2[N+1 Queries]
        C3[No Caching]
        C4[Runtime CSS]
        C5[No Code Splitting]
    end

    subgraph "Improved Architecture"
        I1[Small Focused Components]
        I2[JOIN Queries + Indexes]
        I3[Redis Cache Layer]
        I4[Build-time Assets]
        I5[Lazy Loading + PWA]
    end

    subgraph "Benefits"
        B1[90% Faster Queries]
        B2[Better Maintainability]
        B3[80%+ Cache Hit Rate]
        B4[Faster Page Load]
        B5[Offline Support]
    end

    C1 -.->|Refactor| I1
    C2 -.->|Optimize| I2
    C3 -.->|Implement| I3
    C4 -.->|Fix| I4
    C5 -.->|Add| I5

    I1 --> B2
    I2 --> B1
    I3 --> B3
    I4 --> B4
    I5 --> B5

    style C1 fill:#ffebee,stroke:#c62828
    style C2 fill:#ffebee,stroke:#c62828
    style C3 fill:#ffebee,stroke:#c62828
    style C4 fill:#ffebee,stroke:#c62828
    style C5 fill:#ffebee,stroke:#c62828
    style I1 fill:#e8f5e9,stroke:#1b5e20
    style I2 fill:#e8f5e9,stroke:#1b5e20
    style I3 fill:#e8f5e9,stroke:#1b5e20
    style I4 fill:#e8f5e9,stroke:#1b5e20
    style I5 fill:#e8f5e9,stroke:#1b5e20
```

---

## 📝 Notes

### How to View These Diagrams

1. **VS Code**: Install the "Markdown Preview Mermaid Support" extension
   ```
   Extension ID: bierner.markdown-mermaid
   ```

2. **GitHub**: Diagrams render automatically when viewing on GitHub

3. **Online**: Copy diagrams to [mermaid.live](https://mermaid.live) for editing

### Diagram Legend

- **Blue boxes**: Frontend components (Vue.js)
- **Purple boxes**: Backend components (Python/Frappe)
- **Green boxes**: Database tables (MariaDB)
- **Orange boxes**: Event-driven components
- **Red boxes**: Critical/Large components needing attention

### Related Documentation

- [Complete Analysis](./posawesome_comprehensive_analysis.md)
- [Improvement Plan](./IMPROVEMENT_PLAN.md)
- [File Structure](./app_tree.md)
- [README](./README.md)

---

**Last Updated:** October 12, 2025  
**Maintained By:** abdopcnet@gmail.com  
**Repository:** [https://github.com/abdopcnet/posawesome15_lite](https://github.com/abdopcnet/posawesome15_lite)
