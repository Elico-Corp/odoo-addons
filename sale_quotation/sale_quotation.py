# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from osv import fields, orm, osv
from tools.translate import _
import netsvc
logger = netsvc.Logger()


class quotation_reason(orm.Model):

    """ the reason of quotation """
    _name = "sale.quotation.reason"
    _description = "Make Quotation Reason"

    _columns = {
        'name': fields.char('Name', size=128, required=True, translate=True),
    }


class sale_order(orm.Model):
    _inherit = 'sale.order'

    _columns = {
        'originated_from': fields.many2one(
            'sale.order', 'Originated From', readonly=True),
        'file_number': fields.many2one(
            'crm.lead', 'File Number', readonly=True),
        'quotation_version': fields.integer(
            string='Quotation Version', readonly=True),
        'state': fields.selection([
            ('draft', 'Quotation'),
            ('sent', 'Quotation Sent'),
            ('q_lost', 'Quote Lost'),
            ('q_converted', 'Quote Converted'),
            ('waiting_date', 'Waiting Schedule'),
            ('manual', 'Sale to Invoice'),
            ('progress', 'In Progress'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
        ], 'Order State',
            help="Gives the state of the quotation or sales order. \n\
              The exception state is automatically set when a cancel operation\
              occurs in the invoice validation (Invoice Exception) or in the\
              picking list process (Shipping Exception). \n\
              The 'Waiting Schedule' state is set when the invoice is\
              confirmed but waiting for the scheduler to run on the\
              date 'Ordered Date'.", select=True),
        'reason_code': fields.many2one('sale.quotation.reason',
                                       string='Reason', readonly=True),
        'notes': fields.char(string='Note', size=256, readonly=True),
        'thread': fields.char(string='Thread', size=128, readonly=True),
        'reset': fields.boolean('Reseted', readonly=True),
        'sale_project_id': fields.many2one(
            'sale.project', string='Sales Project', readonly=False),
    }

    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(
            cr, uid, 'sale.quotation'),
        'invoiced': False,
        'reset': False,
        'quotation_version': lambda *args: 1,
    }

    def create(self, cr, uid, vals, context=None):
        """
        if no thread value provide in context, this order will be a new thread,
        with its' name as the thread name
        """
        if not vals.get('file_number', False):
            raise osv.except_osv(_('Warning'), _(
                'You cannot create sale order directly,\
                 please create order from opportunity!'))

        if not vals.get('name', False):
            quotation_name = self.pool.get('ir.sequence').get(cr, uid, 'sale.quotation')
            vals.update({'name': quotation_name})
        new_id = super(sale_order, self).create(cr, uid, vals, context=context)
        if not vals.get('thread', False):
            new_o = self.read(cr, uid, new_id, ['name'], context=context)
            self.write(cr, uid, new_id, {'thread': new_o['name']},
                       context=context)
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        if not isinstance(ids, list):
            ids = [ids]
        if 'state' in vals and vals['state'] == 'progress':
            so = self.browse(cr, uid, ids, context=context)[0]
            vals['name'] = so.name.replace('Q', 'O')
        return super(sale_order, self).write(
            cr, uid, ids, vals, context=context)

    def make_new_quotation(self, cr, uid, ids, context=None):
        new_ids = []
        sequence_pool = self.pool.get('ir.sequence')
        view_pool = self.pool.get('ir.ui.view')
        crm_pool = self.pool.get('crm.lead')
        for o in self.browse(cr, uid, ids):
            to_write = {}
            if o.file_number:
                num = self.search(
                    cr, uid, args=[('file_number.id', '=', o.file_number.id),
                                   ('thread', '=', o.thread)], context=context,
                    count=True) + 1
                to_write.update(
                    {'file_number': o.file_number.id, 'quotation_version': num}
                )
            else:
                to_write.update({'file_number': []})
            data = self.copy_data(cr, uid, o.id, to_write, context)
            data.update({
                'name': sequence_pool.get(
                    cr, uid, 'sale.quotation'),
                'originated_from': o.id,
            })
            new_id = self.create(cr, uid, data, context)
            self.copy_translations(cr, uid, o.id, new_id, context=context)
            new_ids.append(new_id)
            new_o = self.browse(cr, uid, new_id, context=context)
            if o.file_number:
                msg = "Converted to Sales Quotation(name: %s).Version:%d,\
                       Reason:%s,note:%s" % (
                    new_o.name, new_o.quotation_version,
                    context.get('quotation_reason', ''),
                    context.get('quotation_notes', ''))

                crm_pool.message_post(
                    cr, uid, ids,
                    body=_(msg),
                    subtype="crm.mt_lead_convert_to_opportunity",
                    context=context)

        self.write(cr, uid, ids, {'state': 'q_converted'}, context=context)
        self.write(cr, uid, new_ids, {
            'reason_code': context.get('reason_code', False),
            'notes': context.get('quotation_notes', ''),
        }, context=context)
        if not new_ids:
            return {'type': 'ir.actions.act_window_close'}
        view_id = view_pool.search(
            cr, uid, [('name', '=', 'sale_quotation.sale.order.form')],
            context=context)

        value = {
            'domain': str([('id', 'in', new_ids)]),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'sale.order',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'name': _('Sales Quotations'),
            'res_id': new_ids[0]
        }
        return value

    def action_button_confirm(self, cr, uid, ids, context=None):
        '''here we rewrite this function to create an extra quotation
        in state:q_converted to for logging purpose'''
        sequence_pool = self.pool.get('ir.sequence')
        to_write = {}
        new_id = False
        for sale in self.browse(cr, uid, ids):
            if "SO" not in sale.name:
                data = self.copy_data(cr, uid, sale.id, to_write, context)
                data.update({
                    'name': sequence_pool.get(
                        cr, uid, 'sale.order'),
                    'state': 'draft',
                })
                #create the new order.
                new_id = self.create(cr, uid, data, context)
                sale.write({'state': 'q_converted'}, context=context)
        return super(sale_order, self).action_button_confirm(
            cr, 20, new_id and [new_id] or ids, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
            'state': 'draft',
            'date_confirm': False,
            'shipped': False,
            'invoice_ids': [],
            'picking_ids': [],
            'originated_from': id,
            'thread': None,
            'quotation_version': 0,
            'name': self.pool.get('ir.sequence').get(cr, uid, 'sale.quotation')
        })

        return osv.osv.copy(self, cr, uid, id, default, context=context)

    def action_cancel(self, cr, uid, ids, context=None):
        super(sale_order, self).action_cancel(cr, uid, ids, context=context)
        context = context or {}
        for o in self.browse(cr, uid, ids, context=context):
            if o.file_number:
                msg = _(
                    "Sales Order Cancelled(name: %s).Reason:%s,note:%s") % (
                    o.name, context.get('quotation_reason', ''),
                    context.get('quotation_notes', ''))
                self.pool.get('crm.lead').message_post(
                    cr, uid, [o.file_number],
                    body=_(msg), context=context)
        self.write(
            cr, uid, ids, {'reason_code': context.get('reason_code', False),
                           'notes': context.get('quotation_notes', ''),
                           'reset': True,
                           }, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def reset_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def set_to_lost(self, cr, uid, ids, context=None):
        for o in self.browse(cr, uid, ids):
            if o.file_number:
                logger.notifyChannel(
                    'sale_quotation', netsvc.LOG_INFO, 'context= %s' % (
                        context)
                )
                logger.notifyChannel(
                    'sale_quotation', netsvc.LOG_INFO, 'name= %s' % (o.name))
                msg = _("Sales Quotation Lost(name: %s).Reason:%s,note:%s") % (
                    o.name, context.get('quotation_reason', ''),
                    context.get('quotation_notes', ''))
                self.pool.get('crm.lead').message_post(
                    cr, uid, [o.file_number],
                    body=_(msg), context=context)
        self.write(
            cr, uid, ids, {'reason_code': context.get('reason_code', False),
                           'notes': context.get('quotation_notes', ''),
                           'state': 'q_lost'
                           }, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        val = super(sale_order, self).onchange_partner_id(
            cr, uid, ids, part, context=context)['value']
        if 'pricelist_id' in val:
            del val['pricelist_id']
        return {'value': val}

    def onchange_project_id(self, cr, uid, ids, project_id):
        """when user change the sales project
        """
        if not project_id:
            return {'value': {'pricelist_id': False}}
        sale_project = self.pool.get(
            'sale.project').browse(cr, uid, project_id)
        pricelist = sale_project.property_product_pricelist.id\
            if sale_project.property_product_pricelist.id\
            else None
        return {'value': {'pricelist_id': pricelist}}

    def reactive_sale_order(self, cr, uid, ids, context=None):
        '''reactive cancelled orders
            1- if this order already has cancelled DO, we keep them'''
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        wf_service = netsvc.LocalService("workflow")
        for order in self.browse(cr, uid, ids, context=context):
            wf_service.trg_delete(uid, 'sale.order', order.id, cr)
            wf_service.trg_create(uid, 'sale.order', order.id, cr)
            order.write(
                {'state': 'draft',
                 'order_line': [(1, line.id, {'state': 'draft'}) for line in order.order_line]})


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    _columns = {
        'sale_project_id': fields.related(
            'order_id', 'sale_project_id', type='many2one',
            relation='sale.project', string='Sale Project'),
        'project_name': fields.related(
            'sale_project_id', 'project_name', type='char',
            string='Project Name'),
    }
