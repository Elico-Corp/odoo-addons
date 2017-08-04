# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import osv, fields
import openerp.addons.decimal_precision as dp
import time, pytz
from datetime import datetime
from tools.translate import _
        
class product_product(osv.osv):
    _inherit = 'product.product'
      
    _columns = {
        'product_safe_qty': fields.float('Minimum stock warning Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
    }
    _defaults = {    
        'product_safe_qty': 0.0,
    }
product_product()


class product_inventory(osv.osv):
    _name = 'product.inventory'
    _description = 'Product Inventory'
    _rec_name = "code"
    _order = 'code'
    
    _columns = {
        'product_id':    fields.many2one('product.product', 'Products', required=True),
        'onhand_qty':    fields.float("Onhand Quantity", digits_compute=dp.get_precision('Product Unit of Measure')),        
        'onorder_qty':   fields.float("Future Quantity", digits_compute=dp.get_precision('Product Unit of Measure')),
        'ondraft_qty':   fields.float("Not Confirm Quantity", digits_compute=dp.get_precision('Product Unit of Measure')),
        'date':          fields.datetime('Creation Date'),
        'category_id':   fields.many2one('product.category',string='Category'),
        'stock_type_id': fields.many2one('product.stock_type',string='Stock Type'),
        'uom_id':        fields.many2one('product.uom',string='UoM'),
        'code':          fields.char('SKU', size=128,),
        'product_safe_qty': fields.float('Minimum stock warning Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        'name': fields.related('product_id', 'name', string=_('Name'), type='char', size=128),
        'out_stock':fields.boolean("Out Stock"),
    }
    _defaults = {
        'onhand_qty': 0.0,
        'onorder_qty': 0.0,
        'ondraft_qty': 0.0,
        'product_safe_qty': 0.0,
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }    
    
    
    def compute_inventory(self, cr, uid, context=None):
        #prod_obj = self.pool.get('product.product')
        cr.execute("""TRUNCATE TABLE product_inventory""")
        cr.execute("""INSERT INTO product_inventory( product_id, date) SELECT id,current_timestamp at time zone 'UTC' FROM product_product WHERE active AND id IN (SELECT distinct product_id FROM stock_move ) ORDER BY id""")
        cr.execute("""INSERT INTO product_inventory( product_id, date) SELECT product_id,current_timestamp at time zone 'UTC' FROM purchase_order_line WHERE product_id NOT IN (SELECT distinct product_id FROM stock_move ) ORDER BY product_id""")
        cr.execute("""
                UPDATE product_inventory AS i 
                SET code = p.default_code, category_id = t.categ_id,
                    stock_type_id = t.stock_type_id, uom_id = t.uom_id, product_safe_qty = p.product_safe_qty
                FROM product_product p, product_template t
                WHERE i.product_id = p.id AND p.product_tmpl_id = t.id""")
        
        #onhand_qty
        cr.execute("""
                UPDATE product_inventory 
                SET onhand_qty = sl.product_qty 
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),3) AS product_qty
                    FROM stock_move m
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state = 'done'
                    AND m.location_id NOT IN (SELECT distinct d.id 
                                              FROM stock_warehouse w, stock_location h, stock_location d
                                              WHERE w.lot_stock_id = h.id 
                                              AND d.parent_left >= h.parent_left 
                                              AND d.parent_right <= h.parent_right)
                    AND m.location_dest_id IN (SELECT distinct d.id 
                                               FROM stock_warehouse w, stock_location h, stock_location d
                                               WHERE w.lot_stock_id = h.id 
                                               AND d.parent_left >= h.parent_left 
                                               AND d.parent_right <= h.parent_right)
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory.product_id = sl.product_id """)
        
        # Useless, no ?
        #cr.execute("""UPDATE product_inventory SET onhand_qty = 0.0 WHERE coalesce(onhand_qty,0.0) = 0.0""")
        
        cr.execute("""
                UPDATE product_inventory SET onhand_qty = onhand_qty - sl.product_qty 
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),3) AS product_qty
                    FROM stock_move m
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state = 'done'
                    AND m.location_id IN (SELECT distinct d.id 
                                          FROM stock_warehouse w, stock_location h, stock_location d
                                          WHERE w.lot_stock_id = h.id 
                                          AND d.parent_left >= h.parent_left 
                                          AND d.parent_right <= h.parent_right)
                    AND m.location_dest_id NOT IN (SELECT distinct d.id 
                                                   FROM stock_warehouse w, stock_location h, stock_location d
                                                   WHERE w.lot_stock_id = h.id 
                                                   AND d.parent_left >= h.parent_left 
                                                   AND d.parent_right <= h.parent_right)
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory.product_id = sl.product_id """)
        
        
        #onorder_qty
        cr.execute("""
                UPDATE product_inventory SET onorder_qty = sl.product_qty 
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),3) AS product_qty
                    FROM stock_move m
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state != 'cancel' AND m.state != 'new'
                    AND m.location_id NOT IN (SELECT distinct d.id 
                                              FROM stock_warehouse w, stock_location h, stock_location d
                                              WHERE w.lot_stock_id = h.id 
                                              AND d.parent_left >= h.parent_left 
                                              AND d.parent_right <= h.parent_right)
                    AND m.location_dest_id IN (SELECT distinct d.id 
                                               FROM stock_warehouse w, stock_location h, stock_location d
                                               WHERE w.lot_stock_id = h.id 
                                               AND d.parent_left >= h.parent_left 
                                               AND d.parent_right <= h.parent_right)
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory.product_id = sl.product_id """)
        
        # Useless, no ?
        #cr.execute("""UPDATE product_inventory SET onorder_qty = 0.0 WHERE coalesce(onorder_qty,0.0) = 0.0""")
        
        cr.execute("""
                UPDATE product_inventory SET onorder_qty = onorder_qty - sl.product_qty 
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),3) AS product_qty
                    FROM stock_move m
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state != 'cancel' AND m.state != 'new'
                    AND m.location_id IN (SELECT distinct d.id 
                                          FROM stock_warehouse w, stock_location h, stock_location d
                                          WHERE w.lot_stock_id = h.id 
                                          AND d.parent_left >= h.parent_left 
                                          AND d.parent_right <= h.parent_right)
                    AND m.location_dest_id NOT IN (SELECT distinct d.id 
                                                   FROM stock_warehouse w, stock_location h, stock_location d
                                                   WHERE w.lot_stock_id = h.id 
                                                   AND d.parent_left >= h.parent_left 
                                                   AND d.parent_right <= h.parent_right)
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory.product_id = sl.product_id """)
        
        
        #ondraft_qty
        cr.execute("""
                UPDATE product_inventory SET ondraft_qty = sl.product_qty 
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),3) AS product_qty
                    FROM purchase_order_line m
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state = 'draft'
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory.product_id = sl.product_id """)
        
        # Useless, no ?
        #cr.execute("""UPDATE product_inventory SET ondraft_qty = 0.0 WHERE coalesce(ondraft_qty,0.0) = 0.0""")
        
        cr.execute("""UPDATE product_inventory SET out_stock = True WHERE onhand_qty < product_safe_qty""")
        return True

product_inventory()


class product_inventory_dates(osv.osv):
    _name = 'product.inventory.dates'
    _description = 'Product Inventory between dates'
    _rec_name = "code"
    _order = 'code'
    
    _columns = {
        'product_id':      fields.many2one('product.product', 'Product', required=True),
        'product_tmpl_id': fields.many2one('product.template', 'Product Template', required=True),
        'start_qty':       fields.float("Beginning Quantity", digits_compute=dp.get_precision('Product Unit of Measure')),        
        'buy_qty':         fields.float("Purchase Quantity", digits_compute=dp.get_precision('Product Unit of Measure')),
        'sale_qty':        fields.float("Sale Quantity", digits_compute=dp.get_precision('Product Unit of Measure')),
        'scrap_qty':       fields.float("Scrap Quantity", digits_compute=dp.get_precision('Product Unit of Measure')),        
        'consume_qty':     fields.float("Consumption Quantity", digits_compute=dp.get_precision('Product Unit of Measure')),
        'produce_qty':     fields.float("Production Quantity", digits_compute=dp.get_precision('Product Unit of Measure')),
        'end_qty':         fields.float("End Quantity", digits_compute=dp.get_precision('Product Unit of Measure')),
        'start_value':     fields.float("Start Value", digits_compute=dp.get_precision('Account')),
        'start_price':     fields.float("Start Price", digits_compute=dp.get_precision('Account')),
        'buy_value':       fields.float("Purchase Value", digits_compute=dp.get_precision('Account')),
        'sale_value':      fields.float("Sale Value", digits_compute=dp.get_precision('Account')),
        'scrap_value':     fields.float("Scrap Value", digits_compute=dp.get_precision('Account')),        
        'consume_value':   fields.float("Consumption Value", digits_compute=dp.get_precision('Account')),
        'produce_value':   fields.float("Production Value", digits_compute=dp.get_precision('Account')),
        'end_value':       fields.float("End Value", digits_compute=dp.get_precision('Account')),
        'end_price':       fields.float("End Price", digits_compute=dp.get_precision('Account')),
        'category_id':     fields.many2one('product.category',string='Category'),
        'stock_type_id':   fields.many2one('product.stock_type',string='Stock Type'),
        'uom_id':          fields.many2one('product.uom',string='UoM'),
        'code':            fields.char('SKU', size=128,),
        'from_date':       fields.datetime('Start Date'),
        'to_date':         fields.datetime('End Date'),
        'prod_active':          fields.boolean("Product Active?"),
    }
    _defaults = {
        'start_qty': 0.00,
        'end_qty': 0.00,
        'scrap_qty': 0.00,
        'consume_qty': 0.00,
        'produce_qty': 0.00,
        'buy_qty': 0.00,
        'sale_qty':0.00,
    }


    def _auto_init(self, cr, context=None):
        super(product_inventory_dates, self)._auto_init(cr, context=context)
        ###### Create Stored Function which calculated the Start and End prices ######
        cr.execute("SELECT proname FROM pg_catalog.pg_proc WHERE proname = 'set_product_inventory_dates_prices'")
        if not cr.fetchone():
            cr.execute("""
                CREATE OR REPLACE FUNCTION set_product_inventory_dates_prices() RETURNS integer AS $$
                DECLARE
                    inventory RECORD;
                    product_value numeric(5);
                BEGIN
                    FOR inventory IN (SELECT product_id, product_tmpl_id, from_date, to_date FROM product_inventory_dates) LOOP
                        -- Start Price
                        product_value := 0;
                        SELECT standard_price INTO product_value
                        FROM product_price_history
                        WHERE date <= inventory.from_date
                        AND template_id = inventory.product_tmpl_id
                        ORDER BY date DESC LIMIT 1;
                        
                        IF NOT FOUND THEN
                            UPDATE product_inventory_dates SET start_price=0.0 WHERE product_id=inventory.product_id;
                        ELSE
                            UPDATE product_inventory_dates SET start_price=product_value WHERE product_id=inventory.product_id;
                        END IF;
                        
                        -- End Price
                        product_value := 0;
                        SELECT standard_price INTO product_value
                        FROM product_price_history
                        WHERE date <= inventory.to_date
                        AND template_id = inventory.product_tmpl_id
                        ORDER BY date DESC LIMIT 1;
                        
                        IF NOT FOUND THEN
                            UPDATE product_inventory_dates SET end_price=0.0 WHERE product_id=inventory.product_id;
                        ELSE
                            UPDATE product_inventory_dates SET end_price=product_value WHERE product_id=inventory.product_id;
                        END IF;
                        
                    END LOOP;
                    RETURN 1;
                END;
                $$ LANGUAGE plpgsql;""")
            cr.commit()
        ###### /END: Create Stored Functions ######
    


    def compute_inventory(self, cr, uid, context=None):
        from_date = context.get('from_date','2013-04-01')
        to_date = context.get('to_date','2099-12-31')

        cr.execute("""TRUNCATE TABLE product_inventory_dates""")
        
        cr.execute("""INSERT INTO product_inventory_dates(product_id, product_tmpl_id, prod_active, from_date, to_date) 
                SELECT id, product_tmpl_id, active, %s, %s FROM product_product 
                ORDER BY default_code""", (from_date, to_date))

        cr.execute("""
                UPDATE product_inventory_dates AS i 
                SET code = p.default_code, uom_id = t.uom_id, category_id=t.categ_id, stock_type_id = t.stock_type_id,
                    scrap_qty=0.000, consume_qty=0.000, produce_qty=0.000, buy_qty=0.000,sale_qty=0.000
                FROM product_product p, product_template t
                WHERE i.product_id = p.id AND p.product_tmpl_id = t.id""")
        
        cr.execute("""SELECT * FROM set_product_inventory_dates_prices()""")
        
        #start
        cr.execute("""
                UPDATE product_inventory_dates 
                SET start_qty = sl.product_qty, start_value = round(coalesce((sl.product_qty * product_inventory_dates.start_price), 0.0),3) 
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),3) AS product_qty
                    FROM stock_move m
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state = 'done' AND m.date <= %s
                        AND m.location_id NOT IN (SELECT distinct d.id
                                                  FROM stock_warehouse w, stock_location h, stock_location d
                                                  WHERE w.lot_stock_id = h.id 
                                                      AND d.parent_left >= h.parent_left 
                                                      AND d.parent_right <= h.parent_right)
                        AND m.location_dest_id IN (SELECT distinct d.id 
                                                   FROM stock_warehouse w, stock_location h, stock_location d
                                                   WHERE w.lot_stock_id = h.id 
                                                       AND d.parent_left >= h.parent_left 
                                                       AND d.parent_right <= h.parent_right)
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory_dates.product_id = sl.product_id """, (from_date,))
        
        # Useless, no ?
        #cr.execute("""UPDATE product_inventory_dates SET start_qty = 0.0 WHERE coalesce(start_qty,0.0) = 0.0""")
        
        cr.execute("""
                UPDATE product_inventory_dates 
                SET start_qty = start_qty - sl.product_qty, start_value = start_value - round(coalesce((sl.product_qty * product_inventory_dates.start_price), 0.0),3)
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),3) AS product_qty
                    FROM stock_move m 
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state = 'done' AND m.date <= %s
                        AND m.location_id IN (SELECT distinct d.id  
                                              FROM stock_warehouse w, stock_location h, stock_location d
                                              WHERE w.lot_stock_id = h.id 
                                                  AND d.parent_left >= h.parent_left 
                                                  AND d.parent_right <= h.parent_right)
                        AND m.location_dest_id NOT IN (SELECT distinct d.id 
                                                       FROM stock_warehouse w, stock_location h, stock_location d 
                                                       WHERE w.lot_stock_id = h.id 
                                                           AND d.parent_left >= h.parent_left 
                                                           AND d.parent_right <= h.parent_right)
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory_dates.product_id = sl.product_id """, (from_date,))
        
        
        #end
        cr.execute("""
                UPDATE product_inventory_dates  
                SET end_qty = sl.product_qty, end_value = round(coalesce((sl.product_qty * product_inventory_dates.end_price), 0.0),3)
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),3) AS product_qty
                    FROM stock_move m
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state = 'done' AND m.date <= %s 
                        AND m.location_id NOT IN (SELECT distinct d.id 
                                                  FROM stock_warehouse w, stock_location h, stock_location d
                                                  WHERE w.lot_stock_id = h.id 
                                                      AND d.parent_left >= h.parent_left 
                                                      AND d.parent_right <= h.parent_right)
                        AND m.location_dest_id IN (SELECT distinct d.id 
                                                   FROM stock_warehouse w, stock_location h, stock_location d
                                                   WHERE w.lot_stock_id = h.id 
                                                       AND d.parent_left >= h.parent_left 
                                                       AND d.parent_right <= h.parent_right)
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory_dates.product_id = sl.product_id """, (to_date,))
        
        # Useless, no ?
        #cr.execute("""UPDATE product_inventory_dates SET end_qty = 0.0 WHERE coalesce(end_qty,0.0) = 0.0""")
        
        cr.execute("""
                UPDATE product_inventory_dates 
                SET end_qty = end_qty - sl.product_qty, end_value = end_value - round(coalesce((sl.product_qty * product_inventory_dates.end_price), 0.0),3)
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),3) AS product_qty
                    FROM stock_move m 
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state = 'done' AND m.date <= %s
                        AND m.location_id IN (SELECT distinct d.id 
                                              FROM stock_warehouse w, stock_location h, stock_location d
                                              WHERE w.lot_stock_id = h.id 
                                                  AND d.parent_left >= h.parent_left 
                                                  AND d.parent_right <= h.parent_right)
                        AND m.location_dest_id NOT IN (SELECT distinct d.id 
                                                       FROM stock_warehouse w, stock_location h, stock_location d
                                                       WHERE w.lot_stock_id = h.id 
                                                           AND d.parent_left >= h.parent_left 
                                                           AND d.parent_right <= h.parent_right)
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory_dates.product_id = sl.product_id """, (to_date,))
        
        
        #buy
        cr.execute("""
                UPDATE product_inventory_dates 
                SET buy_qty = sl.product_qty, buy_value = sl.product_value 
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor),0.0),3) AS product_qty,
                            round(coalesce(sum(m.amount_total), 0.0),3) AS product_value
                    FROM stock_move m
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state = 'done' AND m.date >= %s AND m.date <= %s
                        AND m.location_id IN (SELECT id FROM stock_location WHERE usage='supplier')
                        AND m.location_dest_id NOT IN (SELECT id FROM stock_location WHERE usage='supplier')
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory_dates.product_id = sl.product_id """, (from_date, to_date,))
        #po_price for return is negative
        cr.execute("""
                UPDATE product_inventory_dates 
                SET buy_qty = buy_qty - sl.product_qty, buy_value = buy_value + sl.product_value 
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor),0.0),3) AS product_qty,
                            round(coalesce(sum(m.amount_total), 0.0),3) AS product_value
                    FROM stock_move m
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state = 'done' AND m.date >= %s AND m.date <= %s
                        AND m.location_id NOT IN (SELECT id FROM stock_location WHERE usage='supplier')
                        AND m.location_dest_id IN (SELECT id FROM stock_location WHERE usage='supplier')
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory_dates.product_id = sl.product_id """, (from_date, to_date,))


        #sale
        cr.execute("""
                UPDATE product_inventory_dates 
                SET sale_qty = sl.product_qty, sale_value = sl.product_value 
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),3) AS product_qty,
                            round(coalesce(sum(m.product_qty * pu.factor / u.factor * m.price_unit), 0.0),3) AS product_value
                    FROM stock_move m
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state = 'done' AND m.date >= %s AND m.date <= %s
                        AND m.location_id NOT IN (SELECT id FROM stock_location WHERE usage='customer')
                        AND m.location_dest_id IN (SELECT id FROM stock_location WHERE usage='customer')
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory_dates.product_id = sl.product_id """, (from_date, to_date,))
        
        cr.execute("""
                UPDATE product_inventory_dates 
                SET sale_qty = sale_qty - sl.product_qty, sale_value = sale_value - sl.product_value 
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),3) AS product_qty,
                            round(coalesce(sum(m.product_qty * pu.factor / u.factor * m.price_unit), 0.0),3) AS product_value
                    FROM stock_move m
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state = 'done' AND m.date >= %s AND m.date <= %s
                        AND m.location_id IN (SELECT id FROM stock_location WHERE usage='customer')
                        AND m.location_dest_id NOT IN (SELECT id FROM stock_location WHERE usage='customer')
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory_dates.product_id = sl.product_id """, (from_date, to_date,))
        

        #scrap
        cr.execute("""
                UPDATE product_inventory_dates 
                SET scrap_qty = sl.product_qty, scrap_value = sl.product_value 
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),3) AS product_qty,
                            round(coalesce(sum(m.product_qty * pu.factor / u.factor * m.price_unit), 0.0),3) AS product_value
                    FROM stock_move m
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state = 'done' AND m.date >= %s AND m.date <= %s
                        AND m.location_id IN (SELECT id FROM stock_location WHERE usage='inventory')
                        AND m.location_dest_id NOT IN (SELECT id FROM stock_location WHERE usage='inventory')
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory_dates.product_id = sl.product_id """, (from_date, to_date,))
        
        cr.execute("""
                UPDATE product_inventory_dates 
                SET scrap_qty = scrap_qty - sl.product_qty, scrap_value = scrap_value - sl.product_value 
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),3) AS product_qty,
                            round(coalesce(sum(m.product_qty * pu.factor / u.factor * m.price_unit), 0.0),3) AS product_value
                    FROM stock_move m
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state = 'done' AND m.date >= %s AND m.date <= %s
                        AND m.location_id NOT IN (SELECT id FROM stock_location WHERE usage='inventory')
                        AND m.location_dest_id IN (SELECT id FROM stock_location WHERE usage='inventory')
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory_dates.product_id = sl.product_id """, (from_date, to_date,))


        #consume
        cr.execute("""
                UPDATE product_inventory_dates 
                SET consume_qty = sl.product_qty, consume_value = sl.product_value 
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),3) AS product_qty,
                            round(coalesce(sum(m.product_qty * pu.factor / u.factor * m.price_unit), 0.0),3) AS product_value
                    FROM stock_move m
                        --INNER JOIN mrp_production_move_ids mp on m.id = mp.move_id
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state = 'done' AND m.date >= %s AND m.date <= %s
                        AND m.location_id NOT IN (SELECT id FROM stock_location WHERE usage='production')
                        AND m.location_dest_id IN (SELECT id FROM stock_location WHERE usage='production')
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory_dates.product_id = sl.product_id """, (from_date, to_date,))
        
        cr.execute("""
                UPDATE product_inventory_dates 
                SET consume_qty = consume_qty - sl.product_qty, consume_value = consume_value - sl.product_value 
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),3) AS product_qty,
                            round(coalesce(sum(m.product_qty * pu.factor / u.factor * m.price_unit), 0.0),3) AS product_value
                    FROM stock_move m
                        --INNER JOIN mrp_production_move_ids mp on m.id = mp.move_id
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state = 'done' AND m.date >= %s AND m.date <= %s
                        AND m.location_id IN (SELECT id FROM stock_location WHERE usage='production')
                        AND m.location_dest_id NOT IN (SELECT id FROM stock_location WHERE usage='production')
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory_dates.product_id = sl.product_id """, (from_date, to_date,))


        #produce
        cr.execute("""
                UPDATE product_inventory_dates 
                SET produce_qty = sl.product_qty, produce_value = sl.product_value 
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),3) AS product_qty,
                            round(coalesce(sum(m.product_qty * pu.factor / u.factor * m.price_unit), 0.0),3) AS product_value
                    FROM stock_move m
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state = 'done' AND m.date >= %s AND m.date <= %s
                        AND m.production_id IS NOT NULL
                        AND m.location_id IN (SELECT id FROM stock_location WHERE usage='production')
                        AND m.location_dest_id NOT IN (SELECT id FROM stock_location WHERE usage='production')
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory_dates.product_id = sl.product_id """, (from_date, to_date,))
        
        cr.execute("""
                UPDATE product_inventory_dates 
                SET produce_qty = produce_qty - sl.product_qty, produce_value = produce_value - sl.product_value 
                FROM 
                    (SELECT m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),3) AS product_qty,
                            round(coalesce(sum(m.product_qty * pu.factor / u.factor * m.price_unit), 0.0),3) AS product_value
                    FROM stock_move m
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)  
                    WHERE m.state = 'done' AND m.date >= %s AND m.date <= %s
                        AND m.production_id IS NOT NULL
                        AND m.location_id NOT IN (SELECT id FROM stock_location WHERE usage='production')
                        AND m.location_dest_id IN (SELECT id FROM stock_location WHERE usage='production')
                    GROUP BY m.product_id ORDER BY m.product_id) sl
                WHERE product_inventory_dates.product_id = sl.product_id """, (from_date, to_date,))
        
        return True

product_inventory_dates()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
