export default {
    data () {
        return {
            float_precision: 2,
            currency_precision: 2,
            // Add cache for optimization
            _formatCache: new Map(),
            _currencySymbolCache: new Map(),
            _lastCacheCleanup: Date.now()
        };
    },
    methods: {
        flt (value, precision, number_format, rounding_method) {
            try {
                if (!precision && precision != 0) {
                    precision = this.currency_precision || 2;
                }
                if (!rounding_method) {
                    rounding_method = "Banker's Rounding (legacy)";
                }
                return flt(value, precision, number_format, rounding_method);
            } catch (error) {
                console.error('[format.js] Error in flt:', error);
                return value;
            }
        },
        
        formatCurrency (value, precision) {
            try {
                const cacheKey = `currency_${value}_${precision}_${this.pos_profile?.currency}`;
                
                if (this._formatCache.has(cacheKey)) {
                    return this._formatCache.get(cacheKey);
                }
                
                const format = get_number_format(this.pos_profile?.currency);
                const formattedValue = format_number(
                    value,
                    format,
                    precision || this.currency_precision || 2
                );
                
                this._formatCache.set(cacheKey, formattedValue);
                this._cleanupCache();
                
                return formattedValue;
            } catch (error) {
                console.error('[format.js] Error in formatCurrency:', error);
                return value;
            }
        },
        
        formatFloat (value, precision) {
            try {
                const cacheKey = `float_${value}_${precision}_${this.pos_profile?.currency}`;
                
                if (this._formatCache.has(cacheKey)) {
                    return this._formatCache.get(cacheKey);
                }
                
                const format = get_number_format(this.pos_profile?.currency);
                const formattedValue = format_number(value, format, precision || this.float_precision || 2);
                
                this._formatCache.set(cacheKey, formattedValue);
                this._cleanupCache();
                
                return formattedValue;
            } catch (error) {
                console.error('[format.js] Error in formatFloat:', error);
                return value;
            }
        },
        
        setFormatedCurrency (el, field_name, precision, no_negative = false, $event) {
            let value = 0;
            try {
                // make sure it is a number and positive
                let _value = parseFloat($event.target.value);
                if (!isNaN(_value)) {
                    value = _value;
                }
                if (no_negative && value < 0) {
                    value = value * -1;
                }
                value = this.formatCurrency($event.target.value, precision);
            } catch (e) {
                console.error('[format.js] Error in setFormatedCurrency:', e);
                value = 0;
            }
            // check if el is an object
            if (typeof el === "object") {
                el[field_name] = value;
            }
            else {
                this[field_name] = value;
            }
            return value;
        },
        
        setFormatedFloat (el, field_name, precision, no_negative = false, $event) {
            let value = 0;
            try {
                // make sure it is a number and positive
                value = parseFloat($event.target.value);
                if (isNaN(value)) {
                    value = 0;
                } else if (no_negative && value < 0) {
                    value = value * -1;
                }
                value = this.formatFloat($event.target.value, precision);
            } catch (e) {
                console.error('[format.js] Error in setFormatedFloat:', e);
                value = 0;
            }
            // check if el is an object
            if (typeof el === "object") {
                el[field_name] = value;
            }
            else {
                this[field_name] = value;
            }
            return value;
        },
        
        currencySymbol (currency) {
            return '';
        },
        
        isNumber (value) {
            try {
                const pattern = /^-?(\d+|\d{1,3}(\.\d{3})*)(,\d+)?$/;
                return pattern.test(value) || "invalid number";
            } catch (error) {
                console.error('[format.js] Error in isNumber:', error);
                return false;
            }
        },
        
        // Helper function to cleanup cache
        _cleanupCache() {
            // Cleanup cache every 5 minutes
            if (Date.now() - this._lastCacheCleanup > 300000) {
                this._formatCache.clear();
                this._currencySymbolCache.clear();
                this._lastCacheCleanup = Date.now();
            }
        }
    },
    
    mounted () {
        this.float_precision = frappe.defaults.get_default('float_precision') || 2;
        this.currency_precision = frappe.defaults.get_default('currency_precision') || 2;
    },
    
    // Cleanup memory when component is destroyed
    beforeDestroy() {
        this._formatCache.clear();
        this._currencySymbolCache.clear();
    }
};