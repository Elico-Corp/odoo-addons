# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import fields, orm
from openerp.addons.base_intercompany.backend import icops
from openerp.addons.base_intercompany.unit.export_synchronizer import (
    ICOPSExporter)
from openerp.addons.base_intercompany.unit.mapper import ICOPSExportMapper
from openerp.addons.connector.unit.mapper import mapping
from openerp.addons.base_intercompany.unit.backend_adapter import (
    ICOPSAdapter)
from openerp.addons.connector.exception import MappingError


class purchase_order(orm.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'icops.model']

    _columns = {
        'openerp_id': fields.many2one('purchase.order',
                                      string='Sale Order',
                                      required=True,
                                      ondelete='cascade'),
        'icops_bind_ids': fields.one2many(
            'icops.purchase.order', 'openerp_id',
            string="ICOPS Bindings"),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['icops_bind_ids'] = False
        return super(purchase_order, self).copy_data(cr, uid, id,
                                                     default=default,
                                                     context=context)

    def create(self, cr, uid, data, context=None):
        data['icops_bind_ids'] = self.pool.get(
            'icops.backend').prepare_binding(cr, uid, data, context)
        return super(purchase_order, self).create(cr, uid, data, context)

    def write(self, cr, uid, ids, data, context=None):
        self._check_icops(cr, uid, ids, context=context)
        return super(purchase_order, self).write(cr, uid, ids, data, context)

    def unlink(self, cr, uid, ids, context=None):
        self._check_icops(cr, uid, ids, context=context)
        return super(purchase_order, self).unlink(cr, uid, ids, context)


class icops_purchase_order(orm.Model):
    _name = 'icops.purchase.order'
    _inherit = 'icops.binding'
    _inherits = {'purchase.order': 'openerp_id'}
    _description = 'ICOPS Purchase Order'

    _columns = {
        'openerp_id': fields.many2one('purchase.order',
                                      string='Product',
                                      required=True,
                                      ondelete='cascade'),
        'backend_id': fields.many2one('icops.backend',
                                      string='ICOPS Backend'),
        'icops_order_line_ids': fields.one2many('icops.purchase.order.line',
                                                'icops_order_id',
                                                'ICOPS Order Lines'),
    }


class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'
    _columns = {
        'icops_bind_ids': fields.one2many(
            'icops.purchase.order.line', 'openerp_id',
            string="ICOPS Bindings"),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['icops_bind_ids'] = False
        return super(purchase_order_line, self).copy_data(cr, uid, id,
                                                          default=default,
                                                          context=context)


class icops_purchase_order_line(orm.Model):
    _name = 'icops.purchase.order.line'
    _inherit = 'icops.binding'
    _description = 'ICOPS Sale Order Line'
    _inherits = {'purchase.order.line': 'openerp_id'}

    def _get_lines_from_order(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('icops.purchase.order.line')
        return line_obj.search(cr, uid,
                               [('icops_order_id', 'in', ids)],
                               context=context)
    _columns = {
        'icops_order_id': fields.many2one('icops.purchase.order',
                                          'ICOPS Sale Order',
                                          required=True,
                                          ondelete='cascade',
                                          select=True),
        'openerp_id': fields.many2one('purchase.order.line',
                                      string='Sale Order Line',
                                      required=True,
                                      ondelete='cascade'),
        'backend_id': fields.related(
            'icops_order_id', 'backend_id',
            type='many2one',
            relation='icops.backend',
            string='ICOPS Backend',
            store={'icops.purchase.order.line':
                   (lambda self, cr, uid, ids, c=None: ids,
                    ['icops_order_id'],
                    10),
                 'icops.purchase.order':
                   (_get_lines_from_order, ['backend_id'], 20),
                   },
            readonly=True)
    }

    def create(self, cr, uid, vals, context=None):
        icops_order_id = vals['icops_order_id']
        info = self.pool['icops.purchase.order'].read(cr, uid,
                        [icops_order_id],
            ['openerp_id'],
            context=context)
        order_id = info[0]['openerp_id']
        vals['order_id'] = order_id[0]
        return super(icops_purchase_order_line, self).create(cr, uid, vals,
                                                             context=context)


@icops
class PurchaseOrderAdapter(ICOPSAdapter):
    _model_name = 'icops.purchase.order'

    def _get_pool(self):
        sess = self.session
        return sess.pool.get('sale.order')

    def confirm(self, id):
        sess = self.session
        pool = self._get_pool()
        context = {'icops': True}
        pool.write(
            sess.cr, self._backend_to.icops_uid.id, [id],
            {'temp_unlock': True}, context=context)
        pool.action_wait(
            sess.cr, self._backend_to.icops_uid.id, [id])
        pool.write(
            sess.cr, self._backend_to.icops_uid.id, [id],
            {'temp_unlock': False}, context=context)

    def cancel(self, id):
        sess = self.session
        pool = self._get_pool()
        context = {'icops': True}
        pool.write(
            sess.cr, self._backend_to.icops_uid.id, [id],
            {'temp_unlock': True}, context=context)
        pool.action_cancel(sess.cr, self._backend_to.icops_uid.id, [id])
        pool.write(
            sess.cr, self._backend_to.icops_uid.id, [id],
            {'temp_unlock': False}, context=context)


@icops
class PurchaseOrderExport(ICOPSExporter):
    _model_name = ['icops.purchase.order']
    _concepts = ['po2so']

    def _custom_routing(self, id, record, fields=None):
        if 'state' in fields:
            state = record.pop('state')
            if state == 'cancel':
                self._cancel(id)
            elif state == 'progress':
                self._confirm(id)
        elif fields:
            self._write(id, record)


@icops
class PurchaseOrderExportMapper(ICOPSExportMapper):
    _model_name = 'icops.purchase.order'

    children = [
        ('order_line', 'order_line', 'icops.purchase.order.line')
    ]

    @mapping
    def origin(self, record):
        return {'origin': 'ICOPS: %s' % record.name}

    @mapping
    def state(self, record):
        state = record.state
        if record.state == 'approved':
            state = 'progress'
        return {'state': state}

    @mapping
    def address(self, record):
        sess = self.session
        partner = record.company_id.partner_id
        partner_pool = sess.pool.get('res.partner')
        addr = partner_pool.address_get(sess.cr, sess.uid, [partner.id],
                                        ['delivery', 'invoice', 'contact'])
        return {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery']
        }

    @mapping
    def icops(self, record):
        if not self._backend_to:
            raise MappingError("Could not find an ICOPS backend")
        sess = self.session
        backend = self._backend_to
        ic_uid = backend.icops_uid.id
        company = backend.company_id
        partner_pool = sess.pool.get('res.partner')
        partner_id = record.company_id.partner_id.id
        partner = partner_pool.browse(sess.cr, ic_uid, partner_id)
        pricelist = (partner.property_product_pricelist.id
                     if partner.property_product_pricelist
                     else False)
        fiscal_position = partner.property_account_position
        payment_term = partner.property_payment_term
        shop = self._backend_to.icops_shop_id
        if company.partner_id.id != record.partner_id.id:
            raise MappingError("Wrong partner")
        return {
            'company_id': company.id,
            'partner_id': partner.id,
            'pricelist_id': pricelist,
            'fiscal_position': fiscal_position.id,
            'payment_term': payment_term.id,
            'user_id': ic_uid,
            'shop_id': shop.id
        }


@icops
class PurchaseOrderLineExportMapper(ICOPSExportMapper):
    _model_name = 'icops.purchase.order.line'

    @mapping
    def product(self, record):
        return {
            'name': record.name,
            'product_id': record.product_id.id,
            'product_uom': record.product_uom.id,
            'product_uom_qty': record.product_qty
        }

    @mapping
    def price(self, record):
        if not record.product_id:
            return {'price_unit': 0}
        sess = self.session
        backend = self._backend_to
        ic_uid = backend.icops_uid.id
        partner_pool = sess.pool.get('res.partner')
        partner_id = record.order_id.company_id.partner_id.id
        partner = partner_pool.browse(sess.cr, ic_uid, partner_id)
        pricelist_id = (partner.property_product_pricelist.id
                        if partner.property_product_pricelist
                        else False)
        pricelist_pool = sess.pool.get('product.pricelist')
        price_unit = pricelist_pool.price_get(
            sess.cr, ic_uid, [pricelist_id],
            record.product_id.id, record.product_qty)
        price = price_unit[int(pricelist_id)]
        return {'price_unit': price}
