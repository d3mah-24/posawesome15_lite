/**
 * Clear All Caches Utility
 * Comprehensive cache clearing functionality for POS Awesome
 * Based on: https://github.com/abdopcnet/posawesome_18092025
 */

class CacheManager {
  constructor() {
    this.isClearing = false;
  }

  /**
   * Clear all possible caches
   */
  async clearAllCaches() {
    if (this.isClearing) {
      console.log('Cache clearing already in progress...');
      return;
    }

    this.isClearing = true;
    console.log('Starting comprehensive cache clearing...');

    try {
      // Clear localStorage
      await this.clearLocalStorage();
      
      // Clear sessionStorage
      await this.clearSessionStorage();
      
      // Clear IndexedDB
      await this.clearIndexedDB();
      
      // Clear Service Worker Cache
      await this.clearServiceWorkerCache();
      
      // Clear Browser Cache (if possible)
      await this.clearBrowserCache();
      
      // Clear Frappe specific caches
      await this.clearFrappeCaches();
      
      console.log('All caches cleared successfully');
      return true;
      
    } catch (error) {
      console.error('Error clearing caches:', error);
      return false;
    } finally {
      this.isClearing = false;
    }
  }

  /**
   * Clear localStorage
   */
  async clearLocalStorage() {
    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        localStorage.removeItem(key);
      });
      console.log(`Cleared ${keys.length} localStorage items`);
    } catch (error) {
      console.error('Error clearing localStorage:', error);
    }
  }

  /**
   * Clear sessionStorage
   */
  async clearSessionStorage() {
    try {
      const keys = Object.keys(sessionStorage);
      keys.forEach(key => {
        sessionStorage.removeItem(key);
      });
      console.log(`Cleared ${keys.length} sessionStorage items`);
    } catch (error) {
      console.error('Error clearing sessionStorage:', error);
    }
  }

  /**
   * Clear IndexedDB databases
   */
  async clearIndexedDB() {
    try {
      if ('indexedDB' in window) {
        const databases = await indexedDB.databases();
        const deletePromises = databases.map(db => {
          return new Promise((resolve, reject) => {
            const deleteReq = indexedDB.deleteDatabase(db.name);
            deleteReq.onsuccess = () => resolve();
            deleteReq.onerror = () => reject(deleteReq.error);
            deleteReq.onblocked = () => {
              console.warn(`Database ${db.name} deletion blocked`);
              resolve();
            };
          });
        });
        
        await Promise.all(deletePromises);
        console.log(`Cleared ${databases.length} IndexedDB databases`);
      }
    } catch (error) {
      console.error('Error clearing IndexedDB:', error);
    }
  }

  /**
   * Clear Service Worker Cache
   */
  async clearServiceWorkerCache() {
    try {
      if ('caches' in window) {
        const cacheNames = await caches.keys();
        const deletePromises = cacheNames.map(cacheName => caches.delete(cacheName));
        await Promise.all(deletePromises);
        console.log(`Cleared ${cacheNames.length} service worker caches`);
      }
    } catch (error) {
      console.error('Error clearing service worker cache:', error);
    }
  }

  /**
   * Clear Browser Cache (limited functionality)
   */
  async clearBrowserCache() {
    try {
      // Clear application cache if available
      if ('applicationCache' in window) {
        window.applicationCache.update();
      }
      
      // Clear any custom caches
      if (window.clearCustomCaches && typeof window.clearCustomCaches === 'function') {
        await window.clearCustomCaches();
      }
      
      console.log('Browser cache cleared');
    } catch (error) {
      console.error('Error clearing browser cache:', error);
    }
  }

  /**
   * Clear Frappe specific caches
   */
  async clearFrappeCaches() {
    try {
      // Clear Frappe's localStorage caches
      const frappeKeys = Object.keys(localStorage).filter(key => 
        key.startsWith('frappe_') || 
        key.startsWith('posawesome_') ||
        key.includes('pos_') ||
        key.includes('invoice_') ||
        key.includes('customer_')
      );
      
      frappeKeys.forEach(key => {
        localStorage.removeItem(key);
      });
      
      console.log(`Cleared ${frappeKeys.length} Frappe-specific cache items`);
      
      // Clear any Frappe global variables
      if (window.frappe && window.frappe.cache) {
        try {
          window.frappe.cache.clear();
        } catch (e) {
          // Frappe cache clear not available
        }
      }
      
    } catch (error) {
      console.error('Error clearing Frappe caches:', error);
    }
  }

  /**
   * Reload page after cache clearing
   */
  reloadPage(delay = 1000) {
    setTimeout(() => {
      console.log('Reloading page...');
      location.reload();
    }, delay);
  }

  /**
   * Show cache clearing status
   */
  showStatus(message, type = 'info') {
    if (window.evntBus) {
      window.evntBus.emit('show_mesage', {
        text: message,
        color: type
      });
    } else {
      console.log(`[${type.toUpperCase()}] ${message}`);
    }
  }
}

// Create global instance
window.cacheManager = new CacheManager();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CacheManager;
}

// Auto-attach to DOM if button exists
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("clear-cache-btn");
  if (btn) {
    btn.addEventListener('click', async () => {
      window.cacheManager.showStatus('Clearing cache...', 'info');
      const success = await window.cacheManager.clearAllCaches();
      
      if (success) {
        window.cacheManager.showStatus('Cache cleared successfully. Reloading...', 'success');
        window.cacheManager.reloadPage();
      } else {
        window.cacheManager.showStatus('Error clearing cache', 'error');
      }
    });
  }
});

// Global function for easy access
window.clearAllCaches = async function() {
  return await window.cacheManager.clearAllCaches();
};
