# -*- coding: utf-8 -*-
# © 2016 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from  openerp.osv import osv, fields

_logger = logging.getLogger(__name__)


class print_product_barcode(osv.osv_memory):
    '''
    print product bar code class
    '''
    _name = 'print.product.barcode'
    _descript = 'print product bar code'

    _columns = {
        'product_id': fields.many2one(
            'product.product',
            u'选择产品',
            required=True
        ),
        'number': fields.integer(
            u'产品条码数量',
            required=True,
            help=u"产品会产生多个打印批次号.",
            default=1
        ),
        'print_num': fields.integer(
            u'每个条码打印的数量',
            required=True,
            help=u"填入打印该产品每个批次号所需要打印的数量.",
            default=1
        ),
        'supplier_seiral_no': fields.char(
            string=u'厂商序列号',
            size=100
        ),
    }

    def button_print_product_barcode(self, cr, uid, ids, context=None):
        '''
            get the product ,then print it .
        '''
        if context is None:
            context = {}

        contents = self.browse(cr, uid, ids, context=context)
        if contents.number <= 0 or contents.print_num <= 0:
            return
        else:
            vals = []
            i = 0
            while i < contents.number:
                record_pool = self.pool.get('stock.production.lot')
                var = {
                    'product_id': contents.product_id.id,
                    'supplier_seiral_no': contents.supplier_seiral_no,
                }
                product_lot_id = record_pool.create(cr, uid, var)
                val = {
                    'print_times': contents.print_num,
                    'product_id': contents.product_id.id,
                    'product_barcode': product_lot_id,
                    'supplier_seiral_no': contents.supplier_seiral_no,
                }
                vals.append(val)
                i += 1

            record_pool = self.pool.get('print.product.barcode.model')
            record_list = []
            for val in vals:
                record_ids = record_pool.create(cr, uid, val)
                record_list.append(record_ids)

        view = self.pool.get('ir.model.data').get_object_reference(
            cr, uid, 'stock_extend',
            'action_print_product_barcode_tree')
        name = 'action_select_product_to_print_review'

        return {
            'domain': "[('id','in',%s)]" % record_list,
            'name': 'product print barcode',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'print.product.barcode.model',
            'type': 'ir.actions.act_window'
        }


class print_product_barcode_model(osv.osv):
    '''
    Build model for product barcode. 
    '''

    _name = 'print.product.barcode.model'
    _descript = 'print product barcode model'
    _columns = {
        'product_id': fields.many2one(
            'product.product',
            'Chose product',
            required=True
        ),
        'product_barcode': fields.many2one(
            'stock.production.lot',
            u'产品序列号',
            required=True
        ),
        'print_times': fields.integer(
            u'条码打印的数量',
            required=True,
            help=u"该产品每个批次号所需要打印的数量.",
            default=1
        ),
        'supplier_seiral_no': fields.char(
            string=u'厂商序列号',
            size=100
        ),
    }
    _order = "product_barcode desc"
    _rec_name = 'product_barcode'
