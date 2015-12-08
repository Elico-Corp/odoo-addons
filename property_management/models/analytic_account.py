# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-Today Serpent Consulting Services PVT LTD (<http://www.serpentcs.com>)
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
from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from openerp import tools, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class account_analytic_account(osv.osv):
    _inherit = "account.analytic.account"


    def _total_amount_rent(self, cr, uid, ids, name, arg, context=None):
        """
            used to calculate total_rent
        """
        res = {}
        tot = 0.00
        for tenancy_brw in self.browse(cr, uid, ids):
            for propety_brw in tenancy_brw.rent_schedule_ids:
                tot += propety_brw.amount
            res[tenancy_brw.id] = tot
        return res

    def _total_amount_deposit(self, cr, uid, ids, name, arg, context=None):
        """
            used to calculate total deposit
        """
        res = {}
        tot = 0.00
        for tenancy_brw in self.browse(cr, uid, ids):
            res[tenancy_brw.id] = tenancy_brw.amount_fee_paid
        return res

    def _get_deposit(self, cr, uid, ids, name, arg, context=None):
        """
            used to calculate total deposit received
        """
        res = {}
        voucher_pool = self.pool.get('account.voucher')
        move_line_pool = self.pool.get('account.voucher.line')
        for tennancy in self.browse(cr, uid, ids, context=context):
            res[tennancy.id] = {'deposit_return':False, 'deposit_received':False}
            voucher_id = voucher_pool.search(cr, uid, [('tenancy_id', '=', tennancy.id), ('state', '=', 'posted')])
            if voucher_id:
                for voucher in voucher_pool.browse(cr, uid, voucher_id):
                    if voucher.type == 'payment':
                        res[tennancy.id]['deposit_return'] = True
                    elif voucher.type == 'receipt' and tennancy.total_deposit == voucher.amount:
                        res[tennancy.id]['deposit_received'] = True
        return res

#    def _total_amount_due(self, cr, uid, ids, name, arg, context=None):
#        res = {}
#        return res

#    def _total_amount_os_date(self, cr, uid, ids, name, arg, context=None):
#        res = {}
#        return res

#    def _total_amount_paid_date(self, cr, uid, ids, name, arg, context=None):
#        res = {}
#        return res

#    def _total_amount_os_altogether(self, cr, uid, ids, name, arg, context=None):
#        res = {}
#        return res



    _columns = {
              'brokerage_fee':fields.float('Brokerage Fee'),
              'rent':fields.float('Rent'),
              'deposit':fields.float('Deposit'),
              'contract_type':fields.selection([('first', '1st Contract'),
                                               ('renewal', 'Renewal'),
                                               ('extension', 'Extension'),
                                               ('amendment', 'Amendment'),], 'Contract Type'),
              'rel_contract_attachment':fields.binary("Tenancy Contract"),
              'property_id':fields.many2one('account.asset.asset','Property'),
              'account_move_line_ids': fields.one2many('account.move.line', 'asset_id', 'Entries', readonly=True, states={'draft':[('readonly',False)]}),
              'history_ids': fields.one2many('account.asset.history', 'asset_id', 'History', readonly=True),
              'tenant_id':fields.many2one('tenant.partner', 'Tenant', domain="[('tenant', '=', True)]"),
              'early_warning':fields.boolean('Early Warning'),
              'ew_weeks':fields.integer('EW Weeks'),
              'total_rent':fields.function(_total_amount_rent, method=True, type='float', string='Total Rent', readonly=True,store=True),
              'total_deposit':fields.function(_total_amount_deposit, method=True, type='float', string='Total Deposit', readonly=True,store=True),
              'deposit_scheme_type':fields.selection([('insurance', 'Insurance-based'),
                                               ], 'Type Of Scheme'),
              'contact_id':fields.many2one('res.partner', 'Contact',),
              'amount_fee_paid':fields.integer('Amount Of Fee Paid'),
              'duration_cover':fields.text('Duration Of Cover'),
              'amount_return':fields.integer('Amount Returned'),
              'date_return':fields.date('Date Returned'),
              'utility_ids':fields.one2many('property.utility', 'tenancy_id', 'Utilities'),
              'rent_schedule_ids':fields.one2many('tenancy.rent.schedule', 'tenancy_id', 'Rent Schedule'),
#              'total_amount_due':fields.function(_total_amount_due, method=True, type='float', string='Total Amount Due'),
#              'total_amount_os_date':fields.function(_total_amount_os_date, method=True, type='float', string='Total Amount Outstanding To Date',),
#              'total_amount_paid_date':fields.function(_total_amount_paid_date, method=True, type='float', string='Total Amount Paid To date'),
#              'total_amount_os_altogether':fields.function(_total_amount_os_altogether, method=True, type='float', string='Total Amount Outstanding altogether'),
              'rel_property_id':fields.related('parent_id', 'property_id', type="many2one", relation="account.asset.asset", string="Property"),
              'contract_attachment' : fields.binary('Tenancy Contract'),
              'deposit_received': fields.function(_get_deposit, method=True, multi='deposit', type='boolean', string='Deposit Received?'),
              'deposit_return':fields.function(_get_deposit, method=True, multi='deposit', type='boolean', string='Deposit Returned?'),
              'doc_name' : fields.char('Filename'),
              'note':fields.text('Notes'),
              'is_property':fields.boolean('Is Property?'),
              'rent_entry_chck':fields.boolean('Rent Entries Check'),
              }

    _defaults = {
               'state': 'draft',
               'rent_entry_chck':False,
               }

    def create(self, cr, uid, vals, context=None):
        """
        This Method is used to overrides orm create method.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param vals: dictionary of fields value.
        @param context: A standard dictionary for contextual values
        """
        if vals.has_key('tenant_id'):
            vals.update({'is_property':True})
        tenant_name = vals.get('tenant_id')
        res = super(account_analytic_account, self).create(cr, uid, vals, context=context)
#        analytic_rec = self.pool.get('account.analytic.account').browse(cr, uid, res, context=context)
#        current_tenant = self.pool.get('account.asset.asset').write(cr, uid, [analytic_rec.property_id.id], 
#                                                                    {'current_tenant': analytic_rec.tenant_id.id,
#                                                                     'state':'normal'},
#                                                                     context=context)
        return res

    # while edit name of tenant, it will write in invisible field current tenant.
    def write(self, cr, uid, ids, vals, context=None):
        """
        This Method is used to overrides orm write method.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param vals: dictionary of fields value.
        @param context: A standard dictionary for contextual values
        """
        asset_obj = self.pool.get('account.asset.asset')
        tenant_contract_rec = self.browse(cr, uid, ids, context=context)
        tenant_name = tenant_contract_rec.tenant_id.id
        rec = super(account_analytic_account, self).write(cr, uid, ids, vals, context=context)
        if vals.get('state'):
            if vals['state'] == 'open':
                current_tenant = asset_obj.write(cr, uid, [tenant_contract_rec.property_id.id],
                                                 {'current_tenant': tenant_contract_rec.tenant_id.id,
                                                  'state': 'normal'},
                                                 context=context)
            if vals['state'] == 'close':
                current_tenant = asset_obj.write(cr, uid, [tenant_contract_rec.property_id.id],
                                                 {'state': 'draft','current_tenant':False},
                                                 context=context)
        return rec


    def button_receive(self, cr, uid, ids, context=None):
        """
            used to open the related account voucher form view
        """
        if not ids: return []
        inv = self.browse(cr, uid, ids[0], context=context)
        obj_ir_model_data = self.pool.get('ir.model.data')
        ir_id = obj_ir_model_data._get_id(cr, uid, 'account_voucher', 'view_voucher_form')
        ir_rec = obj_ir_model_data.browse(cr, uid, ir_id, context=context)
        line_data = []
        line_data.append({'name' : 'deposit', 'account_id' : inv.tenant_id.parent_id.property_account_receivable.id, 'type' : 'cr', 'property_id' : inv.property_id.id, 'amount' : inv.deposit})
        return {
            'view_mode': 'form',
            'view_id': [ir_rec.res_id],
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]',
            'context': {
                'default_partner_id': inv.tenant_id.parent_id.id,
                'default_journal_id' : 17,
                'default_type' : 'receipt',
                'default_reference':inv.name,
                'default_line_ids' : line_data,
                'default_tenancy_id' : inv.id,
                'close_after_process': True,
                }
        }

    def button_return(self, cr, uid, ids, context=None):
            inv = self.browse(cr, uid, ids[0], context=context)
            obj_ir_model_data = self.pool.get('ir.model.data')
            ir_id = obj_ir_model_data._get_id(cr, uid, 'account_voucher', 'view_voucher_form')
            ir_rec = obj_ir_model_data.browse(cr, uid, ir_id, context=context)
            line_data = []
            line_data.append({'name' : 'deposit', 'property_id' : inv.property_id.id, 'account_id' : inv.tenant_id.parent_id.property_account_receivable.id, 'type' : 'dr', 'amount' : inv.amount_return})
            return {
                
                'view_mode': 'form',
                'view_id': [ir_rec.res_id],
                'view_type': 'form',
                'res_model': 'account.voucher',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'domain': '[]',
                'context': {
                    'default_partner_id': inv.tenant_id.parent_id.id,
                    'default_journal_id' : 17,
                    'default_type' : 'payment',
                    'default_reference':inv.name,
                    'default_line_ids' : line_data,
                    'default_tenancy_id' : inv.id,
                    'close_after_process': True
                    }
            }


    def button_start(self, cr, uid, id, context=None):
        current_rec = self.browse(cr, uid , id[0])
        if current_rec.name == '/': 
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'property.analytic.number'),
            self.write(cr, uid, id, {'name':sequence[0]})
        return self.write(cr, uid, id, {'state':'open'})

    def button_close(self, cr, uid, id, context=None):
        return self.write(cr, uid, id, {'state':'close'})

    def button_set_to_draft(self, cr, uid, id, context=None):
        return self.write(cr, uid, id, {'state':'draft'})

    def cron_property_states_changed(self, cr, uid, context=None):
        date = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        date_now = datetime.strptime( date, DEFAULT_SERVER_DATE_FORMAT)
        close_tncy_ids = self.search(cr, uid, [('state','=','close')], context=context)
        tncy_ids = self.search(cr, uid, [('date_start','<=',date_now),('date','>=',date_now),('state','=','open')], context=context)
        for tncy_data in self.browse(cr, uid, tncy_ids, context = context):
            property_id = tncy_data.property_id
            if property_id:
                self.pool.get('account.asset.asset').write(cr, uid, property_id.id, {'state':'normal','color':7}, context=context)
        for tncy_data in self.browse(cr, uid, close_tncy_ids, context = context):
            property_id = tncy_data.property_id
            if property_id:
                self.pool.get('account.asset.asset').write(cr, uid, property_id.id, {'state':'draft','color':4}, context=context)
        return True 

    def cron_property_tenancy(self, cr, uid, context=None):
        """
            This Method is called by Scheduler to send email to tenant as a reminder for rent payment
        """
        lst = []
        tncy_ids = self.search(cr, uid, [], context=context)
        date = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        date_now = datetime.strptime( date, DEFAULT_SERVER_DATE_FORMAT)
        for tncy_data in self.browse(cr, uid, tncy_ids, context = context):
            date_start_str = datetime.strptime( tncy_data.date_start, DEFAULT_SERVER_DATE_FORMAT)
            diff = date_start_str - timedelta(days=7)
            if  diff <= date_now:
                for line in tncy_data.rent_schedule_ids:
                    if not line.move_check:
                        lst.append(tncy_data.id)
        set_lst = list(set(lst))
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'property_management', 'property_email_template')[1]
        for tenant in self.pool.get('tenant.partner').browse(cr, uid, set_lst, context=context):
            self.pool.get('email.template').send_mail(cr, uid, template_id, tenant.id, force_send=True, context=context)
        return True

    def create_rent_schedule(self, cr, uid, ids, context=None):
        """
            used to create rent schedule information
        """
        year_create = []
        res = self.browse(cr, uid, ids, context=context)
        period = res['recurring_rule_type']
        starting_date = res['date_start']
        ending_date = res['date']
        rent = res['rent']
        cr.execute("SELECT start_date FROM tenancy_rent_schedule WHERE tenancy_id=%s" % ids[0])
        exist_dates = cr.fetchall()
        date_add = self.date_addition(starting_date, ending_date, period)
        exist_dates = map(lambda x:x[0], exist_dates)
        result = list(set(date_add) - set(exist_dates))
        for dates in result:
            year_create.append((0, 0, {
                     'start_date':dates,
                     'tenancy_id':ids[0],
                     'amount':rent,
                     'property_id':res.property_id and res.property_id.id or False
                    }))
        return self.write(cr, uid, ids, {'rent_schedule_ids':year_create,'rent_entry_chck':True})

    def date_addition(self, starting_date, end_date, period):
        date_list = []
        if period == 'monthly':
            while starting_date < end_date:
                date_list.append(starting_date)
                res = ((datetime.strptime(starting_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(months=1)).strftime(DEFAULT_SERVER_DATE_FORMAT))
                starting_date = res
            return date_list
        elif period == 'half_yearly':
            while starting_date < end_date:
                date_list.append(starting_date)
                res = ((datetime.strptime(starting_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(months=6)).strftime(DEFAULT_SERVER_DATE_FORMAT))
                starting_date = res
            return date_list
        else:
            while starting_date < end_date:
                date_list.append(starting_date)
                res = ((datetime.strptime(starting_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(years=1)).strftime(DEFAULT_SERVER_DATE_FORMAT))
                starting_date = res
            return date_list


class account_voucher(osv.Model):
    _inherit = "account.voucher"

    _columns = {
            'tenancy_id':fields.many2one('account.analytic.account', 'Tenancy'),
                }


class account_voucher_line(osv.Model):
    _inherit = "account.voucher.line"
    
    _columns = {
            'tenancy_rent_id':fields.many2one('tenancy.rent.schedule', 'Tenancy Rent'),
            'property_id' : fields.many2one('account.asset.asset', 'Property')
                }
    
    def onchange_tenant_rent(self, cr, uid, id, tenancy_rent_id, context=None):
        rent_amount = 0.00 
        if tenancy_rent_id:
            tenancy_rent_brw = self.pool.get('tenancy.rent.schedule').browse(cr, uid, tenancy_rent_id)
            rent_amount = tenancy_rent_brw.amount
        return {'value':{'amount':rent_amount}}


class account_move_line(osv.Model):
    _inherit = "account.move.line"
    _columns = {
              'property_id':fields.many2one('account.asset.asset', 'Property'),
              }
