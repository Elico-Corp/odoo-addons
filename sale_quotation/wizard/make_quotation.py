# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import fields, osv
from tools.translate import _
import time
from tools import ustr


class make_quotation(osv.osv_memory):

    """ Make sale quotation """

    _name = "sale.make.quotation"
    _description = "Make Quotation Wizard"

    def view_init(self, cr, uid, fields_list, context=None):
        return super(make_quotation, self).view_init(
            cr, uid, fields_list, context=context)

    def next_action(self, cr, uid, ids, context=None):
        sale_obj = self.pool.get('sale.order')
        return sale_obj.make_new_quotation(
            cr, uid, ids, context=context)

    def confirm(self, cr, uid, ids, context=None):
        """
        This function  create Quotation on given case.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of crm make sales' ids
        @param context: A standard dictionary for contextual values
        @return: Dictionary value of created sales order.
        """
        if context is None:
            context = {}

        data = context and context.get('active_ids', []) or []

        for make in self.browse(cr, uid, ids, context=context):
            context.update({'quotation_reason': make.reason_code.name,
                            'reason_code': make.reason_code.id,
                            'quotation_notes': ustr(make.notes) or ''})
                #'quotation_notes':make.notes or ''})
            value = self.next_action(cr, uid, data, context=context)
            return value

    _columns = {
        'reason_code': fields.many2one(
            'sale.quotation.reason', 'Reason', required=True),
        'notes': fields.char('Note', size=256, required=False),
    }


class cancel_order(osv.osv_memory):

    """ cancel an order"""

    _name = "sale.cancel.order"
    _inherit = "sale.make.quotation"
    _description = "Cancel an Order"

    def next_action(self, cr, uid, ids, context=None):
        sale_obj = self.pool.get('sale.order')
        return sale_obj.action_cancel(cr, uid, ids, context=context)


class lost_quotation(osv.osv_memory):

    """ cancel an order"""

    _name = "sale.lost.quotation"
    _inherit = "sale.make.quotation"
    _description = "Lost an Order"

    def next_action(self, cr, uid, ids, context=None):
        sale_obj = self.pool.get('sale.order')
        return sale_obj.set_to_lost(cr, uid, ids, context=context)


class crm_make_sale(osv.osv_memory):

    """ Make sale  order for crm """

    _name = "crm.make.sale"
    _description = "Make sales"
    _inherit = "crm.make.sale"

    def _selectPartner_overriding(self, cr, uid, context=None):
        """
        This function gets default value for partner_id field.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param context: A standard dictionary for contextual values
        @return: default value of partner_id field.
        """
        context = context or {}
        lead_obj = self.pool.get('crm.lead')
        active_id = context and context.get('active_id', False) or False
        if not active_id:
            return False
        lead = lead_obj.browse(cr, uid, active_id, context)
        return lead.partner_id.id

    def makeOrder(self, cr, uid, ids, context=None):
        """
        This function  create Quotation on given case.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of crm make sales' ids
        @param context: A standard dictionary for contextual values
        @return: Dictionary value of created sales order.
        """
        context = context or {}

        case_obj = self.pool.get('crm.lead')
        sale_obj = self.pool.get('sale.order')
        partner_obj = self.pool.get('res.partner')
        data = context and context.get('active_ids', []) or []

        for make in self.browse(cr, uid, ids, context=context):
            partner = make.partner_id
            partner_addr = partner_obj.address_get(
                cr, uid, [partner.id],
                ['default', 'invoice', 'delivery', 'contact'])
            pricelist = partner.property_product_pricelist.id
            fpos = partner.property_account_position\
                and partner.property_account_position.id or False
            new_ids = []
            for case in case_obj.browse(cr, uid, data, context=context):
                # if not partner and case.partner_id:
                if case.partner_id:
                    partner = case.partner_id
                    fpos = partner.property_account_position\
                        and partner.property_account_position.id or False
                    partner_addr = partner_obj.address_get(
                        cr, uid, [partner.id],
                        ['default', 'invoice', 'delivery', 'contact'])
                    # get sales team and payment term
                    section_id = partner.section_id and \
                        partner.section_id.id or False
                    payment_term = partner.property_payment_term and \
                        partner.property_payment_term.id or ''
                    #pricelist = partner.property_product_pricelist.id
                    pricelist = case.sale_project_id\
                        and case.sale_project_id.property_product_pricelist.id\
                        or partner.property_product_pricelist.id
                if False in partner_addr.values():
                    raise osv.except_osv(
                        _('Data Insufficient!'), _(
                            'Customer has no addresses defined!'))

                vals = {
                    'origin': _('Opportunity: %s') % str(case.id),
                    'section_id': (case.section_id and case.section_id.id
                                   or False),
                    'shop_id': make.shop_id.id,
                    'partner_id': partner.id,
                    'sale_project_id': case.sale_project_id and
                    case.sale_project_id.id or False,
                    'pricelist_id': pricelist,
                    'partner_invoice_id': partner_addr['invoice'],
                    'partner_order_id': partner_addr['contact'],
                    'partner_shipping_id': partner_addr['delivery'],
                    'date_order': time.strftime('%Y-%m-%d'),
                    'fiscal_position': fpos,
                    'file_number': case.id,
                    'payment_term': payment_term,
                    'section_id': section_id,
                }

                if partner.id:
                    vals['user_id'] = partner.user_id\
                        and partner.user_id.id or uid
                new_id = sale_obj.create(cr, uid, vals)
                # link sale_obj with the categ_ids on lead.
                if case.categ_ids:
                    sale_obj.write(
                        cr, uid, new_id,
                        {'categ_ids': [(
                            6, 0, [categ.id for categ in case.categ_ids])]})
                case_obj.write(cr, uid, [case.id],
                               {'ref': 'sale.order,%s' % new_id})
                new_ids.append(new_id)

            # add reason for new orders
            sale_obj.write(cr, uid, new_ids, {
                'notes': _('Create from Opportunity'),
            }, context=context)
            if make.close:
                case_obj.case_close(cr, uid, data)
            if make.stage_id:
                case_obj.write(cr, uid, [case.id],
                               {'stage_id': make.stage_id.id})
            if not new_ids:
                return {'type': 'ir.actions.act_window_close'}
            if len(new_ids) <= 1:
                value = {
                    'name': _('Sales Quotations'),
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form,tree',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'res_id': new_ids and new_ids[0]
                }
            else:
                value = {
                    'name': _('Sales Quotations'),
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form,tree',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'res_id': new_ids
                }
            return value

    _columns = {
        'stage_id': fields.many2one(
            'crm.case.stage', 'Set Stage', required=False),
    }

    _defaults = {
        'partner_id': _selectPartner_overriding,
        'close': False,
    }


class lost_opportunity(osv.osv_memory):

    """ Lost an opportunity"""

    _name = "crm.lost.opportunity"
    _inherit = "sale.make.quotation"
    _description = "Lost an opportunity"

    def next_action(self, cr, uid, ids, context=None):
        opp_obj = self.pool.get('crm.lead')
        return opp_obj.set_to_lost(cr, uid, ids, context=context)
