# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Chen rong <chen.rong@elico-corp.com>

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import date, datetime
from dateutil import relativedelta
import json
import time

from openerp.osv import fields, osv
from openerp.tools.float_utils import float_compare, float_round
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import SUPERUSER_ID, api
import openerp.addons.decimal_precision as dp
from openerp.addons.procurement import procurement
import logging

class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'
    _columns = {
        'supplier_seiral_no': fields.char(string='Supplier Lot No',size=100, select=True),
        'vlidity_from':fields.date(u'有效期从'),
        'vlidity_to':fields.date(u'有效期至'),
        'reinspec_way':fields.char(u'复验方式',size=16),
        'production_date':fields.date(u'生产日期'),
        'reinspec_number':fields.char(u'交验记录单编号',size=16),
        'production_batch':fields.char(u'生产批次'),
        'structure_level':fields.char(u'结构级别'),
        'usage_mode':fields.char(u'使用方式'),
        'concession_or_replace_number':fields.char(u'让步/代用单号'),
        'meterial_plan_status':fields.char(u'物资计划状态'),
        'meterial_quality_status':fields.char(u'物资质量状态'),
        'quality_info_number':fields.char(u'质量信息单编号'),
        'special_requirement':fields.char(u'特殊要求'),
        'material':fields.char(u"材料",size=100),
        'design_quality':fields.char(u"设计质量",size=100),
        'product_category':fields.char(u"类别",size=100),
    }

class stock_quant(osv.osv):
    _inherit = 'stock.quant'
    _columns = {
        'supplier_seiral_no': fields.related('lot_id','supplier_seiral_no',type='char',relation='stock.production.lot',string='Supplier Lot No',readonly=True, select=True,store=True),
        'vlidity_from': fields.related('lot_id','vlidity_from',type='date',relation='stock.production.lot',string='有效期从',readonly=True, select=True,store=True),
        'vlidity_to': fields.related('lot_id','vlidity_to',type='date',relation='stock.production.lot',string='有效期至',readonly=True, select=True,store=True),
        'reinspec_way': fields.related('lot_id','reinspec_way',type='char',relation='stock.production.lot',string='复验方式',readonly=True, select=True,store=True),
        'production_date': fields.related('lot_id','production_date',type='date',relation='stock.production.lot',string='生产日期',readonly=True, select=True,store=True),
        'reinspec_number': fields.related('lot_id','reinspec_number',type='char',relation='stock.production.lot',string='交验记录单编号',readonly=True, select=True,store=True),
        'production_batch': fields.related('lot_id','production_batch',type='char',relation='stock.production.lot',string='生产批次',readonly=True, select=True,store=True),
        'structure_level': fields.related('lot_id','structure_level',type='char',relation='stock.production.lot',string='结构级别',readonly=True, select=True,store=True),
        'concession_or_replace_number': fields.related('lot_id','concession_or_replace_number',type='char',relation='stock.production.lot',string='让步/代用单号',readonly=True, select=True,store=True),
        'usage_mode': fields.related('lot_id','usage_mode',type='char',relation='stock.production.lot',string='物资计划状态',readonly=True, select=True,store=True),
        'meterial_plan_status': fields.related('lot_id','meterial_plan_status',type='char',relation='stock.production.lot',string='物资计划状态',readonly=True, select=True,store=True),
        'meterial_quality_status': fields.related('lot_id','meterial_quality_status',type='char',relation='stock.production.lot',string='物资计划状态',readonly=True, select=True,store=True),
        'quality_info_number': fields.related('lot_id','quality_info_number',type='char',relation='stock.production.lot',string='质量信息单编号',readonly=True, select=True,store=True),
        'special_requirement': fields.related('lot_id','special_requirement',type='char',relation='stock.production.lot',string='特殊要求',readonly=True, select=True,store=True),
        'material': fields.related('lot_id','material',type='char',relation='stock.production.lot',string='材料',readonly=True, select=True,store=True),
        'design_quality': fields.related('lot_id','design_quality',type='char',relation='stock.production.lot',string='设计质量',readonly=True, select=True,store=True),
        'product_category': fields.related('lot_id','product_category',type='char',relation='stock.production.lot',string='类别',readonly=True, select=True,store=True),
    }

class stock_move(osv.osv):
    _inherit = 'stock.move'
    #单位统一，不需要换算，只作为产品描述
    _columns = {
        'supplier_seiral_no': fields.related('restrict_lot_id','supplier_seiral_no',type='char',relation='stock.production.lot',string='Supplier Lot No',select=True),
        'uom_description': fields.char(u"单位",size=16),
        'is_transfer': fields.boolean(u"发货"),
        'loc_rack': fields.related('product_id','loc_rack',type='char',relation='product.product',string=u'货架',readonly=True),
    }

    def create_and_assign_lot(self, cr, uid, product_id,name=False, context=None):
        ''' Used by barcode interface to create a new lot and assign it to the move
        '''

        val = {'product_id': product_id}
        new_lot_id = False
        if name:
            lots = self.pool.get('stock.production.lot').search(cr, uid, ['&', ('name', '=', name), ('product_id', '=', product_id)], context=context)
            if lots:
                new_lot_id = lots[0]
            else:
                val.update({'name': name})

        if not new_lot_id:
            new_lot_id = self.pool.get('stock.production.lot').create(cr, uid, val, context=context)
        return {'restrict_lot_id':new_lot_id}

    def create(self, cr, uid, vals, context=None):
        """Auto create lot no when picking type is receive material from supplier"""

        picking_id = vals.get('picking_id',False)
        picking_type_id = vals.get('picking_type_id',False)
        product_id = vals.get('product_id',False)
        restrict_lot_id = vals.get('restrict_lot_id',False)

        if picking_id:
            if product_id and not restrict_lot_id and picking_type_id:
                #判断是否需要自动创建序列号
                if self.pool.get('stock.picking.type').browse(cr, uid,picking_type_id, context=context)['auto_create_lot']:
                    val = self.create_and_assign_lot(cr, uid,product_id, context=context)
                    vals.update(val)
            #if vals.get('state','draft')=='draft':
            #    vals.update({'state': 'confirmed',})

        return super(stock_move, self).create(cr, uid, vals, context=context)

    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False, loc_dest_id=False, partner_id=False):
        vals = {}
        if prod_id:
            vals = super(stock_move, self).onchange_product_id(cr, uid, ids, prod_id, loc_id, loc_dest_id, partner_id)

            product = self.pool.get('product.product').browse(cr, uid, [prod_id])[0]
            uom_description = product.uom_description or ''
            
            if vals.get('value',False):
                vals['value'].update({'uom_description':uom_description})
        return vals

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def _state_get(self, cr, uid, ids, field_name, arg, context=None):
        res = super(stock_picking, self)._state_get(cr, uid, ids, field_name, arg, context=context)
        if isinstance(ids, (int, long)):
            ids = [ids]

        for picking in self.browse(cr, uid, ids, context=context):
            scan_operation_type = picking.picking_type_id.scan_operation_type or '1'
            if scan_operation_type == "3":
                if res.get(picking.id,False) =="draft":
                    res.update({picking.id:'assigned'})

        return res

    def _get_pickings(self, cr, uid, ids, context=None):
        res = set()
        for move in self.browse(cr, uid, ids, context=context):
            if move.picking_id:
                res.add(move.picking_id.id)
        return list(res)

    _columns = {
        'state': fields.function(_state_get, type="selection", copy=False,
            store={
                'stock.picking': (lambda self, cr, uid, ids, ctx: ids, ['move_type'], 20),
                'stock.move': (_get_pickings, ['state', 'picking_id', 'partially_available'], 20)},
            selection=[
                ('draft', 'Draft'),
                ('cancel', 'Cancelled'),
                ('waiting', 'Waiting Another Operation'),
                ('confirmed', 'Waiting Availability'),
                ('partially_available', 'Partially Available'),
                ('assigned', 'Ready to Transfer'),
                ('done', 'Transferred'),
                ], string='Status', readonly=True, select=True, track_visibility='onchange',
            help="""
                * Draft: not confirmed yet and will not be scheduled until confirmed\n
                * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
                * Waiting Availability: still waiting for the availability of products\n
                * Partially Available: some products are available and reserved\n
                * Ready to Transfer: products reserved, simply waiting for confirmation.\n
                * Transferred: has been processed, can't be modified or cancelled anymore\n
                * Cancelled: has been cancelled, can't be confirmed anymore"""
        ),
    }
    _order="create_date desc"

    @api.cr_uid_ids_context
    def open_barcode_interface(self, cr, uid, picking_ids, context=None):
        final_url="/barcode/web/?&debug#action=stock.ui&picking_id="+str(picking_ids[0])
        return {'type': 'ir.actions.act_url', 'url':final_url, 'target': '_blank','style':'height=500,width=600,toolbar=0,menubar=0'}

    def _prepare_pack_ops(self, cr, uid, picking, quants, forced_qties, context=None):
        """ returns a list of dict, ready to be used in create() of stock.pack.operation.

        :param picking: browse record (stock.picking)
        :param quants: browse record list (stock.quant). List of quants associated to the picking
        :param forced_qties: dictionary showing for each product (keys) its corresponding quantity (value) that is not covered by the quants associated to the picking
        """
        def _picking_putaway_apply(product):
            location = False
            # Search putaway strategy
            if product_putaway_strats.get(product.id):
                location = product_putaway_strats[product.id]
            else:
                location = self.pool.get('stock.location').get_putaway_strategy(cr, uid, picking.location_dest_id, product, context=context)
                product_putaway_strats[product.id] = location
            return location or picking.location_dest_id.id

        # If we encounter an UoM that is smaller than the default UoM or the one already chosen, use the new one instead.
        product_uom = {} # Determines UoM used in pack operations
        for move in picking.move_lines:
            if not product_uom.get(move.product_id.id):
                product_uom[move.product_id.id] = move.product_id.uom_id
            if move.product_uom.id != move.product_id.uom_id.id and move.product_uom.factor > product_uom[move.product_id.id].factor:
                product_uom[move.product_id.id] = move.product_uom

        pack_obj = self.pool.get("stock.quant.package")
        quant_obj = self.pool.get("stock.quant")
        vals = []
        qtys_grouped = {}
        #for each quant of the picking, find the suggested location
        quants_suggested_locations = {}
        product_putaway_strats = {}
        for quant in quants:
            if quant.qty <= 0:
                continue
            suggested_location_id = _picking_putaway_apply(quant.product_id)
            quants_suggested_locations[quant] = suggested_location_id

        #find the packages we can movei as a whole
        top_lvl_packages = self._get_top_level_packages(cr, uid, quants_suggested_locations, context=context)
        # and then create pack operations for the top-level packages found
        for pack in top_lvl_packages:
            pack_quant_ids = pack_obj.get_content(cr, uid, [pack.id], context=context)
            pack_quants = quant_obj.browse(cr, uid, pack_quant_ids, context=context)
            vals.append({
                    'picking_id': picking.id,
                    'package_id': pack.id,
                    'product_qty': 1.0,
                    'location_id': pack.location_id.id,
                    'location_dest_id': quants_suggested_locations[pack_quants[0]],
                    'owner_id': pack.owner_id.id,
                })
            #remove the quants inside the package so that they are excluded from the rest of the computation
            for quant in pack_quants:
                del quants_suggested_locations[quant]

        # Go through all remaining reserved quants and group by product, package, lot, owner, source location and dest location
        for quant, dest_location_id in quants_suggested_locations.items():
            key = (quant.product_id.id, quant.package_id.id, quant.lot_id.id, quant.owner_id.id, quant.location_id.id, dest_location_id)
            if qtys_grouped.get(key):
                qtys_grouped[key] += quant.qty
            else:
                qtys_grouped[key] = quant.qty
        
        # Do the same for the forced quantities (in cases of force_assign or incomming shipment for example)
        for product, qty in forced_qties.items():
            if qty <= 0:
                continue
            suggested_location_id = _picking_putaway_apply(product[0])
            #*****add by xie xiaopeng 2015.04.16 for add lot no*****#
            #key = (product.id, False, False, picking.owner_id.id, picking.location_id.id if picking.location_id.id else picking.picking_type_id.default_location_src_id.id, suggested_location_id)
            key = (product[0].id, False, product[1].id, picking.owner_id.id, picking.location_id.id if picking.location_id.id else picking.picking_type_id.default_location_src_id.id, suggested_location_id)
            #*****end add by xie xiaopeng 2015.04.16 for add lot no*****#
            if qtys_grouped.get(key):
                qtys_grouped[key] += qty
            else:
                qtys_grouped[key] = qty

        # Create the necessary operations for the grouped quants and remaining qtys
        uom_obj = self.pool.get('product.uom')
        prevals = {}
        for key, qty in qtys_grouped.items():
            product = self.pool.get("product.product").browse(cr, uid, key[0], context=context)
            uom_id = product.uom_id.id
            qty_uom = qty
            if product_uom.get(key[0]):
                uom_id = product_uom[key[0]].id
                qty_uom = uom_obj._compute_qty(cr, uid, product.uom_id.id, qty, uom_id)
            val_dict = {
                'picking_id': picking.id,
                'product_qty': qty_uom,
                'product_id': key[0],
                'package_id': key[1],
                'lot_id': key[2],
                'owner_id': key[3],
                'location_id': key[4],
                'location_dest_id': key[5],
                'product_uom_id': uom_id,
            }
            if key[0] in prevals:
                prevals[key[0]].append(val_dict)
            else:
                prevals[key[0]] = [val_dict]
        # prevals var holds the operations in order to create them in the same order than the picking stock moves if possible
        processed_products = set()
        for move in picking.move_lines:
            if move.product_id.id not in processed_products:
                vals += prevals.get(move.product_id.id, [])
                processed_products.add(move.product_id.id)
        return vals

    @api.cr_uid_ids_context
    def do_prepare_partial(self, cr, uid, picking_ids, context=None):

        context = context or {}
        pack_operation_obj = self.pool.get('stock.pack.operation')
        #used to avoid recomputing the remaining quantities at each new pack operation created
        ctx = context.copy()
        ctx['no_recompute'] = True

        picking = self.pool.get('stock.picking').browse(cr, uid, picking_ids[0], context=context)
        scan_operation_type = picking.picking_type_id.scan_operation_type or '1'
        #判断是否需要自动创建序列号
        #if scan_operation_type=='1':
        #    return

        #get list of existing operations and delete them
        existing_package_ids = pack_operation_obj.search(cr, uid, [('picking_id', 'in', picking_ids),('processed','=','false')], context=context)
        if existing_package_ids:
            pack_operation_obj.unlink(cr, uid, existing_package_ids, context)
        for picking in self.browse(cr, uid, picking_ids, context=context):
            forced_qties = {}  # Quantity remaining after calculating reserved quants
            picking_quants = []
            #Calculate packages, reserved quants, qtys of this picking's moves
            for move in picking.move_lines:
                if picking.picking_type_id.partial_delivey and not move.is_transfer:
                    continue
                if move.state not in ('assigned', 'confirmed'):
                    continue

                #******modified by xie xiaopeng 20150411 for sync move and operation**********#
                #move_quants = move.reserved_quant_ids
                #picking_quants += move_quants
                #forced_qty = (move.state == 'assigned') and move.product_qty - sum([x.qty for x in move_quants]) or 0
                
                opteration_ids = [x.operation_id.id for x in move.linked_move_operation_ids]
                scaned_ids =  pack_operation_obj.search(cr, uid, [('picking_id', 'in', picking_ids),('id','in',opteration_ids),('processed','=','true')], context=context)
                scaned_operation = pack_operation_obj.browse(cr, uid, scaned_ids,context=context)
                forced_qty = (move.state == 'assigned') and move.product_qty - sum([x.qty_done for x in scaned_operation]) or 0
                #******end modified by xie xiaopeng 20150411 sync move and operation**********#

                #if we used force_assign() on the move, or if the move is incoming, forced_qty > 0
                if float_compare(forced_qty, 0, precision_rounding=move.product_id.uom_id.rounding) > 0:
                    #*****add by xie xiaopeng 2015.04.16 for add lot no*****#
                    key = (move.product_id,move.restrict_lot_id)
                    if forced_qties.get(key):
                        forced_qties[key] += forced_qty
                    else:
                        forced_qties[key] = forced_qty
                    #*****end add by xie xiaopeng 2015.04.16 for add lot no*****#

            for vals in self._prepare_pack_ops(cr, uid, picking, picking_quants, forced_qties, context=context):
                pack_operation_obj.create(cr, uid, vals, context=ctx)
        #recompute the remaining quantities all at once
        
        self.do_recompute_remaining_quantities(cr, uid, picking_ids, context=context)
        self.write(cr, uid, picking_ids, {'recompute_pack_op': False}, context=context)

    def _prepare_values_extra_move(self, cr, uid, op, product, remaining_qty, context=None):
        """
        Creates an extra move when there is no corresponding original move to be copied
        """
        uom_obj = self.pool.get("product.uom")
        uom_id = product.uom_id.id
        qty = remaining_qty
        if op.product_id and op.product_uom_id and op.product_uom_id.id != product.uom_id.id:
            if op.product_uom_id.factor > product.uom_id.factor: #If the pack operation's is a smaller unit
                uom_id = op.product_uom_id.id
                #HALF-UP rounding as only rounding errors will be because of propagation of error from default UoM
                qty = uom_obj._compute_qty_obj(cr, uid, product.uom_id, remaining_qty, op.product_uom_id, rounding_method='HALF-UP')
        picking = op.picking_id
        res = {
            'picking_id': picking.id,
            #*****modifed by xie xiaopeng 2015.04.10 for when picking not have move items***/
            #'location_id': picking.location_id.id, 
            #'location_dest_id': picking.location_dest_id.id,

            'location_id': picking.location_id.id if picking.location_id.id else picking.picking_type_id.default_location_src_id.id, 
            'location_dest_id': picking.location_dest_id.id if picking.location_dest_id.id else picking.picking_type_id.default_location_dest_id.id, 
            'restrict_lot_id':op.lot_id.id,
            #*****modifed by xie xiaopeng 2015.04.10 for when picking not have move items***/
            'product_id': product.id,
            'product_uom': uom_id,
            'product_uom_qty': qty,
            'name': _('Extra Move: ') + product.name,
            'state': 'draft',
            }
        return res

    @api.cr_uid_ids_context
    def do_enter_transfer_details(self, cr, uid, picking, context=None):
        """check qty before transfer"""
        
        for picking_id in picking:
            pick = self.browse(cr, uid, picking_id, context=context)
            scan_operation_type = pick.picking_type_id.scan_operation_type

            if scan_operation_type in ['2','4']:#扫描时核对产品数量
                for move in pick.move_lines:
                    linked_move_operation_ids = self.pool.get('stock.move.operation.link').search_read(cr, uid, [('move_id', '=', move.id)], ['operation_id'])
                    linked_move_operation_ids = [x['operation_id'][0] for x in linked_move_operation_ids]
                    linked_move_operation_ids = list(set(linked_move_operation_ids))#去掉重复的值
                    linked_move_operation = self.pool.get('stock.pack.operation').search_read(cr,uid,[('id', 'in', linked_move_operation_ids),('processed','=','true')], ['qty_done'], context=context)
                    scaned_qty = sum([x['qty_done'] for x in linked_move_operation]) or 0.0
                    if move.product_uos_qty != scaned_qty:
                        raise osv.except_osv(_('Error'),u'扫描数量和出库数量不一致!')

        return super(stock_picking, self).do_enter_transfer_details(cr, uid, picking, context=context)

    def process_product_id_from_ui(self, cr, uid, picking_id, product_id, op_id, increment=True, context=None):
        return
        
    def action_assign(self, cr, uid, ids, context=None):
        """ Check availability of picking moves.
        This has the effect of changing the state and reserve quants on available moves, and may
        also impact the state of the picking as it is computed based on move's states.
        @return: True
        """

        for pick in self.browse(cr, uid, ids, context=context):
            if pick.state == 'draft':
                self.action_confirm(cr, uid, [pick.id], context=context)
            #skip the moves that don't need to be checked
            move_ids = [x.id for x in pick.move_lines if x.state not in ('draft', 'cancel', 'done')]
            #*******add by xie xiaopeng 20150412**********#
            #if not move_ids:
            #    raise osv.except_osv(_('Warning!'), _('Nothing to check the availability for.'))
            #*******end add by xie xiaopeng 20150412**********#
            if move_ids:
                self.pool.get('stock.move').action_assign(cr, uid, move_ids, context=context)
        return True

    def process_barcode_from_ui(self, cr, uid, picking_id, barcode_str, visible_op_ids, context=None):
        answer = super(stock_picking, self).process_barcode_from_ui(cr, uid, picking_id, barcode_str, visible_op_ids, context=context)
        if barcode_str and not answer['operation_id']:
            raise osv.except_osv(u'扫描的序列号[%s]不存在!'%barcode_str,'')

        return answer

class stock_pack_operation(osv.osv):
    _inherit = 'stock.pack.operation'

    _columns = {
        'supplier_seiral_no': fields.related('lot_id','supplier_seiral_no',type='char',relation='stock.production.lot',string='Supplier Lot No',select=True),
        'uom_description':fields.char(u"单位",size=4),
    }

    def check_operation(self, cr, uid, picking_id,product_id,lot_id=False,increment=True,context=None):
        product = self.pool.get("product.product").browse(cr,uid,product_id,context=context)
        picking = self.pool.get("stock.picking").browse(cr, uid, picking_id, context=context)
        scan_operation_type = picking.picking_type_id.scan_operation_type
        lot = lot_id
        #检查扫描的产品是否在出库列表，不在时不允许扫描
        if scan_operation_type in [False, '1']:
            raise osv.except_osv(_(u'提示'),u'目前的设置是不需要扫描，请修改扫描动作类型!')
        if scan_operation_type in ['2','4'] and lot_id > 0:#扫描时核对产品
            if scan_operation_type == '2':
                lot = False
            domain = [['picking_id', '=', picking_id],['product_id','=',product_id],['lot_id','=',lot],['product_qty','>',0]]
            group_res = self.read_group(cr, uid, domain, ['product_qty','qty_done', 'lot_id'], ['lot_id'])
            noscan_qty = sum([x['product_qty'] - x['qty_done'] for x in group_res if x['product_qty'] >0]) or 0.0
            
            if noscan_qty <=0:
                if lot:
                    lot = self.pool.get('stock.production.lot').browse(cr, uid, lot, context=context)
                    raise osv.except_osv(_(u'核对序列号错误'),u',可能单据明细里面没有产品[%s],序列号[%s]或者已经扫描完毕!'%(product.name, lot.name))
                else:
                    raise osv.except_osv(_(u'核对产品错误'),u'可能单据明细里面没有产品[%s]或者已经扫描完毕!'%product.name)

        #同一张单一个序列号只能扫描一个数量
        if increment and product.uom_type == "one":
            operations = self.search_read(cr, uid, [('picking_id', '=', picking_id),('product_id','=',product_id),('lot_id','=',lot_id),('qty_done','>',0)],['qty_done'], context=context)
            scaned_qty = sum([x['qty_done'] for x in operations]) or 0.0
            if scaned_qty >=1:
                raise osv.except_osv(_('Error'),u'产品[%s]一个序列号只能扫描一个数量!'%product.name)

    def update_origin_operation_qty(self, cr, uid, picking_id,product_id,increment=True, context=None):
        #修改原出库的数量
        origin_operation_ids = False
        origin_operation_ids = self.search(cr, uid, [('picking_id', '=', picking_id),('product_id','=',product_id),('lot_id','=',False),('product_qty','>',0)], context=context)
        if origin_operation_ids:
            origin_operation_id = origin_operation_ids[0]
            op_obj = self.browse(cr, uid, origin_operation_id, context=context)
            qty = op_obj.product_qty
            if increment:
                qty -= 1 if qty >= 1 else 0
            elif not increment:
                qty +=1

            if qty == 0 and op_obj.qty_done == 0:
                #we have a line with 0 qty set, so delete it
                self.unlink(cr, uid, [origin_operation_id], context=context)
            else:
                self.write(cr, uid, [origin_operation_id], {'product_qty': qty}, context=context)

    def _search_and_increment(self, cr, uid, picking_id, domain, filter_visible=False, visible_op_ids=False, increment=True, context=None):
        '''Search for an operation with given 'domain' in a picking, if it exists increment the qty (+1) otherwise create it

        :param domain: list of tuple directly reusable as a domain
        context can receive a key 'current_package_id' with the package to consider for this operation
        returns True
        '''
        if context is None:
            context = {}

        product_id = False
        lot_id = False
        for key in domain:
            var_name, dummy, value = key
            if var_name == 'product_id':
                product_id = value
            if var_name == 'lot_id':
                lot_id = value

        self.check_operation(cr, uid, picking_id,product_id,lot_id,increment, context=None)        

        #if current_package_id is given in the context, we increase the number of items in this package
        package_clause = [('result_package_id', '=', context.get('current_package_id', False))]
        existing_operation_ids = self.search(cr, uid, [('picking_id', '=', picking_id)] + domain + package_clause, context=context)
        todo_operation_ids = []

        if existing_operation_ids:
            if filter_visible:
                todo_operation_ids = [val for val in existing_operation_ids if val in visible_op_ids]
            else:
                todo_operation_ids = existing_operation_ids
        picking = self.pool.get("stock.picking").browse(cr, uid, picking_id, context=context)
        scan_operation_type = picking.picking_type_id.scan_operation_type
        if todo_operation_ids:
            #existing operation found for the given domain and picking => increment its quantity
            operation_id = todo_operation_ids[0]
            op_obj = self.browse(cr, uid, operation_id, context=context)
            qty = op_obj.qty_done
            if increment:
                qty += 1
            else:
                qty -= 1 if qty >= 1 else 0
                if qty == 0 and op_obj.product_qty == 0:
                    #we have a line with 0 qty set, so delete it
                    self.unlink(cr, uid, [operation_id], context=context)
                    return False

            context.update({'increment':increment, 'no_recompute': True}) # 不加no_recompute时，速度很慢
            vals = {'qty_done': qty}
            if scan_operation_type in ['2', '3']:
                vals.update({'product_qty': qty})
            self.write(cr, uid, [operation_id], vals, context=context)
        else:
            #no existing operation found for the given domain and picking => create a new one
            if scan_operation_type in ['1','4']:#不新增扫描操作
                return 

            values = {
                'picking_id': picking_id,
                'product_qty': 0,
                #*****modifed by xie xiaopeng 2015.04.10 for when picking not have move items***/
                #'location_id': picking.location_id.id, 
                #'location_dest_id': picking.location_dest_id.id,

                'location_id': picking.location_id.id if picking.location_id.id else picking.picking_type_id.default_location_src_id.id, 
                'location_dest_id': picking.location_dest_id.id if picking.location_dest_id.id else picking.picking_type_id.default_location_dest_id.id, 
                #*****modifed by xie xiaopeng 2015.04.10 for when picking not have move items***/
                'qty_done': 1,
                'product_qty': 1,
                }

            for key in domain:
                var_name, dummy, value = key
                uom_id = False
                if var_name == 'product_id':
                    uom_id = self.pool.get('product.product').browse(cr, uid, value, context=context).uom_id.id
                update_dict = {var_name: value}
                if uom_id:
                    update_dict['product_uom_id'] = uom_id
                values.update(update_dict)
            
            operation_id = self.create(cr, uid, values, context=context)

            if lot_id > 0:#when scan lot no
                self.update_origin_operation_qty(cr, uid, picking_id,product_id,increment,context=context)
        return operation_id

    def write(self, cr, uid, ids, vals, context=None):
        '''when a route is deactivated, deactivate also its pull and push rules'''
        if isinstance(ids, (int, long)):
            ids = [ids]
        
        if 'qty_done' in vals:
            op_obj = self.browse(cr, uid, ids, context=context)
            qty_done = vals.get('qty_done',0)

            increment = None
            if context:
               increment = context.get('increment',None)
            if increment == None:
                #不允许从扫描界面直接修改数量
                return

            self.update_origin_operation_qty(cr, uid, op_obj.picking_id.id,op_obj.product_id.id,increment,context=context)

        res = super(stock_pack_operation, self).write(cr, uid, ids, vals, context=context)

        return res

    def unlink(self, cr, uid, ids, context=None):
        #after unlink operation,unlink stock_move_operation_link recorde
        #***add by xie xiaopeng 20150415***#

        super(stock_pack_operation, self).unlink(cr, uid, ids, context=context)

        move_operation_link_obj = self.pool.get('stock.move.operation.link')
        move_operation_link_ids = move_operation_link_obj.search(cr, uid, [('operation_id', 'in', ids)], context=context)
        if move_operation_link_ids:
            move_operation_link_obj.unlink(cr, uid, move_operation_link_ids, context=context)

    def update_operation_product_qty_by_move(self, cr, uid, move_ids, context=None):
        #update operation prucuct_qty
        vals = {}
        if move_ids:
            for move in self.pool.get('stock.move').browse(cr, uid, move_ids,context):
                all_opteration_ids = self.pool.get('stock.move.operation.link').search_read(cr, uid, [('move_id', '=', move.id)], ['operation_id'])
                all_opteration_ids = all_opteration_ids and all_opteration_ids[0]['operation_id'][0] or False
                if all_opteration_ids:
                    all_opteration_ids = self.search(cr, uid,[('id', 'in', [all_opteration_ids]),('lot_id', '=', False)], context=context)
                    if all_opteration_ids:
                        processed_ids = [all_opteration_ids[0]]#
                        vals.update({'product_id':move.product_id.id,'product_qty':move.product_uom_qty,'product_uom_id':move.product_uom.id,'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
                        super(stock_pack_operation, self).write(cr, uid, processed_ids, vals, context=context)

class stock_picking_type(osv.osv):
    _inherit = 'stock.picking.type'

    _columns = {
        'scan_operation_type': fields.selection([
            ('1','不用扫描'),
            ('2','扫描时自动拆分产品'),
            ('3','不需要在单据创建产品，扫描时自动新增'),
            ('4','扫描时核对产品序列号')],
            string='Type of Scan Operation'),
        'auto_create_lot': fields.boolean('Auto Create Lot No'),
        'partial_delivey': fields.boolean(u'可部分扫描',help=u'发货明细表的发货字段打勾时, 才能出现在扫描页面.'),
    }

class product_template(osv.osv):
    _inherit = 'product.template'

    _columns = {
        'default_code': fields.related('product_variant_ids', 'default_code', type='char', string=u'产品定义码',required=True),
        'uom_description':fields.char(u"单位",size=16),
        'uom_type':fields.selection([('one','个'), ('multi','批')],string=u'单位类型'),
        'supply_method':fields.selection([('manufacture','u生产'),('purchase',u'购买')],string=u'供应方法'),
        'type_specification':fields.char(u"型号规格",size=100),
        'figure_number':fields.char(u"图号",size=100),
        'remark':fields.char(u"备注",size=100),
        'product_description':fields.char(u"产品说明",size=200),
        'project_code':fields.char(u"项目代号",size=100),
        'quality_grade':fields.char(u"质量等级",size=100),
        'standard_number':fields.char(u"标准号",size=100),
    }

class mrp_bom(osv.osv):
    _inherit = 'mrp.bom'

    _columns = {
        'bom_line2_ids': fields.one2many('mrp.bom.line2', 'bom_id', 'BoM Lines', copy=True),
    }
    
class mrp_bom_line2(osv.osv):
    _name = 'mrp.bom.line2'
    _order = "sequence"
    _rec_name = "product_id"

    def _get_child_bom_lines(self, cr, uid, ids, field_name, arg, context=None):
        """If the BOM line refers to a BOM, return the ids of the child BOM lines"""
        bom_obj = self.pool['mrp.bom']
        res = {}
        for bom_line in self.browse(cr, uid, ids, context=context):
            bom_id = bom_obj._bom_find(cr, uid,
                product_tmpl_id=bom_line.product_id.product_tmpl_id.id,
                product_id=bom_line.product_id.id, context=context)
            if bom_id:
                child_bom = bom_obj.browse(cr, uid, bom_id, context=context)
                res[bom_line.id] = [x.id for x in child_bom.bom_line_ids]
            else:
                res[bom_line.id] = False
        return res

    _columns = {
        'type': fields.selection([('normal', 'Normal'), ('phantom', 'Phantom')], 'BoM Line Type', required=True,
                help="Phantom: this product line will not appear in the raw materials of manufacturing orders,"
                     "it will be directly replaced by the raw materials of its own BoM, without triggering"
                     "an extra manufacturing order."),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'product_uos_qty': fields.float('Product UOS Qty'),
        'product_uos': fields.many2one('product.uom', 'Product UOS', help="Product UOS (Unit of Sale) is the unit of measurement for the invoicing and promotion of stock."),
        'product_qty': fields.float('Product Quantity', required=True, digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True,
            help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control"),
        
        'date_start': fields.date('Valid From', help="Validity of component. Keep empty if it's always valid."),
        'date_stop': fields.date('Valid Until', help="Validity of component. Keep empty if it's always valid."),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying."),
        'routing_id': fields.many2one('mrp.routing', 'Routing', help="The list of operations (list of work centers) to produce the finished product. The routing is mainly used to compute work center costs during operations and to plan future loads on work centers based on production planning."),
        'product_rounding': fields.float('Product Rounding', help="Rounding applied on the product quantity."),
        'product_efficiency': fields.float('Manufacturing Efficiency', required=True, help="A factor of 0.9 means a loss of 10% within the production process."),
        'property_ids': fields.many2many('mrp.property', string='Properties'), #Not used

        'bom_id': fields.many2one('mrp.bom', 'Parent BoM', ondelete='cascade', select=True, required=True),
        'attribute_value_ids': fields.many2many('product.attribute.value', string='Variants', help="BOM Product Variants needed form apply this line."),
        'child_line_ids': fields.function(_get_child_bom_lines, relation="mrp.bom.line", string="BOM lines of the referred bom", type="one2many")
    }

    def _get_uom_id(self, cr, uid, *args):
        return self.pool["product.uom"].search(cr, uid, [], limit=1, order='id')[0]
    _defaults = {
        'product_qty': lambda *a: 1.0,
        'product_efficiency': lambda *a: 1.0,
        'product_rounding': lambda *a: 0.0,
        'type': lambda *a: 'normal',
        'product_uom': _get_uom_id,
    }
    _sql_constraints = [
        ('bom_qty_zero', 'CHECK (product_qty>0)', 'All product quantities must be greater than 0.\n' \
            'You should install the mrp_byproduct module if you want to manage extra products on BoMs !'),
    ]

    def onchange_uom(self, cr, uid, ids, product_id, product_uom, context=None):
        res = {'value': {}}
        if not product_uom or not product_id:
            return res
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        uom = self.pool.get('product.uom').browse(cr, uid, product_uom, context=context)
        if uom.category_id.id != product.uom_id.category_id.id:
            res['warning'] = {'title': _('Warning'), 'message': _('The Product Unit of Measure you chose has a different category than in the product form.')}
            res['value'].update({'product_uom': product.uom_id.id})
        return res

    def onchange_product_id(self, cr, uid, ids, product_id, product_qty=0, context=None):
        """ Changes UoM if product_id changes.
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        res = {}
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            res['value'] = {
                'product_uom': prod.uom_id.id,
                'product_uos_qty': 0,
                'product_uos': False
            }
            if prod.uos_id.id:
                res['value']['product_uos_qty'] = product_qty * prod.uos_coeff
                res['value']['product_uos'] = prod.uos_id.id
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: