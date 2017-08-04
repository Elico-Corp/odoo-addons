# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp


class product_product(orm.Model):
    _inherit = 'product.product'

    def get_kits_product_available(self, cr, uid, ids, context=None):
        pass

    def _kits_product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        res = {}
        field_names = field_names or []
        context = context or {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0.0)
        field_map = {
            'kits_qty_available': 'qty_available',
            'kits_incoming_qty': 'incoming_qty',
            'kits_outgoing_qty': 'outgoing_qty',
            'kits_virtual_available': 'virtual_available'
        }
        for product_record in self.browse(cr, uid, ids, context=context):
            #check if is a kit product.
            so_qty = self._get_sale_quotation_qty(cr, uid, product_record.id, context=context)
            if not self._is_kit(
                cr, uid,
                [product_record.id],
                    context=context).get(product_record.id):

                res[product_record.id] = {
                    'kits_qty_available': 0,
                    'kits_incoming_qty': 0,
                    'kits_virtual_available': 0,
                    'kits_outgoing_qty': 0,
                    'kits_sale_quotation_qty': so_qty
                }
            #product with no bom
            #TODO how to deal with multi-bom products.
            #now get always get the first bom.
            #product with bom
            else:
                for bom in product_record.bom_ids:
                    #bom type is phantom
                    #TODO take care of the valid date of the components
                    if bom.type == 'phantom':
                        child_product_res = {}
                        for line in bom.bom_lines:
                            child_product_res[line.product_id.id] = {'product_qty': line.product_qty or 0.0}
                        child_product_qtys = self._product_available(cr, uid, child_product_res.keys(), field_map.values(), context=context)
                        res[product_record.id] = {
                            'kits_qty_available': self._get_qty_from_children(child_product_qtys, child_product_res, 'qty_available'),
                            'kits_incoming_qty': self._get_qty_from_children(child_product_qtys, child_product_res, 'incoming_qty'),
                            'kits_virtual_available': self._get_qty_from_children(child_product_qtys, child_product_res, 'virtual_available') - so_qty,
                            'kits_outgoing_qty': self._get_qty_from_children(child_product_qtys, child_product_res, 'outgoing_qty'),
                            'kits_sale_quotation_qty': so_qty
                        }

                    else:
                        raw_res = self._product_available(cr, uid, ids, field_map.values(), arg, context)
                        for key, val in field_map.items():
                            res[product_record.id][key] = raw_res[product_record.id].get(val)

                    #only get the first bom.
                    break
        return res

    def _get_sale_quotation_qty(self, cr, uid, product_id, context=None):
        '''get all qty of the product in all sale quotations (draft, sent)'''
        sol_obj = self.pool.get('sale.order.line')
        domain = [('state', 'in', ('draft', False, None)), ('product_id', '=', product_id)]
        #TODO take care of the uom.
        sol_ids = sol_obj.read_group(cr, uid, domain, ['product_uom_qty', 'product_id'], groupby=['product_id'])
        return sol_ids and sol_ids[0].get('product_uom_qty') or 0.0

    def _get_qty_from_children(self, child_product_qtys, child_product_res, field_name):
        def qty_div(product_total_qty, component_qty):
            return product_total_qty[1].get(field_name) / component_qty[1].get('product_qty')
        return min(map(qty_div, child_product_qtys.iteritems(), child_product_res.iteritems()))

    def _is_kit(self, cr, uid, ids, fields=None, args=False, context=None):
        '''see if this product is Kit or not'''
        res = {}
        for product_record in self.browse(cr, uid, ids, context=context):
            res[product_record.id] = False
            if product_record.bom_ids:
                for bom in product_record.bom_ids:
                    if bom.type == 'phantom':
                        res[product_record.id] = True
        return res

    def _get_product_from_bom(self, cr, uid, ids, context=None):
        res = {}
        bom_ids = self.pool.get('mrp.bom').browse(cr, uid, ids, context=context)
        for bom in bom_ids:
            res[bom.product_id.id] = True
        return res.keys()

    _columns = {
        'is_kit': fields.function(
            _is_kit,
            readonly=True,
            type='boolean',
            string='Is Kit',
            store={
                'mrp.bom': (_get_product_from_bom, ['type'], 10)
            }),
        'kits_qty_available': fields.function(
            _kits_product_available,
            multi='kits_qty_available',
            type='float',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Quantity On Hand (Kits)',
            help=""),
        'kits_incoming_qty': fields.function(
            _kits_product_available,
            multi='kits_qty_available',
            type='float',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Incoming (Kits)',
            help=""),
        'kits_outgoing_qty': fields.function(
            _kits_product_available,
            multi='kits_qty_available',
            type='float',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Outgoing (Kits)',
            help=""),
        'kits_sale_quotation_qty': fields.function(
            _kits_product_available,
            multi='kits_qty_available',
            type='float',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Sales Quotation Allocated',
            help=""),
        'kits_virtual_available': fields.function(
            _kits_product_available,
            multi='kits_qty_available',
            type='float',
            digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Forecasted Quantity (Kits)',
            help=""),
    }
