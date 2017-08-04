# -*- coding: utf-8 -*-
# © 2011 SYLEAM Info Services (http://www.Syleam.fr)
# © 2011 Sylvain Garancher (sylvain.garancher@syleam.fr)
# © 2011 Sebastien LANGE (sebastien.lange@syleam.fr)
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.sql import drop_view_if_exists
#from openerp import decimal_precision as dp
from openerp.addons.decimal_precision import decimal_precision as dp

class wms_report_stock_available(osv.osv):
    """
    Display the stock available, per unit, production lot
    """
    _name = 'wms.report.stock.available'
    _description = 'Stock available'
    _auto = False
    _rec_name = 'product_id'

    _columns = {
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'uom_id': fields.many2one('product.uom', 'UOM', readonly=True),
        'prodlot_id': fields.many2one('stock.production.lot', 'Production lot', readonly=True),
        'location_id': fields.many2one('stock.location', 'Location', readonly=True),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', readonly=True),
        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM'), readonly=True),
        'usage': fields.char('Usage', size=16, help="""* Supplier Location: Virtual location representing the source location for products coming from your suppliers
                       \n* View: Virtual location used to create a hierarchical structures for your warehouse, aggregating its child locations ; can't directly contain products
                       \n* Internal Location: Physical locations inside your own warehouses,
                       \n* Customer Location: Virtual location representing the destination location for products sent to your customers
                       \n* Inventory: Virtual location serving as counterpart for inventory operations used to correct stock levels (Physical inventories)
                       \n* Procurement: Virtual location serving as temporary counterpart for procurement operations when the source (supplier or production) is not known yet. This location should be empty when the procurement scheduler has finished running.
                       \n* Production: Virtual counterpart location for production operations: this location consumes the raw material and produces finished products
                      """),
        'company_id': fields.many2many('res.company', 'Company'),
    }

    def init(self, cr):
        drop_view_if_exists(cr, 'wms_report_stock_available')
        cr.execute("""
                CREATE OR REPLACE VIEW wms_report_stock_available AS (
                    WITH RECURSIVE location(id, name, parent_id, warehouse_id) AS (
                                    select sw.lot_stock_id, ''::varchar, 0, sw.id
                                    FROM   stock_warehouse sw
                                    UNION
                                    SELECT sl.id, sl.name, sl.location_id, sl.warehouse_id FROM stock_location sl, location
                                    WHERE  sl.location_id = location.id)
                    SELECT  max(id) AS id,
                            (SELECT warehouse_id FROM stock_location WHERE id=report.location_id) AS warehouse_id,
                            location_id,
                            product_id,
                            (SELECT product_template.uom_id FROM product_product, product_template WHERE product_product.product_tmpl_id = product_template.id AND product_product.id = report.product_id) AS uom_id,
                            prodlot_id,
                            usage,
                            sum(qty) AS product_qty
                    FROM (
                           SELECT   -max(sm.id) AS id,
                                    sm.location_id,
                                    sm.product_id,
                                    sm.prodlot_id,
                                    sl.usage,
                                    -sum(sm.product_qty /uo.factor) AS qty
                           FROM stock_move as sm
                           LEFT JOIN stock_location sl ON (sl.id = sm.location_id)
                           LEFT JOIN product_uom uo ON (uo.id=sm.product_uom)
                           WHERE state = 'done' AND sm.location_id != sm.location_dest_id
                           GROUP BY sm.location_id, sm.product_id, sm.product_uom, sm.prodlot_id, sl.usage
                           UNION ALL
                           SELECT   max(sm.id) AS id,
                                    sm.location_dest_id AS location_id,
                                    sm.product_id,
                                    sm.prodlot_id,
                                    sl.usage,
                                    sum(sm.product_qty /uo.factor) AS qty
                           FROM stock_move AS sm
                           LEFT JOIN stock_location sl ON (sl.id = sm.location_dest_id)
                           LEFT JOIN product_uom uo ON (uo.id=sm.product_uom)
                           WHERE sm.state = 'done' AND sm.location_id != sm.location_dest_id
                           GROUP BY sm.location_dest_id, sm.product_id, sm.product_uom, sm.prodlot_id, sl.usage
                    ) AS report
                    GROUP BY location_id, product_id, prodlot_id, usage
                    HAVING sum(qty) > 0)
        """)

wms_report_stock_available()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
