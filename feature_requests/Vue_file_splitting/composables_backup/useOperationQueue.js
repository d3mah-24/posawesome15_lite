/**
 * useOperationQueue - Operation Batching Queue System
 * 
 * Implements the mandatory 3-API batch queue policy:
 * - Collects all operations (item, payment, discount, offers, customer)
 * - Waits 1 second idle time
 * - Sends ONE batch API call with all changes
 * - Proper timer cleanup
 */

import { ref } from 'vue'
import { evntBus } from '../bus'

export function useOperationQueue() {
  // ===== OPERATION CACHE =====
  const operationQueue = ref([])
  const lastOperationTime = ref(null)
  const batchTimer = ref(null)
  const maxBatchSize = 50
  const batchWaitTime = 1000 // 1 second

  /**
   * Add operation to queue
   * @param {Object} operation - Operation object
   * @param {string} operation.type - Operation type (qty, rate, discount, offer, payment, customer)
   * @param {Object} operation.data - Operation data
   * @param {string} operation.itemCode - Item code (if item operation)
   */
  const queueOperation = (operation) => {
    if (!operation || !operation.type) return

    // Check if batch is full
    if (operationQueue.value.length >= maxBatchSize) {
      // Force send before adding new operation
      return flushQueue()
    }

    // Add to queue
    operationQueue.value.push({
      ...operation,
      timestamp: Date.now(),
    })

    // Reset batch timer
    resetBatchTimer()
  }

  /**
   * Add multiple operations at once
   * @param {Array} operations - Array of operation objects
   */
  const queueOperations = (operations = []) => {
    if (!Array.isArray(operations) || operations.length === 0) return

    operations.forEach((op) => {
      if (operationQueue.value.length < maxBatchSize) {
        operationQueue.value.push({
          ...op,
          timestamp: Date.now(),
        })
      }
    })

    resetBatchTimer()
  }

  /**
   * Reset batch timer - wait for 1 second idle before sending
   */
  const resetBatchTimer = () => {
    // Clear existing timer
    if (batchTimer.value) {
      clearTimeout(batchTimer.value)
    }

    // Set new timer - wait 1 second of idle time
    batchTimer.value = setTimeout(() => {
      if (operationQueue.value.length > 0) {
        flushQueue()
      }
    }, batchWaitTime)

    lastOperationTime.value = Date.now()
  }

  /**
   * Immediately flush queue without waiting
   * @returns {Promise<void>}
   */
  const flushQueue = async () => {
    if (operationQueue.value.length === 0) return

    // Clear timer if exists
    if (batchTimer.value) {
      clearTimeout(batchTimer.value)
      batchTimer.value = null
    }

    // Get all operations from queue
    const operations = operationQueue.value.slice()
    operationQueue.value = [] // Clear queue

    // Group operations by type
    const grouped = groupOperationsByType(operations)

    // Emit batch event for Invoice.vue to handle
    evntBus.emit('batch_operations_ready', {
      operations: grouped,
      count: operations.length,
      timestamp: Date.now(),
    })

    return operations
  }

  /**
   * Group operations by type for processing
   * @param {Array} operations - Operations to group
   * @returns {Object} - Grouped operations
   */
  const groupOperationsByType = (operations = []) => {
    const grouped = {
      items: [],
      discounts: [],
      offers: [],
      payments: [],
      customer: null,
      other: [],
    }

    operations.forEach((op) => {
      switch (op.type) {
        case 'qty':
        case 'rate':
        case 'item-discount':
          grouped.items.push(op)
          break
        case 'invoice-discount':
          grouped.discounts.push(op)
          break
        case 'offer':
        case 'coupon':
          grouped.offers.push(op)
          break
        case 'payment':
          grouped.payments.push(op)
          break
        case 'customer':
          grouped.customer = op
          break
        default:
          grouped.other.push(op)
      }
    })

    return grouped
  }

  /**
   * Get current queue size
   * @returns {number}
   */
  const getQueueSize = () => operationQueue.value.length

  /**
   * Check if queue has pending operations
   * @returns {boolean}
   */
  const hasPendingOperations = () => operationQueue.value.length > 0

  /**
   * Get queue contents (for debugging)
   * @returns {Array}
   */
  const getQueueContents = () => [...operationQueue.value]

  /**
   * Force immediate flush without waiting
   * @returns {Promise<void>}
   */
  const forceFlush = async () => {
    return flushQueue()
  }

  /**
   * Clear queue completely
   */
  const clearQueue = () => {
    operationQueue.value = []
    if (batchTimer.value) {
      clearTimeout(batchTimer.value)
      batchTimer.value = null
    }
  }

  /**
   * Cleanup on unmount
   */
  const cleanup = () => {
    if (batchTimer.value) {
      clearTimeout(batchTimer.value)
      batchTimer.value = null
    }
    operationQueue.value = []
    lastOperationTime.value = null
  }

  return {
    // Queue operations
    queueOperation,
    queueOperations,

    // Queue control
    flushQueue,
    forceFlush,
    clearQueue,
    resetBatchTimer,

    // Queue info
    getQueueSize,
    hasPendingOperations,
    getQueueContents,

    // Cleanup
    cleanup,

    // Constants (for reference)
    maxBatchSize,
    batchWaitTime,
  }
}
