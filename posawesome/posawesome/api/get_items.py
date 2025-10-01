# -*- coding: utf-8 -*-
"""
New optimized get_items function for POS Awesome
Standalone function with all required fields for frontend
"""

import json
import frappe
from frappe.utils import nowdate
from erpnext.stock.doctype.batch.batch import get_batch_qty
from erpnext.accounts.doctype.pos_profile.pos_profile import get_item_groups


@frappe.whitelist()
def get_items(
    pos_profile, price_list=None, item_group="", search_value="", customer=None
):
    """
    Optimized standalone function to get items with all required fields
    
    Args:
        pos_profile: JSON string of POS Profile data
        price_list: Price list name (optional)
        item_group: Item group filter (optional)
        search_value: Search term for item code/name (optional)
        customer: Customer for customer-specific pricing (optional)
    
    Returns:
        List of item dictionaries with all required fields
    """
    pos_profile = json.loads(pos_profile)
    today = nowdate()
    warehouse = pos_profile.get("warehouse")
    
    if not price_list:
        price_list = pos_profile.get("selling_price_list")
    
    # Build conditions
    conditions = ["i.disabled = 0", "i.is_sales_item = 1", "i.is_fixed_asset = 0"]
    
    # Item group condition
    if item_group:
        conditions.append(f"i.item_group LIKE '%{item_group}%'")
    
    # Search condition
    if search_value:
        conditions.append(f"(i.name LIKE '%{search_value}%' OR i.item_name LIKE '%{search_value}%')")
    
    # POS Profile item groups condition
    item_groups = get_item_groups(pos_profile.get("name"))
    if item_groups:
        item_groups_str = "', '".join(item_groups)
        conditions.append(f"i.item_group IN ('{item_groups_str}')")
    
    # Template items condition
    if not pos_profile.get("posa_show_template_items"):
        conditions.append("i.has_variants = 0")
    
    where_clause = " AND ".join(conditions)
    
    # Main optimized SQL query
    sql_query = f"""
    SELECT 
        i.name AS item_code,
        i.item_name,
        i.description,
        i.stock_uom,
        i.image,
        i.is_stock_item,
        i.has_variants,
        i.variant_of,
        i.item_group,
        i.has_batch_no,
        i.has_serial_no,
        i.max_discount,
        i.brand,
        COALESCE(ip.price_list_rate, 0) AS rate,
        COALESCE(ip.currency, '{pos_profile.get("currency", "SAR")}') AS currency,
        COALESCE(sle.qty_after_transaction, 0) AS actual_qty
    FROM `tabItem` i
    LEFT JOIN (
        SELECT 
            item_code,
            price_list_rate,
            currency,
            ROW_NUMBER() OVER (
                PARTITION BY item_code 
                ORDER BY valid_from DESC, creation DESC
            ) as rn
        FROM `tabItem Price`
        WHERE price_list = '{price_list}'
            AND selling = 1
            AND (valid_from IS NULL OR valid_from <= '{today}')
            AND (valid_upto IS NULL OR valid_upto >= '{today}')
            AND (customer IS NULL OR customer = '' OR customer = '{customer or ""}')
    ) ip ON i.name = ip.item_code AND ip.rn = 1
    LEFT JOIN (
        SELECT 
            item_code,
            qty_after_transaction,
            ROW_NUMBER() OVER (
                PARTITION BY item_code 
                ORDER BY posting_date DESC, posting_time DESC, creation DESC
            ) as rn
        FROM `tabStock Ledger Entry`
        WHERE warehouse = '{warehouse}'
            AND is_cancelled = 0
    ) sle ON i.name = sle.item_code AND sle.rn = 1
    WHERE {where_clause}
    ORDER BY i.item_name ASC
    LIMIT 500
    """
    
    # Execute main query
    items_data = frappe.db.sql(sql_query, as_dict=True)
    
    # Process each item to add additional data
    result = []
    for item in items_data:
        item_code = item['item_code']
        
        # Get item UOMs
        item_uoms = get_item_uoms(item_code)
        item['item_uoms'] = item_uoms or []
        
        # Get item barcodes
        item_barcodes = frappe.get_all(
            "Item Barcode",
            filters={"parent": item_code},
            fields=["barcode", "posa_uom"],
        )
        item['item_barcode'] = item_barcodes or []
        
        # Get serial numbers
        serial_no_data = []
        if item['has_serial_no']:
            serial_no_data = frappe.get_all(
                "Serial No",
                filters={
                    "item_code": item_code,
                    "status": "Active",
                    "warehouse": warehouse,
                },
                fields=["name as serial_no"],
            )
        item['serial_no_data'] = serial_no_data
        
        # Get batch numbers
        batch_no_data = []
        if item['has_batch_no']:
            batch_list = get_batch_qty(warehouse=warehouse, item_code=item_code)
            if batch_list:
                for batch in batch_list:
                    if batch.qty > 0 and batch.batch_no:
                        batch_doc = frappe.get_cached_doc("Batch", batch.batch_no)
                        if (
                            str(batch_doc.expiry_date) > str(today)
                            or batch_doc.expiry_date in ["", None]
                        ) and batch_doc.disabled == 0:
                            batch_no_data.append({
                                "batch_no": batch.batch_no,
                                "batch_qty": batch.qty,
                                "expiry_date": batch_doc.expiry_date,
                                "batch_price": batch_doc.posa_batch_price,
                                "manufacturing_date": batch_doc.manufacturing_date,
                            })
        item['batch_no_data'] = batch_no_data
        
        # Get attributes for template items
        attributes = ""
        if pos_profile.get("posa_show_template_items") and item['has_variants']:
            attributes = get_item_attributes(item_code)
        item['attributes'] = attributes or ""
        
        # Get item attributes for variants
        item_attributes = []
        if pos_profile.get("posa_show_template_items") and item['variant_of']:
            item_attributes = frappe.get_all(
                "Item Variant Attribute",
                fields=["attribute", "attribute_value"],
                filters={"parent": item_code, "parentfield": "attributes"},
            )
        item['item_attributes'] = item_attributes or []
        
        # Filter by stock if required
        if pos_profile.get("posa_display_items_in_stock") and item['actual_qty'] <= 0:
            continue
            
        result.append(item)
    
    return result


def get_item_uoms(item_code):
    """
    Get all UOM conversion details for an item
    """
    try:
        # Get stock UOM
        stock_uom = frappe.get_cached_value("Item", item_code, "stock_uom")
        
        # Get all UOM conversion details
        item_uoms = frappe.get_all(
            "UOM Conversion Detail",
            filters={"parent": item_code},
            fields=["uom", "conversion_factor"],
        )
        
        # Add stock UOM if not already in the list
        stock_uom_exists = any(uom["uom"] == stock_uom for uom in item_uoms)
        if not stock_uom_exists:
            item_uoms.insert(0, {"uom": stock_uom, "conversion_factor": 1.0})
            
        return item_uoms
    except Exception as e:
        frappe.logger().error(f'Error in get_item_uoms: {e}')
        return []


def get_item_attributes(item_code):
    """
    Get item attributes for template items
    """
    try:
        attributes = frappe.db.get_all(
            "Item Variant Attribute",
            fields=["attribute"],
            filters={"parenttype": "Item", "parent": item_code},
            order_by="idx asc",
        )

        optional_attributes = get_item_optional_attributes(item_code)

        for a in attributes:
            values = frappe.db.get_all(
                "Item Attribute Value",
                fields=["attribute_value", "abbr"],
                filters={"parenttype": "Item Attribute", "parent": a.attribute},
                order_by="idx asc",
            )
            a.values = values
            if a.attribute in optional_attributes:
                a.optional = True

        return attributes
    except Exception as e:
        frappe.logger().error(f'Error in get_item_attributes: {e}')
        return []

@frappe.whitelist()
def get_items_groups():
    """
    Get list of item groups for POS interface
    Returns list of item group names
    """
    return frappe.db.sql(
        """
        SELECT name 
        FROM `tabItem Group`
        WHERE is_group = 0
        ORDER BY name
        LIMIT 200
        """,
        as_dict=1,
    )