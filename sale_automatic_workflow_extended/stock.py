# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)
from openerp.osv import orm, fields
from openerp import netsvc
import logging

from openerp.addons.sale_automatic_workflow.automatic_workflow_job import commit

_logger = logging.getLogger(__name__)


class sale_workflow_process(orm.Model):
    _inherit = "sale.workflow.process"

    def _get_journal_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        journal_obj = self.pool.get('account.journal')
        user_obj = self.pool.get('res.users')
        company_id = user_obj.browse(cr, uid, uid, context=context).company_id
        journal_type = 'sale'
        journal_ids = journal_obj.search(
            cr, uid, [('type', '=', journal_type), ('company_id', '=', company_id.id)])
        return journal_ids and journal_ids[0] or False

    def onchange_order_policy(self, cr, uid, ids, order_policy, context=None):
        val = {}
        if order_policy:
            if order_policy == 'picking':
                val['create_invoice_on'] = 'on_picking_done'
        return {'value': val}

    _columns = {
        'journal_id': fields.many2one(
            'account.journal', 'Destination Journal', required=True),
    }
    _defaults = {
        'journal_id': _get_journal_id
    }


class automatic_workflow_job(orm.Model):
    """ Scheduler that will play automatically the validation of
    invoices, pickings...  """
    _inherit = 'automatic.workflow.job'

    def _validate_sale_orders(self, cr, uid, context=None):
        ''' inherit this method to include the sent quotation'''
        wf_service = netsvc.LocalService("workflow")
        sale_obj = self.pool.get('sale.order')
        sale_ids = sale_obj.search(
            cr, uid,
            [('state', 'in', ('draft', 'sent')),
             ('workflow_process_id.validate_order', '=', True)],
            context=context)
        _logger.debug('Sale Orders to validate: %s', sale_ids)
        for sale_id in sale_ids:
            with commit(cr):
                wf_service.trg_validate(uid, 'sale.order',
                                        sale_id, 'order_confirm', cr)

    def _create_invoice_on_shipping(self, cr, uid, context=None):
        context = context or {}
        picking_obj = self.pool.get('stock.picking.out')
        inv_obj = self.pool.get('account.invoice')
        wf_service = netsvc.LocalService('workflow')
        todo = {}
        res = []
        picking_ids = picking_obj.search(
            cr, uid,
            [('invoice_state', '=', '2binvoiced'), ('state', '=', 'done'), ('sale_id.partner_id.active', '=', True)],
            context=context)
        if picking_ids:
            for pick in picking_obj.browse(
                    cr, uid, picking_ids, context=context):
                workflow_process = pick.sale_id and pick.sale_id.workflow_process_id
                if workflow_process and \
                        workflow_process.create_invoice_on == 'on_picking_done':
                    todo[pick.id] = (workflow_process.journal_id.id, workflow_process.id)
        todo_ids = todo.keys()
        active_pickings = picking_obj.browse(
            cr, uid, todo_ids, context=context)
        for active_picking in active_pickings:
            inv_type = picking_obj._get_invoice_type(active_picking)
            context['inv_type'] = inv_type
            res = active_picking.action_invoice_create(
                journal_id=todo[active_picking.id][0],
                type=inv_type,
                context=context)
            # hook, write back the invoice: workflow_process_id
            if res:
                invoice_ids = res.values()
                inv_obj.write(
                    cr, uid,
                    invoice_ids,
                    {'workflow_process_id': todo[active_picking.id][1]},
                    context=context)
            # trigger the workflow of sale order from to_invoice to invoiced.
            wf_service.trg_write(uid, 'sale.order', active_picking.sale_id.id, cr)
        return res

    def run(self, cr, uid, ids=None, context=None):
        """ Must be called from ir.cron
            overwrite this function from module: sale_automatic_workflow
        """
        self._validate_sale_orders(cr, uid, context=context)
        self._create_invoice_on_shipping(cr, uid, context=context)
        self._validate_invoices(cr, uid, context=context)
        self._validate_pickings(cr, uid, context=context)
        return True


class stock_move(orm.Model):
    _inherit = 'stock.move'

    def _prepare_chained_picking(self, cr, uid, picking_name, picking, picking_type, moves_todo, context=None):
        """Prepare the definition (values) to create a new chained picking.

           :param str picking_name: desired new picking name
           :param browse_record picking: source picking (being chained to)
           :param str picking_type: desired new picking type
           :param list moves_todo: specification of the stock moves to be later included in this
               picking, in the form::

                   [[move, (dest_location, auto_packing, chained_delay, chained_journal,
                                  chained_company_id, chained_picking_type)],
                    ...
                   ]

               See also :meth:`stock_location.chained_location_get`.

            Rewrite to add workflow process
        """
        res = super(stock_move, self)._prepare_chained_picking(
            cr, uid, picking_name, picking,
            picking_type, moves_todo, context=context)
        res['workflow_process_id'] = picking.workflow_process_id and picking.workflow_process_id.id or False
        return res

class sale_order(orm.Model):
    _inherit = 'sale.order'


    def _get_default_workflow(self, cr, uid, context=None):
        '''Get the default workflow from company.
        A new field: default_workflow has been added on the company.
        for more details: check: task: 5621:automatic workflow setup'''
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        workflow = user.company_id.workflow_process_id
        return workflow and workflow.id or False
        
    _defaults = {'workflow_process_id': _get_default_workflow}

class res_company(orm.Model):
    _inherit = 'res.company'
    _columns = {'workflow_process_id': fields.many2one('sale.workflow.process',
                                                string='Default Sale Workflow Process')}
