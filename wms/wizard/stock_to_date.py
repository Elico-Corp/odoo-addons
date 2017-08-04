# -*- coding: utf-8 -*-
# © 2011 SYLEAM Info Services (http://www.Syleam.fr)
# © 2011 Sebastien LANGE (sebastien.lange@syleam.fr)
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import osv
from openerp.osv import fields
from openerp.addons.decimal_precision import decimal_precision as dp

from datetime import date
from dateutil.rrule import MO, FR
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _


class stock_to_date(osv.osv_memory):
    _name = 'stock.to.date'
    _description = 'Stock to date by product'
    _rec_name = 'product_id'

    def compute_stock_to_date(self, cr, uid, ids, context=None):
        """
        Compute total quantity on lines
        """
        product_obj = self.pool.get('product.product')
        line_obj = self.pool.get('stock.to.date.line')
        self.write(cr, uid, ids, {'stock_to_date_line_ids': [(5,)]}, context=context)

        for wizard in self.browse(cr, uid, ids, context=context):
            warehouse_ids = []
            if not wizard.warehouse_id:
                wids = self.pool.get('stock.warehouse').search(cr, uid, [], context=context)
                user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
                for w in self.pool.get('stock.warehouse').browse(cr, uid, wids, context=context):
                    if w.partner_address_id and w.partner_address_id.partner_id and user.company_id.partner_id == w.partner_address_id.partner_id:
                        warehouse_ids.append(w.id)
            else:
                warehouse_ids.append(wizard.warehouse_id.id)
            if not warehouse_ids:
                raise osv.except_osv(_('Warning !'), _('Please contact your administrator to configure warehouse in your profile.'))
            tuple_warehouse_ids = tuple(warehouse_ids)

            cr.execute(
                """
                SELECT distinct(date_move), product_id, warehouse_id
                FROM (
                    SELECT r.date::date AS date_move, r.product_id, %s AS warehouse_id
                    FROM stock_move r LEFT JOIN product_uom u ON (r.product_uom=u.id)
                    WHERE state IN ('confirmed','assigned','waiting','done','reserved')
                    AND product_id = %s
                    AND location_id IN (
                        WITH RECURSIVE location(id, parent_id) AS (
                        SELECT id, location_id FROM stock_location WHERE id IN (SELECT lot_stock_id FROM stock_warehouse WHERE id IN %s)
                        UNION
                        SELECT sl.id, sl.location_id FROM stock_location sl, location
                        WHERE  sl.location_id = location.id)
                        SELECT id FROM location)
                    AND location_dest_id NOT IN (
                        WITH RECURSIVE location(id, parent_id) AS (
                        SELECT id, location_id FROM stock_location WHERE id IN (SELECT lot_stock_id FROM stock_warehouse WHERE id IN %s)
                        UNION
                        SELECT sl.id, sl.location_id FROM stock_location sl, location
                        WHERE  sl.location_id = location.id)
                        SELECT id FROM location)
                    AND r.date::date >= %s AND r.date::date <= %s
                    GROUP BY r.date::date, product_id, warehouse_id
                    UNION ALL
                    SELECT r.date::date as date_move, r.product_id, %s AS warehouse_id
                    FROM stock_move r LEFT JOIN product_uom u on (r.product_uom=u.id)
                    WHERE state IN ('confirmed','assigned','waiting','done','reserved')
                    AND product_id = %s
                    AND location_dest_id IN (
                        WITH RECURSIVE location(id, parent_id) AS (
                        SELECT id, location_id FROM stock_location WHERE id IN (SELECT lot_stock_id FROM stock_warehouse WHERE id IN %s)
                        UNION
                        SELECT sl.id, sl.location_id FROM stock_location sl, location
                        WHERE  sl.location_id = location.id)
                        SELECT id FROM location)
                    AND location_id NOT IN (
                        WITH RECURSIVE location(id, parent_id) AS (
                        SELECT id, location_id FROM stock_location WHERE id IN (SELECT lot_stock_id FROM stock_warehouse WHERE id IN %s)
                        UNION
                        SELECT sl.id, sl.location_id FROM stock_location sl, location
                        WHERE  sl.location_id = location.id)
                        SELECT id FROM location)
                    AND r.date::date >= %s and r.date::date <= %s
                    GROUP BY r.date::date, product_id, warehouse_id
                ) subquery
                ORDER BY date_move ASC
                """,
                (
                    tuple_warehouse_ids,
                    wizard.product_id.id,
                    tuple_warehouse_ids,
                    tuple_warehouse_ids,
                    wizard.date_from,
                    wizard.date_to,
                    tuple_warehouse_ids,
                    wizard.product_id.id,
                    tuple_warehouse_ids,
                    tuple_warehouse_ids,
                    wizard.date_from,
                    wizard.date_to,
                )
            )

            results = cr.fetchall()
            today = date.today().strftime('%Y-%m-%d')
            ok = False
            for result in results:
                if today in result:
                    ok = True
                    break
            if not ok:
                results.append((today, wizard.product_id.id, warehouse_ids))
            for date_move, product_id, warehouse_ids in sorted(results):
                ctx = context.copy()
                if isinstance(warehouse_ids, (int, long)):
                    ctx.update({
                        'warehouse': warehouse_ids,
                    })
                elif warehouse_ids and len(warehouse_ids) == 1:
                    ctx.update({
                        'warehouse': warehouse_ids[0],
                    })
                ctx.update({
                    'to_date': date_move + ' 23:59:59',
                    'compute_child': True,
                })
                ctx2 = ctx.copy()
                ctx2.update({
                    'from_date': date_move + ' 00:00:00',
                })
                product = product_obj.browse(cr, uid, product_id, context=ctx)
                product2 = product_obj.browse(cr, uid, product_id, context=ctx2)
                line_obj.create(cr, uid, {
                    'stock_to_date_id': wizard.id,
                    'date': date_move,
                    'virtual_available': product.virtual_available,
                    'incoming_qty': product2.incoming_qty,
                    'outgoing_qty': product2.outgoing_qty * -1,
                    'color': date_move == today and True or False,
                }, context=context)
        return True

    def _get_orderpoint(self, cr, uid, ids, field_name, args, context=None):
        """
        Get orderpoint for this product
        """
        orderpoint_obj = self.pool.get('stock.warehouse.orderpoint')
        result = {}
        for wizard in self.browse(cr, uid, ids, context=context):
            result[wizard.id] = orderpoint_obj.search(cr, uid, [('product_id', '=', wizard.product_id.id)], context=context)
        return result

    def _get_report_stock(self, cr, uid, ids, field_name, args, context=None):
        """
        Get stock avalaible by location for this product
        """
        report_obj = self.pool.get('wms.report.stock.available')
        result = {}
        for wizard in self.browse(cr, uid, ids, context=context):
            result[wizard.id] = report_obj.search(cr, uid, [('usage', '=', 'internal'), ('product_id', '=', wizard.product_id.id)], context=context)
        return result

    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'uom_id': fields.related('product_id', 'uom_id', type='many2one', relation='product.uom', string='Default UoM'),
        'date_from': fields.date('Date start', required=True, help='Date start to compute stock'),
        'date_to': fields.date('Date End', required=True, help='Date end to compute stock'),
        'stock_to_date_line_ids': fields.one2many('stock.to.date.line', 'stock_to_date_id', 'Line of stock to date', readonly=True),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', required=False),
        'orderpoint_ids': fields.function(_get_orderpoint, method=True, string='OrderPoint', type='one2many', relation='stock.warehouse.orderpoint', store=False),
        'report_stock_ids': fields.function(_get_report_stock, method=True, string='Stock Available', type='one2many', relation='wms.report.stock.available', store=False),
    }

    def default_get(self, cr, uid, fields_list, context=None):
        """
        Automatically populate fields and lines when opening the wizard from the selected stock move
        """
        if context is None:
            context = {}
        product_obj = self.pool.get('product.product')

        # Call to super for standard behaviour
        values = super(stock_to_date, self).default_get(cr, uid, fields_list, context=context)

        # Retrieve current stock move from context
        product_id = 'default_product_id' in context and context['default_product_id'] or 'active_id' in context and context['active_id'] or False
        orderpoint_obj = self.pool.get('stock.warehouse.orderpoint')
        report_obj = self.pool.get('wms.report.stock.available')
        #user_obj = self.pool.get('res.users')
        #user = user_obj.browse(cr, uid, uid, context=context)
        if product_id:
            product = product_obj.browse(cr, uid, product_id, context=context)

            # Initialize values
            values['product_id'] = product.id
            values['stock_to_date_line_ids'] = []
            orderpoint_ids = orderpoint_obj.search(cr, uid, [('product_id', '=', product_id)], context=context)
            values['orderpoint_ids'] = orderpoint_obj.read(cr, uid, orderpoint_ids, [], context=context)
            report_stock_ids = report_obj.search(cr, uid, [('usage', '=', 'internal'), ('product_id', '=', product_id)], context=context)
            values['report_stock_ids'] = report_obj.read(cr, uid, report_stock_ids, [], context=context)
        #if user.context_stock2date_start:
        #    values['date_from'] = (date.today() + relativedelta(weekday=MO(user.context_stock2date_start))).strftime('%Y-%m-%d')
        #if user.context_stock2date_end:
        #    values['date_to'] = 'default_date_to' in context and context['default_date_to'] or (date.today() + relativedelta(weekday=FR(user.context_stock2date_end))).strftime('%Y-%m-%d')
        return values

stock_to_date()


class stock_to_date_line(osv.osv_memory):
    _name = 'stock.to.date.line'
    _description = 'Lines of stock to date'
    _order = 'date asc'

    _columns = {
        'stock_to_date_id': fields.many2one('stock.to.date', 'Stock To Date'),
        'date': fields.date('Date'),
        'virtual_available': fields.float('Virtual', digits_compute=dp.get_precision('Product UoM')),
        'incoming_qty': fields.float('Incoming', digits_compute=dp.get_precision('Product UoM')),
        'outgoing_qty': fields.float('Outgoing', digits_compute=dp.get_precision('Product UoM')),
        'color': fields.boolean('Color', help='Just for show color in today'),
        'empty': fields.char(' ', size=1),
    }

    _defaults = {
        'color': False,
    }

stock_to_date_line()



