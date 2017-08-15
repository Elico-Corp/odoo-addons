# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 Serpent Consulting Services PVT LTD (<http://www.serpentcs.com>)
#
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
############################################################################

from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from openerp.exceptions import except_orm, Warning, RedirectWarning

class crm_lead(osv.osv):
    _inherit = "crm.lead"

    _columns = {
              'is_rent':fields.boolean('Is Rent'),
              'is_buy':fields.boolean('Is Buy'),
              'min_bedroom':fields.integer('Min. Bedroom Require'),
              'max_bedroom':fields.integer('Max Bedroom Require'),
              'min_bathroom':fields.integer('Min. Bathroom Require'),
              'max_bathroom':fields.integer('Max Bathroom Require'),
              'min_price':fields.float('Min. Price'),
              'max_price':fields.float('Max Price'),
              'facing':fields.char('Facing'),
              'furnished':fields.char('Furnishing', help='Furnishing'),
              'demand':fields.boolean('Is Demand'),
              'type_id':fields.many2one('property.type', 'Property Type',help='Property Type'),
              'email_send':fields.boolean('Email Send', help="it is checked when email is send"),
              }

    _defaults = {
               'is_rent': False,
               'is_buy':False,
               }

    def cron_property_demand(self, cr, uid, context=None):
        """
        This is schedular function which send mails to customers who are demanded properties.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param context: A standard dictionary for contextual values
        """
        lead_ids = self.search(cr, uid, [('demand','=',True)], context=context)
        property_obj = self.pool.get('account.asset.asset')
        ir_model_data = self.pool.get('ir.model.data')
        email_objc = self.pool.get('email.template')
        template_id = ir_model_data.get_object_reference(cr, uid, 'property_management','email_template_demand_property')[1]
        if lead_ids:
            for lead_rec in self.browse(cr,uid,lead_ids,context=context):
                req_args = [('bedroom','<=',lead_rec.max_bedroom),
                            ('bedroom','>=',lead_rec.min_bedroom),
                            ('bathroom','<=',lead_rec.max_bathroom),
                            ('bathroom','>=',lead_rec.min_bathroom),
                            ('sale_price','<=',lead_rec.max_price),
                            ('sale_price','>=',lead_rec.min_price),
                            ('type_id','=',lead_rec.type_id.id)]
                if lead_rec.furnished == "all" and lead_rec.facing == "all":
                    required_prop = property_obj.search(cr, uid, req_args, context=context)
                elif lead_rec.furnished == "all":
                    req_args += [('facing','=',lead_rec.facing)]
                    required_prop = property_obj.search(cr, uid, req_args, context=context)
                elif lead_rec.facing == "all":
                    req_args += [('furnished','=',lead_rec.furnished)]
                    required_prop = property_obj.search(cr, uid, req_args, context=context)
                else:
                    req_args += [('furnished','=',lead_rec.furnished),('facing','=',lead_rec.facing)]
                    required_prop = property_obj.search(cr, uid, req_args, context=context)
                if template_id and required_prop and lead_rec.user_id.login and lead_rec.email_send == False:
                    email_objc.send_mail(cr, uid, template_id, lead_rec.id, force_send=True, context=context)
                    self.write(cr, uid, lead_rec.id, {'email_send':True}, context=context)
        return True

    def _lead_create_contact(self, cr, uid, lead, name, is_company, parent_id=False, context=None):
        partner = self.pool.get('res.partner')
        tenant_obj = self.pool.get('tenant.partner')
        vals = {'name': name,
            'user_id': lead.user_id.id,
            'comment': lead.description,
            'section_id': lead.section_id.id or False,
            'parent_id': parent_id,
            'phone': lead.phone,
            'mobile': lead.mobile,
            'email': lead.email_from,
            'fax': lead.fax,
            'title': lead.title and lead.title.id or False,
            'function': lead.function,
            'street': lead.street,
            'street2': lead.street2,
            'zip': lead.zip,
            'city': lead.city,
            'country_id': lead.country_id and lead.country_id.id or False,
            'state_id': lead.state_id and lead.state_id.id or False,
            'is_company': is_company,
            'type': 'contact',
            'is_tenant':True,
        }
        if not lead.email_from:
            raise osv.except_osv(
                _('Warning!'),
                _(' Contact Name or Email is Missing')
            )
        if lead.is_rent:
            tenant = tenant_obj.create(cr, uid, vals, context=context)
            tenant_data = tenant_obj.browse(cr, uid, tenant, context=context).parent_id.id
            partner.write(cr, uid, tenant_data, {'is_tenant':True})
            return tenant_data
        else:
            vals2 = {'name': name,
                'user_id': lead.user_id.id,
                'comment': lead.description,
                'section_id': lead.section_id.id or False,
                'parent_id': parent_id,
                'phone': lead.phone,
                'mobile': lead.mobile,
                'email': tools.email_split(lead.email_from) and tools.email_split(lead.email_from)[0] or False,
                'fax': lead.fax,
                'title': lead.title and lead.title.id or False,
                'function': lead.function,
                'street': lead.street,
                'street2': lead.street2,
                'zip': lead.zip,
                'city': lead.city,
                'country_id': lead.country_id and lead.country_id.id or False,
                'state_id': lead.state_id and lead.state_id.id or False,
                'is_company': is_company,
                'type': 'contact'
            }
            partner = partner.create(cr, uid, vals2, context=context)
            return partner


class crm_make_sale(osv.osv_memory):
    """ Make sale  order for crm """

    _inherit = "crm.make.sale"
    
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
        # update context: if come from phonecall, default state values can make the quote crash lp:1017353
        context = dict(context or {})
        context.pop('default_state', False)        
        
        case_obj = self.pool.get('crm.lead')
        sale_obj = self.pool.get('sale.order')
        partner_obj = self.pool.get('res.partner')
        asset_obj = self.pool.get('account.asset.asset')
        data = context and context.get('active_ids', []) or []

        for make in self.browse(cr, uid, ids, context=context):
            partner = make.partner_id
            partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                    ['default', 'invoice', 'delivery', 'contact'])
            pricelist = partner.property_product_pricelist.id
            fpos = partner.property_account_position and partner.property_account_position.id or False
            payment_term = partner.property_payment_term and partner.property_payment_term.id or False
            new_ids = []
            for case in case_obj.browse(cr, uid, data, context=context):
                if not partner and case.partner_id:
                    partner = case.partner_id
                    fpos = partner.property_account_position and partner.property_account_position.id or False
                    payment_term = partner.property_payment_term and partner.property_payment_term.id or False
                    partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                            ['default', 'invoice', 'delivery', 'contact'])
                    pricelist = partner.property_product_pricelist.id
                if False in partner_addr.values():
                    raise osv.except_osv(_('Insufficient Data!'), _('No address(es) defined for this customer.'))

                vals = {
                    'origin': _('Opportunity: %s') % str(case.id),
                    'section_id': case.section_id and case.section_id.id or False,
                    'categ_ids': [(6, 0, [categ_id.id for categ_id in case.categ_ids])],
                    'partner_id': partner.id,
                    'pricelist_id': pricelist,
                    'partner_invoice_id': partner_addr['invoice'],
                    'partner_shipping_id': partner_addr['delivery'],
                    'date_order': fields.datetime.now(),
                    'fiscal_position': fpos,
                    'payment_term':payment_term,
                    'is_property':True,
                }
                if partner.id:
                    vals['user_id'] = partner.user_id and partner.user_id.id or uid
                if case.property_id:
                    pro_sale_vals = {
                        'origin': 'crm.lead',
                        'property_id' :case.property_id.id,
                        'name' : case.property_id.name or "" ,
                        'product_uom_qty' : 1,
                        'price_unit':case.property_id.sale_price or 0.0,
                        'is_property':True,
                        }
                    vals.update({'order_line': [(0, 0, pro_sale_vals)]})
                    asset_obj.write(cr, uid, [case.property_id.id], {'state':'sold'}, context=context)
                new_id = sale_obj.create(cr, uid, vals, context=context)
                sale_order = sale_obj.browse(cr, uid, new_id, context=context)
                case_obj.write(cr, uid, [case.id], {'ref': 'sale.order,%s' % new_id})
                new_ids.append(new_id)
                message = _("Opportunity has been <b>converted</b> to the quotation <em>%s</em>.") % (sale_order.name)
                case.message_post(body=message)
            if make.close:
                case_obj.case_mark_won(cr, uid, data, context=context)
            if not new_ids:
                return {'type': 'ir.actions.act_window_close'}
            if len(new_ids)<=1:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids and new_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids
                }
            return value


class crm_make_contract(osv.osv_memory):
    """ Make contract  order for crm """

    _name = "crm.make.contract"
    _description = "Make sales"

    def _selectPartner(self, cr, uid, context=None):
        """
        This function gets default value for partner_id field.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param context: A standard dictionary for contextual values
        @return: default value of partner_id field.
        """
        if context is None:
            context = {}

        lead_obj = self.pool.get('crm.lead')
        active_id = context and context.get('active_id', False) or False
        if not active_id:
            return False

        lead = lead_obj.read(cr, uid, [active_id], ['partner_id'], context=context)[0]
        return lead['partner_id'][0] if lead['partner_id'] else False


    def makecontract(self, cr, uid, ids, context=None):
        """
        This function  create Quotation on given case.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of crm make sales' ids
        @param context: A standard dictionary for contextual values
        @return: Dictionary value of created sales order.
        """
        # update context: if come from phonecall, default state values can make the quote crash lp:1017353
        context = dict(context or {})
        context.pop('default_state', False)        
        
        case_obj = self.pool.get('crm.lead')
        analytic_obj = self.pool.get('account.analytic.account')
        partner_obj = self.pool.get('res.partner')
        data = context and context.get('active_ids', []) or []
#        date_start = 
        for make in self.browse(cr, uid, ids, context=context):
            partner = make.partner_id
            pricelist = partner.property_product_pricelist.id
            fpos = partner.property_account_position and partner.property_account_position.id or False
            payment_term = partner.property_payment_term and partner.property_payment_term.id or False
            new_ids = []
            for case in case_obj.browse(cr, uid, data, context=context):
                if not partner and case.partner_id:
                    partner = case.partner_id

                vals = {
                    'name':case.name,
                    'partner_id': partner.id,
                    'company_id':partner.company_id.id,
                    'date_start':make.date_start or False,
                    'date':make.date or False,
                    'type':'contract',
                }
                new_id = analytic_obj.create(cr, uid, vals, context=context)
                analyitic_acc = analytic_obj.browse(cr, uid, new_id, context=context)
                case_obj.write(cr, uid, [case.id], {'ref': 'account.analytic.account,%s' % new_id})
                new_ids.append(new_id)
                message = _("Opportunity has been <b>converted</b> to the Contract <em>%s</em>.") % (analyitic_acc.name)
                case.message_post(body=message)
            if make.close:
                case_obj.case_mark_won(cr, uid, data, context=context)
            if not new_ids:
                return {'type': 'ir.actions.act_window_close'}
            if len(new_ids)<=1:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.analytic.account',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Contract'),
                    'res_id': new_ids and new_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.analytic.account',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Contract'),
                    'res_id': new_ids
                }
            return value


    _columns = {
        'partner_id': fields.many2one('res.partner', 'Customer', required=True, domain=[('customer','=',True)]),
        'close': fields.boolean('Mark Won', help='Check this to close the opportunity after having created the sales order.'),
        'date':fields.date('End Date'),
        'date_start': fields.date('Start Date'),
    }
    _defaults = {
        'close': False,
        'partner_id': _selectPartner,
        'date_start': lambda *a: time.strftime('%Y-%m-%d'),
    }