# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import osv,fields
import time

from tools.translate import _
import decimal_precision as dp

class slowmove(osv.osv):
    _name = 'stock.slowmove'
    _description = 'Stock Slow Moving'
    _rec_name = "product_id"
    _order = 'rotation_rate desc, onhand_qty desc'

    _columns = {
        'product_id': fields.many2one('product.product', 'Products', required=True),     
        'category_id': fields.many2one('product.category', 'Product Category'),
        'onhand_qty': fields.float("Onhand Quantity"),
        'so_line_id': fields.many2one('sale.order.line', 'Last Sale Line'),
        'lasts_date': fields.date("Last Sale Date"),
        'lasts_qty': fields.float("Last Sale Quantity"),
        'po_line_id': fields.many2one('purchase.order.line', 'Last Purchase Line'),
        'lastp_date': fields.date("Last Purchase Date"),
        'lastp_qty': fields.float("Last Purchase Quantity"),
        'mo_id': fields.many2one('mrp.production', 'Last Production'),
        'lastm_date': fields.date("Last Production Date"),
        'lastm_qty': fields.float("Last Production Quantity"),
        'product_lastq_qty': fields.float('Last 6-Month Quantity'),
        'product_lasty_qty': fields.float('Last 12-Month Quantity',),
        'rotation_rate': fields.float('Sale Rotation (Month)',),
        'date': fields.date('Creation Date'),
        #add a new related field: categ1_id
        # [update 2014-07-14]<alex.duan@elico-corp.com>
        'categ1_id': fields.many2one('product.category', 'Product Category 1'),
        # 'categ1_id': fields.related(
        #     'product_id', 'categ1_id', readonly=True, type="many2one",
        #     relation="product.category",
        #     string="Product Category 1",
        #     store={
        #         'stock.slowmove': (
        #             lambda self, cr, uid, ids, c={}: ids, ['product_id'], 21),
        #         'product.product': (
        #             lambda self, cr, uid, ids, c={}: ids, ['categ1_id'], 21),
        #     }),
    }

    _defaults = {
        'product_lastq_qty': 0.0,
        'product_lasty_qty': 0.0,
        'rotation_rate': 0.0,
        'date': lambda *a: time.strftime('%Y-%m-%d'),
    }

    def process_slowmove(self, cr, uid, context={}):
        prod_obj = self.pool.get('product.product')
        cr.execute("""truncate table stock_slowmove""")
        cr.execute("""insert into stock_slowmove(id,product_id) select id,id from product_product where active and id in (select distinct product_id from stock_move ) order by id""")
        cr.execute("""
                        update stock_slowmove set so_line_id =sl.id from 
                            (select product_id, max(id) as id from sale_order_line group by product_id) sl
                        where stock_slowmove.product_id = sl.product_id """)
        cr.execute("""
                        update stock_slowmove set po_line_id =pl.id from 
                            (select product_id, max(id) as id from purchase_order_line group by product_id) pl
                        where stock_slowmove.product_id = pl.product_id """)
        cr.execute("""
                        update stock_slowmove set mo_id =m.id from 
                            (select product_id, max(id) as id from mrp_production group by product_id) m
                        where stock_slowmove.product_id = m.product_id """)

        cr.execute("""
                        update stock_slowmove set product_lastq_qty =sl.qty from 
                            (select d.product_id, sum(d.product_uom_qty) as qty from sale_order_line d 
                                inner join sale_order h on d.order_id = h.id
                                where current_date - 183 <= h.date_order group by d.product_id) sl
                        where stock_slowmove.product_id = sl.product_id """)
        cr.execute("""
                        update stock_slowmove set product_lasty_qty =sl.qty from 
                            (select d.product_id, sum(d.product_uom_qty) as qty from sale_order_line d 
                                inner join sale_order h on d.order_id = h.id
                                where current_date - 365 <= h.date_order group by d.product_id) sl
                        where stock_slowmove.product_id = sl.product_id """)

        cr.execute("""
                        update stock_slowmove set lasts_qty = d.product_uom_qty, lasts_date = h.date_order
                        from sale_order_line d,sale_order h 
                        where stock_slowmove.so_line_id = d.id and d.order_id = h.id """)

        cr.execute("""
                        update stock_slowmove set lastp_qty = d.product_qty, lastp_date = h.date_order
                        from purchase_order_line d,purchase_order h 
                        where stock_slowmove.po_line_id = d.id and d.order_id = h.id """)

        cr.execute("""
                        update stock_slowmove set lastm_qty = d.product_qty, lastm_date = coalesce(d.date_finished,d.date_planned)
                        from mrp_production d
                        where stock_slowmove.mo_id = d.id """)
        
        cr.execute("""
                        update stock_slowmove set onhand_qty = sl.product_qty from 
                            (Select m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),4) as product_qty
            FROM
                stock_move m
                    LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                    LEFT JOIN product_uom u ON (m.product_uom=u.id)  
            where m.state = 'done'
            and m.location_id not in (select  distinct d.id  from stock_warehouse w, stock_location h, stock_location d
             where w.company_id = 3 and w.lot_stock_id = h.id and d.parent_left >= h.parent_left and d.parent_right <= h.parent_right)
        
                and m.location_dest_id in (select  distinct d.id  from stock_warehouse w, stock_location h, stock_location d
             where w.company_id = 3 and w.lot_stock_id = h.id and d.parent_left >= h.parent_left and d.parent_right <= h.parent_right)
            GROUP BY m.product_id
        order by m.product_id) sl
                        where stock_slowmove.product_id = sl.product_id """)
        
        cr.execute("""
                        update stock_slowmove set onhand_qty = 0.0 where coalesce(onhand_qty,0.0) = 0.0
                """)
        cr.execute("""
                        update stock_slowmove set onhand_qty = onhand_qty- sl.product_qty from 
                            (Select m.product_id, round(coalesce(sum(m.product_qty * pu.factor / u.factor), 0.0),4) as product_qty
            FROM
                stock_move m
                    LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                    LEFT JOIN product_uom u ON (m.product_uom=u.id)  
            where m.state = 'done'
            and m.location_id in (select  distinct d.id  from stock_warehouse w, stock_location h, stock_location d
             where w.company_id = 3 and w.lot_stock_id = h.id and d.parent_left >= h.parent_left and d.parent_right <= h.parent_right)
        
                and m.location_dest_id not in (select  distinct d.id  from stock_warehouse w, stock_location h, stock_location d
             where w.company_id = 3 and w.lot_stock_id = h.id and d.parent_left >= h.parent_left and d.parent_right <= h.parent_right)
            GROUP BY m.product_id
        order by m.product_id) sl
                        where stock_slowmove.product_id = sl.product_id """)  
        
        cr.execute("""
                        update stock_slowmove set onhand_qty = 0.0 where coalesce(onhand_qty,0.0) = 0.0
                """)      

        cr.execute("""
                        update stock_slowmove set date = current_date, rotation_rate = CASE WHEN product_lasty_qty is null Then 9999.99 ELSE 12 * onhand_qty / product_lasty_qty end
                """)
        cr.execute("""
                        update stock_slowmove set category_id = t.categ_id from product_product p, product_template t where product_id = p.id and p.product_tmpl_id = t.id
                """)
        cr.execute("""
                        update stock_slowmove set categ1_id = t.categ1_id from product_product p, product_template t where product_id = p.id and p.product_tmpl_id = t.id
                """)
        
        cr.execute("""
                        update stock_slowmove set rotation_rate = 0.0 where coalesce(rotation_rate,0.0) = 0.0
                """)         
        return True

slowmove()
