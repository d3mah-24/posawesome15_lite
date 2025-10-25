<template>
  <div class="pos-container">
    <ClosingDialog></ClosingDialog>
    <Returns></Returns>
    <NewAddress></NewAddress>
    <OpeningDialog v-if="dialog" :dialog="dialog"></OpeningDialog>

    <div v-show="!dialog" class="pos-main-wrapper">
      <div class="pos-left-panel">
        <div v-show="!payment && !offers" class="panel-content">
          <ItemsSelector></ItemsSelector>
        </div>
        <div v-show="offers" class="panel-content">
          <PosOffers @offerApplied="handleOfferApplied" @offerRemoved="handleOfferRemoved"></PosOffers>
        </div>
        <div v-show="payment" class="panel-content">
          <Payments ref="payments" @request-print="onPrintRequest"></Payments>
        </div>
      </div>

      <div class="pos-right-panel">
        <div class="panel-content">
          <Invoice :is_payment="payment" :offer-applied="offerApplied" :offer-removed="offerRemoved"></Invoice>
        </div>
      </div>
    </div>
  </div>
</template>

<script src="./Pos.js" />

<style scoped>
/* ===== MAIN CONTAINER ===== */
/* Simple background - no gradient to avoid affecting ERP doctypes */
.pos-container {
  padding: 0 3px 3px 3px;
  /* top=0, right=3px, bottom=3px, left=3px */
  background: #f8f9fa;
  /* Simple light gray background */
  min-height: 100vh;
  overflow: visible;
}

/* ===== MAIN WRAPPER - FLEXBOX LAYOUT ===== */
.pos-main-wrapper {
  display: flex;
  gap: 5px;
  min-height: calc(100vh - 130px) !important;
  width: 100%;
  margin-top: 3px !important;
}

/* ===== LEFT PANEL (Items/Offers/Payments) ===== */
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
.panel-content>* {
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
    padding: 0 2px 2px 2px;
    /* top=0, right=2px, bottom=2px, left=2px */
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
    padding: 0 2px 2px 2px;
    /* top=0, right=2px, bottom=2px, left=2px */
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
.pos-left-panel>div {
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

.pos-left-panel>div[style*="display: none"] {
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}

.pos-left-panel>div:not([style*="display: none"]) {
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
