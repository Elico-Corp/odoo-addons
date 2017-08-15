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
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from openerp import tools, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
import webbrowser
from openerp.exceptions import except_orm, Warning, RedirectWarning


class tenant_partner(osv.Model):
    _name = "tenant.partner"
    _inherits = {'res.partner':'parent_id'}

    _columns = {
        'initials':fields.char('Initials', size=20),
        'tenant':fields.boolean('Tenant',),
        'tenancy_ids':fields.one2many('account.analytic.account', 'tenant_id', 'Tenancy'),
        'note':fields.text('Note'),
        'doc_name' : fields.char('Filename'),
        'id_attachment' : fields.binary('Identity Proof'),
        'agent':fields.boolean('Agent',),
        'tenant_ids':fields.many2many('tenant.partner', 'agent_tenant_rel', 'agent_id', 'tenant_id', 'Tenant detail',domain=[('customer', '=',True),('agent','=',False)]),
        'is_tenant':fields.boolean('Tenant'),
    }

    _defaults = {
               'tenant':True,
               }

    #while create tenant user(tenant or agent) will created and write in particular property group.
    def create(self, cr, uid, vals, context=None):
        dataobj = self.pool.get('ir.model.data')
        property_user = False
        tenant_name = vals.get('name')
        tenant_email = vals.get('email')
        res = super(tenant_partner, self).create(cr, uid, vals, context=context)
        tenant = self.browse(cr, uid, res, context=context)
        create_user = self.pool.get('res.users').create(cr,uid,{'login': tenant_email, 
                                                            'name': tenant_name, 
                                                            'tenant_id': res, 
                                                            'partner_id': tenant.parent_id.id},
                                                    context=context)
        if tenant.customer:
            property_user = dataobj.get_object_reference(cr, uid, 'property_management', 'group_property_user')
        if tenant.agent:
            property_user = dataobj.get_object_reference(cr, uid, 'property_management', 'group_property_agent')
        if property_user:
            self.pool.get('res.groups').write(cr, uid, property_user[1], {'users': [(4, create_user)]}, context=context)
        return res

    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(tenant_partner, self).default_get(cr, uid, fields, context=context)
        if context.get('tenant', False):
            res.update({
                        'tenant':context['tenant'],
                        })
        res.update({
                    'customer':False
                    })
        return res

class property_stage(osv.Model):
    _name = "property.stage"

    _columns = {
                'name':fields.char('Name', size=50, required=True)
                }

class property_type(osv.Model):
    _name = "property.type"

    _columns = {
                'name':fields.char('Name', size=50, required=True)
                }

class rent_type(osv.Model):
    _name = "rent.type"

    _columns = {
                'name':fields.char('Name', size=50, required=True)
                }

class room_type(osv.Model):
    _name = "room.type"

    _columns = {
                'name':fields.char('Name', size=50, required=True)
                }

class utility(osv.Model):
    _name = "utility"

    _columns = {
                'name':fields.char('Name', size=50, required=True)
                }

class property_phase(osv.Model):
    _name = "property.phase"

    _columns = {
            'phase_id':fields.many2one('account.asset.asset', 'Property'),
            'start_date':fields.date('Beginning date'),
            'end_date':fields.date('End Date'),
            'lease_price':fields.float('Sales/lease price per month'),
            'occupancy_rate':fields.float('Occupancy rate (in %)'),
            'operational_budget':fields.float('Operational budget (in %)'),
            'company_income':fields.float('Company Income Tax CIT (in %)'),
            'commercial_tax':fields.float('Commercial Tax (in %)')
        }

class property_photo(osv.Model):
    _name = "property.photo"

    _columns = {
        'photo_id':fields.many2one('account.asset.asset', 'Property'),
        'photos':fields.binary('Photos'),
        'doc_name' :fields.char('Filename'),
        'photos_description':fields.char('Description'),
        }

class sale_schedule(osv.Model):
    _name = "sale.schedule"

    _columns = {
                'sale_id':fields.many2one('account.asset.asset', 'Property'),
                'schedule_date':fields.date('Date'),
                'amount_curr':fields.float('Amount'),
                'amount_per':fields.float('Amount(%)'),
                'payment_detail':fields.char('Payment Detail'),
                'paid':fields.boolean('Paid'),
                'note':fields.text('Notes'),
                'remain_amount_per':fields.float('Remaining Amount(%)'),
                'remain_amount_curr':fields.float('Remaining Amount'),
                }

class property_sale(osv.Model):
    _name = "property.sale"

    _columns = {
                'sale_id':fields.many2one('account.asset.asset', 'Property'),
                'client_code':fields.integer('Client Code'),
                'client_name':fields.char('Client Name'),
                'broker_fee':fields.float('Brokerage Fee'),
                'sale_price':fields.float('Selling Price'),
                'contact_date':fields.date('Contract Date'),
                'contract':fields.binary('Contract'),
                'note':fields.text('Remarks')
                }

class property_room(osv.Model):
    _name = "property.room"

    _columns = {
              'name':fields.char('Name', size=60),
              'property_id':fields.many2one('account.asset.asset', 'Property'),
              'type_id':fields.many2one('room.type', 'Room Type'),
              'length':fields.float('Length'),
              'width':fields.float('Width'),
              'height':fields.float('Height'),
              'assets_ids':fields.one2many('room.assets', 'room_id', 'Assets'),
              'attach':fields.boolean('Attach Bathroom'),
              'note':fields.text('Notes'),
              'image':fields.binary('Picture'),
              }

class place_type(osv.Model):
    _name = 'place.type'

    _columns = {
                'name':fields.char('Place Type', size=50, required=True),
                }

class nearby_property(osv.Model):
    _name = 'nearby.property'
    
    _columns = {
                'name':fields.char('Name', size=100),
                'distance':fields.float('Distance'),
                'type':fields.many2one('place.type','Type'),
                'property_id':fields.many2one('account.asset.asset','Property'),
    }

class maintenance_type(osv.Model):
    _name = 'maintenance.type'

    _columns = {
                'name':fields.char('Maintenace Type', size=50, required=True),
                }

class property_maintenace(osv.Model):
    _name = "property.maintenance"

    _columns = {
                'state': fields.selection([('draft', 'Draft'), ('progress', 'In Progress'), ('incomplete', 'Incomplete'), ('done', 'Done')], 'State'),
                'date':fields.date('Date'),
                'name':fields.char('Description', size=100),
                'cost':fields.float('Cost'),
                'cost_type':fields.selection([('revenue','Revenue Cost'),
                                              ('average','Average Cost')],'Cost Type'),
                'property_id':fields.many2one('account.asset.asset','Property'),
                'type':fields.many2one('maintenance.type','Type'),
                'cost_type':fields.selection([('revenue', 'Revenue Cost'),
                                              ('average', 'Average Cost')], 'Cost Type'),
                'type':fields.many2one('maintenance.type', 'Type'),
                'assign_to':fields.many2one('res.partner','Assign To'),
                'account_code':fields.many2one('account.account','Account Code'),
                'renters_fault':fields.boolean('Renters Fault'),
                'invc_check':fields.boolean('Already created'),
                'last_record_update':fields.date('Last Record Update'),
                'invc_id':fields.many2one('account.invoice','Invoice Id'),
                }

    _defaults = {
               'state': 'draft',
               'renters_fault':True,
               'invc_check':False,
               }

    def create_invoice(self, cr, uid, id, context=None):
        """
        This Method is used to create invoice from maintenance record.
        """
        for data in self.browse(cr, uid, id, context=context):
            tncy_ids = [o.id for o in data.property_id.tenancy_property_ids]
            tenant_name = ''
            if not data.account_code:
                raise osv.except_osv(_("Warning!"), _("Please Select Account Code"))
            for tenancy_data in self.pool.get('account.analytic.account').browse(cr, uid, tncy_ids):
                if tenancy_data.state != 'close':
                    tenant_name = tenancy_data.tenant_id.name
                    tnt_number = tenancy_data.name
            partner_id = self.pool.get('res.partner').search(cr,uid,[('name','=',tenant_name)])
            if not partner_id:
                raise osv.except_osv(_("Warning!"), _("no current tenant for this property"))
            inv_line_values = {
                        'name':data.name or "",
                        'origin': 'property.maintenance',
                        'quantity': 1,
                        'price_unit': data.cost or 0.00,
                    }
            inv_values = {
                        'origin':data.name or "",
                        'type': 'out_invoice',
                        'partner_id' : partner_id[0] or False,
                        'account_id' : data.account_code.id or False,
                        'invoice_line': [(0, 0, inv_line_values)],
                        'amount_total' : data.cost or 0.0,
                        'date_invoice' : datetime.now().strftime('%Y-%m-%d') or False,
                        'number': tnt_number or '',
                    }
            acc_id= self.pool.get('account.invoice').create(cr, uid, inv_values, context = context)
            self.write(cr, uid, id, {'renters_fault':False,'invc_check':True,'invc_id':acc_id})
        return True

    def create(self, cr, uid, vals, context=None):
        vals['last_record_update'] = fields.datetime.now()
        res = super(property_maintenace, self).create(cr, uid, vals, context=context)
        return res

    def open_invoice(self, cr, uid, id, context=None):
        """
        This Method is used to Open invoice from maintenance record.
        """
        wiz_form_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'invoice_form')[1]
        self_data = self.browse(cr, uid, id, context = context)
        return {
            'view_type': 'form',
            'view_id': wiz_form_id,
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'res_id':self_data.invc_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': context,
            }
        return True


class cost_cost(osv.Model):
    _name = "cost.cost"

    def _get_move_check(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = bool(line.move_id)
        return res

    _columns = {
                'currency_id': fields.many2one('res.currency', 'Currency'),
                'name':fields.char('Description', size=100),
                'date':fields.date('Date'),
                'amount':fields.float('Amount'),
                'move_id': fields.many2one('account.move', 'Purchase Entry'),
                'purchase_property_id':fields.many2one('account.asset.asset', 'Property'),
                'sale_property_id':fields.many2one('account.asset.asset', 'Property'),
                'move_check': fields.function(_get_move_check, method=True, type='boolean', string='Posted', store=True),
                'payment_details':fields.char('Payment Details',size=100),
                'remaining_amount':fields.float('Remaining Amount', help='Shows remaining amount in currency'),
                'rmn_amnt_per':fields.float('Remaining Amount In %', help='Shows remaining amount in Percentage'),
                }
    _order = 'date'

    def create_move(self, cr, uid, ids, context=None):
        context = dict(context or {})
        can_close = False
        asset_obj = self.pool.get('account.asset.asset')
        period_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        created_move_ids = []
        asset_ids = []
        journal_id = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'purchase')])
        for line in self.browse(cr, uid, ids, context=context):
            depreciation_date = datetime.now()
            period_ids = period_obj.find(cr, uid, depreciation_date, context=context)
            company_currency = line.purchase_property_id.company_id.currency_id.id
            current_currency = line.purchase_property_id.currency_id.id
            sign = -1
            asset_name = line.purchase_property_id.name
            reference = line.purchase_property_id.code
            move_vals = {
                'name': asset_name,
                'date': depreciation_date,
                'ref': reference,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id[0],
                }
            move_id = move_obj.create(cr, uid, move_vals, context=context)
            if not line.purchase_property_id.partner_id:
                raise Warning(_('Please Select Partner From Genral Tab'))
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.purchase_property_id.partner_id.property_account_payable.id or False,
                'debit': 0.0,
                'credit': line.amount,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id[0],
                'partner_id': line.purchase_property_id.partner_id.id or False,
                'currency_id': company_currency != current_currency and  current_currency or False,
                'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
                'date': depreciation_date,
            })
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.purchase_property_id.category_id.account_asset_id.id,
                'credit': 0.0,
                'debit': line.amount,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id[0],
                'partner_id': line.purchase_property_id.partner_id.id or False,
                'currency_id': company_currency != current_currency and  current_currency,
                'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
                'analytic_account_id': line.purchase_property_id.analytic_acc_id.id or False,
                'date': depreciation_date,
                'asset_id': line.purchase_property_id.id or False,
            })
            self.write(cr, uid, line.id, {'move_id': move_id}, context=context)
            created_move_ids.append(move_id)
            asset_ids.append(line.purchase_property_id.id)
        return created_move_ids


class room_assets(osv.Model):
    _name = "room.assets"

    _columns = {
                'date':fields.date('Date'),
                'name':fields.char('Description', size=60),
                'type':fields.selection([('fixed', 'Fixed Assets'),
                                         ('movable', 'Movable Assets'),
                                         ('other', 'Other Assets')], 'Type'),
                'qty':fields.float('Quantity'),
                'room_id':fields.many2one('property.room', 'Property'),
                } 


class property_insurance(osv.Model):
    _name = "property.insurance"

    _columns = {
              'name':fields.char('Description', size=60),
              'policy_no':fields.char('Policy Number', size=60),
              'start_date':fields.date('Start Date'),
              'end_date':fields.date('End Date'),
              'premium':fields.float('Premium'),
              'contact':fields.many2one('res.company', 'Contact'),
              'reference':fields.char('Reference', size=60),
              'expiry':fields.date('Expiry Date'),
              'insured_amount':fields.float('Insured Amount'),
              'weeks':fields.integer('Weeks'),
              'print':fields.boolean('Print'),
              'ew':fields.boolean('EW'),
              'payment_mode_type':fields.selection([('monthly', 'Monthly'), ('semi_annually', 'Semi Annually'),('yearly', 'Annually')], 'Payment Term', size=40),
              'property_insurance_id':fields.many2one('account.asset.asset', 'Property'),
              'company_id':fields.many2one('res.company', 'Related Company'),
              'doc_name' : fields.char('Filename'),
              'contract':fields.binary('Contract')
              }


class rent_payment(osv.Model):
    _name = "rent.payment"

    _columns = {
              'payment_date':fields.date("Date"),
              'amount_paid':fields.float('Amount Paid'),
              'description':fields.text('Description'),
              'rent_payment_id':fields.many2one('account.asset.asset', 'Property'),
              }


class property_rates(osv.Model):
    _name = "property.rates"

    _columns = {
              'name':fields.char('Description', size=60),
              'start_date':fields.date('Start Date'),
              'end_date':fields.date('End Date'),
              'cost':fields.float('Cost'),
              'payment_mode_type':fields.selection([('monthly', 'MONTHLY'), ('yearly', 'YEARLY')], 'Payment Mode', size=40),
              'property_rate_id':fields.many2one('account.asset.asset', 'Property'),
              }


class tenancy_rent_schedule(osv.Model):
    _name = "tenancy.rent.schedule"
    _rec_name = "tenancy_id"

    def _get_move_check(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = bool(line.move_id)
        return res

    _columns = {
              'move_id': fields.many2one('account.move', 'Depreciation Entry'),
              'tenancy_id':fields.many2one('account.analytic.account', 'Tenancy',),
              'property_id':fields.many2one('account.asset.asset', 'Property'),
              'start_date':fields.date('Date'),
              'end_date':fields.date('End Date'),
              'amount':fields.float('Amount'),
              'note':fields.text('Notes'),
              'bad':fields.boolean('Bad'),
              'advance':fields.boolean('Advance'),
              'cheque_detail':fields.char('Cheque Detail', size=30),
              'paid':fields.boolean('Paid', help="True if this rent is paid by tenant", readonly=True),
              'move_check': fields.function(_get_move_check, method=True, type='boolean', string='Posted', store=True),
              'rel_tenant_id':fields.related('tenancy_id', 'tenant_id', type="many2one", relation="tenant.partner", string="Tenant", store=True),
              'company_id':fields.many2one('res.company', 'Related Company'),
              }

    _order = 'start_date'

    def open_account_move(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param context: A standard dictionary for contextual values
        """
        open_move_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'view_move_form')[1]
        open_move_obj = self.browse(cr, uid, ids, context=context)
        return {
                'view_type': 'form',
                'view_id': open_move_id,
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id':open_move_obj.move_id.id,
                'type': 'ir.actions.act_window',
                'target': 'current',
                'context': context,
                }

    def create_move(self, cr, uid, ids, context=None):
        context = dict(context or {})
        can_close = False
        asset_obj = self.pool.get('account.asset.asset')
        period_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        created_move_ids = []
        asset_ids = []
        journal_id = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'sale')])
        for line in self.browse(cr, uid, ids, context=context):
            depreciation_date = datetime.now()
            period_ids = period_obj.find(cr, uid, depreciation_date, context=context)
            company_currency = line.tenancy_id.company_id.currency_id.id
            current_currency = line.tenancy_id.currency_id.id
            sign = -1
            asset_name = line.tenancy_id.name
            reference = line.tenancy_id.code
            move_vals = {
                'name': asset_name,
                'date': depreciation_date,
                'ref': reference,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id[0],
                }
            move_id = move_obj.create(cr, uid, move_vals, context=context)
            if not line.tenancy_id.property_id.income_acc.id:
                raise Warning(_('Please Configure Income Account from Property'))
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.tenancy_id.property_id.income_acc.id or False,
                'debit': 0.0,
                'credit': line.tenancy_id.rent,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id[0],
                'partner_id': line.tenancy_id.tenant_id.id or False,
                'currency_id': company_currency != current_currency and  current_currency or False,
                'amount_currency': company_currency != current_currency and - sign * line.tenancy_id.rent or 0.0,
                'date': depreciation_date,
            })
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.tenancy_id.tenant_id.property_account_receivable.id,
                'credit': 0.0,
                'debit': line.tenancy_id.rent,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id[0],
                'partner_id': line.tenancy_id.tenant_id.id or False,
                'currency_id': company_currency != current_currency and  current_currency,
                'amount_currency': company_currency != current_currency and sign * line.tenancy_id.rent or 0.0,
                'analytic_account_id': line.tenancy_id.id,
                'date': depreciation_date,
                'asset_id': line.tenancy_id.property_id.id or False,
            })
            self.write(cr, uid, line.id, {'move_id': move_id}, context=context)
            created_move_ids.append(move_id)
            asset_ids.append(line.tenancy_id.id)
        return created_move_ids


class property_utility(osv.Model):
    _name = "property.utility"

    _columns = {
              'utility_id':fields.many2one('utility', 'Utility'),
              'contact_id':fields.many2one('tenant.partner', 'Contact', domain="[('tenant', '=', True)]"),
              'ref':fields.char('Reference', size=60),
              'property_id':fields.many2one('account.asset.asset', 'Property'),
              'tenancy_id':fields.many2one('account.analytic.account', 'Tenancy'),
              'reading':fields.integer('Reading'),
              'note':fields.text('Remarks'),
              'issue_date':fields.date('Issuance Date'),
              'expiry_date':fields.date('Expiry Date'),
              }


class property_safety_certificate(osv.Model):
    _name = "property.safety.certificate"

    _columns = {
              'name':fields.char('Certificate', size=60, required=True),
              'contact_id':fields.many2one('tenant.partner', 'Contact', domain="[('tenant', '=', True)]"),
              'ref':fields.char('Reference', size=60),
              'expiry_date':fields.date('Expiry Date'),
              'ew':fields.boolean('EW'),
              'weeks':fields.integer('Weeks'),
              'property_id':fields.many2one('account.asset.asset', 'Property'),
              }

class property_attachment(osv.Model):
    _name = 'property.attachment'

    _columns = {
        'name' : fields.char('Description', size=64, requiered=True),
        'expiry_date' : fields.date('Expiry date'),
        'contract_attachment' : fields.binary('Attachment'),
        'property_id' : fields.many2one('account.asset.asset', 'Property'),
        'doc_name' : fields.char('Filename'),
    }

class sale_cost(osv.Model):
    _name = "sale.cost"

    def _get_move_check(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = bool(line.move_id)
        return res

    _columns = {
                'currency_id': fields.many2one('res.currency', 'Currency'),
                'name':fields.char('Description', size=100),
                'date':fields.date('Date'),
                'amount':fields.float('Amount'),
                'move_id': fields.many2one('account.move', 'Purchase Entry'),
                'purchase_property_id':fields.many2one('account.asset.asset', 'Property'),
                'sale_property_id':fields.many2one('account.asset.asset', 'Property'),
                'move_check': fields.function(_get_move_check, method=True, type='boolean', string='Posted', store=True),
                'payment_details':fields.char('Payment Details',size=100),
                'remaining_amount':fields.float('Remaining Amount', help='Shows remaining amount in currency'),
                'rmn_amnt_per':fields.float('Remaining Amount In %', help='Shows remaining amount in Percentage'),
                }
    _order = 'date'

    def create_move(self, cr, uid, ids, context=None):
        context = dict(context or {})
        can_close = False
        asset_obj = self.pool.get('account.asset.asset')
        period_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        created_move_ids = []
        asset_ids = []
        journal_id = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'sale')])
        for line in self.browse(cr, uid, ids, context=context):
            depreciation_date = datetime.now()
            period_ids = period_obj.find(cr, uid, depreciation_date, context=context)
            company_currency = line.sale_property_id.company_id.currency_id.id
            current_currency = line.sale_property_id.currency_id.id
            sign = -1
            asset_name = line.sale_property_id.name
            reference = line.sale_property_id.code
            move_vals = {
                'name': asset_name,
                'date': depreciation_date,
                'ref': reference,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id[0],
                }
            move_id = move_obj.create(cr, uid, move_vals, context=context)
            if not line.sale_property_id.customer_id:
                raise Warning(_('Please Select Customer'))
            if not line.sale_property_id.income_acc:
                raise Warning(_('Please Select Income Account'))
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.sale_property_id.income_acc.id or False,
                'debit': 0.0,
                'credit': line.amount,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id[0],
                'partner_id': line.sale_property_id.customer_id.id or False,
                'currency_id': company_currency != current_currency and  current_currency or False,
                'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
                'date': depreciation_date,
            })
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.sale_property_id.customer_id.property_account_receivable.id or False,
                'credit': 0.0,
                'debit': line.amount,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id[0],
                'partner_id': line.sale_property_id.customer_id.id or False,
                'currency_id': company_currency != current_currency and  current_currency,
                'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
                'analytic_account_id': line.sale_property_id.analytic_acc_id.id or False,
                'date': depreciation_date,
                'asset_id': line.sale_property_id.id or False,
            })
            self.write(cr, uid, line.id, {'move_id': move_id}, context=context)
            created_move_ids.append(move_id)
            asset_ids.append(line.sale_property_id.id)
        return created_move_ids
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
