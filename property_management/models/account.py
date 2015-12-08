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
import time
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from openerp import tools, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import webbrowser
from openerp.exceptions import except_orm, Warning, RedirectWarning

class account_asset_asset(osv.osv):
    _inherit = 'account.asset.asset'
    _description = 'Asset'

    def create(self, cr, uid, vals, context=None):
        asset_id = super(account_asset_asset, self).create(cr, uid, vals, context=context)
        rec = {
               'name':vals['name'],
               }
        acc_analytic_id = self.pool.get('account.analytic.account').create(cr, uid, rec, context=context)
        return asset_id

    def write(self, cr, uid, ids, vals, context=None):
        if vals.has_key('state') and vals['state'] == 'new_draft':
            vals.update({'color':0})
        if vals.has_key('state') and vals['state'] == 'draft':
            vals.update({'color':4})
        if vals.has_key('state') and vals['state'] == 'book':
            vals.update({'color':2})
        if vals.has_key('state') and vals['state'] == 'normal':
            vals.update({'color':7})
        if vals.has_key('state') and vals['state'] == 'close':
            vals.update({'color':9})
        if vals.has_key('state') and vals['state'] == 'sold':
            vals.update({'color':9})
        if vals.has_key('state') and vals['state'] == 'cancel':
            vals.update({'color':1})
        ret_val = super(account_asset_asset, self).write(cr, uid, ids, vals, context=context)
        return ret_val


    @api.multi
    def _has_image(self, name, args):
        return dict((p.id, bool(p.image)) for p in self)

    def occupancy_calculation(self, cr, uid, ids, field_name, arg, context=None):
       """
            This Method is used to calculate occupancy
       """
       rec = {}
       occ = 0
       for res in self.browse(cr, uid, ids, context=None):
           cur_datetime = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
           cur_datetime = datetime.strptime(cur_datetime, DEFAULT_SERVER_DATE_FORMAT)
           purchase_date = datetime.strptime(res.purchase_date, DEFAULT_SERVER_DATE_FORMAT)
           purchase_diff2 = cur_datetime - purchase_date
           purchase_diff = purchase_diff2.days
           diff = 0
           for i in res.tenancy_property_ids:
               if i.date and i.date_start:
                   diff2 = datetime.strptime(i.date, DEFAULT_SERVER_DATE_FORMAT) - datetime.strptime(i.date_start, DEFAULT_SERVER_DATE_FORMAT)
                   diff = diff + diff2.days
           if (purchase_diff != 0):
               occ = (diff * 100) / (purchase_diff)
               rec[res.id] = occ
       return rec

    def sales_rate_calculation(self, cr, uid, ids, field_name, arg, context=None):
       """
            This Method is used to calculate occupancy
       """
       rec = {}
       sales_rate = 0
       counter = 0
       sr = 0
       for res in self.browse(cr, uid, ids, context=None):
           for i in res.property_phase_ids:
                   counter = counter + 1
                   sales_rate = sales_rate + i.lease_price
           if (counter != 0):
                 sr = sales_rate / counter
       rec[res.id] = sr
       return rec

    def roi_calculation(self, cr, uid, ids, field_name, arg, context=None):
       """
            This Method is used to Calculate ROI.
        """
       rec = {}
       cost_of_investment = 0
       gain_from_investment = 0
       roi = 0
       for res in self.browse(cr, uid, ids, context=None):
           for maintenance in res.maintenance_ids:
               cost_of_investment = cost_of_investment + maintenance.cost
           for gain in res.tenancy_property_ids:
               gain_from_investment = gain_from_investment + gain.rent
       if (cost_of_investment != 0):
           roi = (gain_from_investment - cost_of_investment) / cost_of_investment
       rec[res.id] = roi
       return rec

    def ten_year_roi_calculation(self, cr, uid, ids, field_name, arg, context=None):
        
        rec = {}
        ten_roi = 0
        roi = 0
        for res in self.browse(cr, uid, ids, context=None):
            roi = res.roi
        ten_roi = 10 * roi
        rec[res.id] = ten_roi
        return rec

    def return_period(self, cr, uid, ids, field_name, arg, context=None):
         """
            This Method is used to Calculate Return Period.
         """
         rec = {}
         rp = 0
         for res in self.browse(cr, uid, ids, context=None):
             purchase_price = res.purchase_price
             rent = res.ground_rent
             if (rent != 0):
                 rp = purchase_price / rent
         rec[res.id] = rp
         return rec

    def operation_cost(self, cr, uid, ids, field_name, arg, context=None):
         """
            This Method is used to Calculate Operation Cost.
         """
         rec = {}
         operational_cost = 0
         counter = 0
         oc = 0
         gain_from_investment = 0
         
         for res in self.browse(cr, uid, ids, context=None):
             for gain in res.tenancy_property_ids:
               gain_from_investment = gain_from_investment + gain.rent
             for i in res.property_phase_ids:
                 counter = counter + 1
                 operational_cost = operational_cost + i.operational_budget
             if (gain_from_investment != 0):
                 oc = operational_cost / gain_from_investment
         rec[res.id] = oc
         return rec
         

    def cal_simulation(self, cr, uid, ids, field_name, arg, context=None):
        """
            used to calculate simulation which is used in BI charts
        """
        rec = {}
        amt = 0.0
        for property_data in self.browse(cr, uid, ids, context=context):
            tncy_lst = [tncy.id for tncy in property_data.tenancy_property_ids]
            set_lst = set(tncy_lst)
            sort_tncy = list(set_lst)
            for tncy_data in self.pool.get('account.analytic.account').browse(cr, uid, sort_tncy, context=context):
                for prty_tncy_data in tncy_data.rent_schedule_ids:
                    amt += prty_tncy_data.amount
        return {ids[0]:amt}

    def cal_revenue(self, cr, uid, ids, field_name, arg, context=None):
        """
            used to calculate revenue which is used in BI charts
        """
        amt = 0.0
        for property_data in self.browse(cr, uid, ids, context=context):
            tncy_lst = [tncy.id for tncy in property_data.tenancy_property_ids]
            set_lst = set(tncy_lst)
            sort_tncy = list(set_lst)
            for tncy_data in self.pool.get('account.analytic.account').browse(cr, uid, sort_tncy, context=context):
                for prty_tncy_data in tncy_data.rent_schedule_ids:
                    if prty_tncy_data.move_check == True:
                        amt += prty_tncy_data.amount
        return {ids[0]:amt}
    
    def parent_property_calculation(self, cr, uid, ids, field_name, arg, context=None):
         """
            This Method is used to get Parent Properties from all properties.
         """
         rec = {}
         property_list = []
         sub_property_list = [] 
         for property_data in self.browse(cr, uid, ids):
            if property_data.child_ids:
                for sub in property_data.child_ids:
                    sub_property_list.append(sub.id)
                property_list.append(property_data.name)
                rec[property_data.id] = property_data.name
            else:
                if property_data.id not in sub_property_list:
                    property_list.append(property_data.name)
                    rec[property_data.id] = property_data.name
         return rec

    def sub_property_calculation(self, cr, uid, ids, field_name, arg, context=None):
         """
            This Method is used to get Sub Properties from all properties.
         """
         rec = {}
         sub_property_list = []
         for property_data in self.browse(cr, uid, ids):
            if property_data.child_ids:
                for sub in property_data.child_ids:
                    rec[property_data.id] = sub.name
         return rec

    def expence_calculation(self, cr, uid, ids, field_name, arg, context=None):
         """
            This Method is used to Calculate Expence.
         """
         rec = {}
         maintenance_obj = self.pool.get('property.maintenance')
         m_ids = maintenance_obj.search(cr, uid, [])
         for res in maintenance_obj.browse(cr, uid, m_ids, context=None):
             rec[res.id] = res.type.name
         return rec
     
    def cal_total_price(self, cr, uid, ids, field_name, arg, context=None):
         """
            This Method is used to Calculate Total Price.
         """
         rec = {}
         total_price = 0 
         up = 0
         gfa = 0
         for property_data in self.browse(cr, uid, ids):
                    gfa = property_data.gfa_feet
                    up = property_data.unit_price
         total_price = gfa * up
         rec[property_data.id] = total_price
         return rec
     
    def _get_ground_rent(self, cr, uid, ids, context=None):
        """
            Returns keys of dictionary from account_asset_asset. 
        """
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            result[line.ground_rent] = True
        return result.keys()
     
    def _get_rent(self, cr, uid, ids, context=None):
        """
            Returns keys of dictionary from account_analytic_account. 
        """
        result = {}
        for line in self.pool.get('account.analytic.account').browse(cr, uid, ids, context=context):
            result[line.property_id.id] = True
        return result.keys()

    def get_date(self, cr, uid, ids, context=None):
        """
            Returns keys of dictionary from account_analytic_account. 
        """
        result = {}
        for line in self.pool.get('account.analytic.account').browse(cr, uid, ids, context=context):
            result[line.property_id.id] = True
        return result.keys()
    
    def _get_type(self, cr, uid, ids, context=None):
        """
            Returns keys of dictionary from property_maintenance. 
        """
        result = {}
        for line in self.pool.get('property.maintenance').browse(cr, uid, ids, context=context):
            result[line.type] = True
        return result.keys() 
    
    def get_amt_test(self, cr, uid, ids, context=None):
        """
            Returns keys of dictionary from account_analytic_account.
        """
        result = {}
        for line in self.pool.get('account.analytic.account').browse(cr, uid, ids, context=context):
            result[line.property_id.id] = True
        return result.keys()

    def _get_check(self, cr, uid, ids, context=None):
        """
            Returns keys of dictionary from tenancy_rent_schedule 
        """
        result = {}
        for line in self.pool.get('tenancy.rent.schedule').browse(cr, uid, ids, context=context):
            result[line.property_id.id] = True
        return result.keys()

    def _get_check_test(self, cr, uid, ids, context=None):
        """
            Returns keys of dictionary from tenancy_rent_schedule . 
        """
        result = {}
        for line in self.pool.get('tenancy.rent.schedule').browse(cr, uid, ids, context=context):
            result[line.property_id.id] = True
        return result.keys()

    def get_rpi(self, cr, uid, ids, context=None):
        """
            Returns keys of dictionary from tenancy_rent_schedule. 
        """
        result = {}
        for line in self.pool.get('tenancy.rent.schedule').browse(cr, uid, ids, context=context):
            result[line.tenancy_id.id] = True
        return result.keys()


    _columns = {
                'type_id':fields.many2one('property.type', 'Property Type',help='Property Type'),
                'furnished':fields.selection([('none', 'None'),
                                               ('semi_furnished', 'Semi Furnished'),
                                               ('full_furnished', 'Full Furnished')], 'Furnishing', help='Furnishing'),
                'state': fields.selection([('new_draft', 'Booking Open'), ('draft', 'Available'), ('book', 'Booked'), ('normal', 'On Lease'), ('close', 'Sale'), ('sold', 'Sold'), ('cancel', 'Cancel')], 'State', required=True),

                'contact_id':fields.many2one('tenant.partner', 'Contact Name', domain="[('tenant', '=', True)]"),
                'street': fields.char('Street'),
                'street2': fields.char('Street2'),
                'zip': fields.char('Zip', size=24, change_default=True),
                'township': fields.char('Township'),
                'city': fields.char('City'),
                'state_id': fields.many2one("res.country.state", 'State', ondelete='restrict'),
                'country_id': fields.many2one('res.country', 'Country', ondelete='restrict'),
                'room_ids':fields.one2many('property.room', 'property_id', 'Rooms'),
                'maintenance_ids':fields.one2many('property.maintenance', 'property_id', 'Maintenance'),
                'utility_ids':fields.one2many('property.utility', 'property_id', 'Utilities'),
                'safety_certificate_ids':fields.one2many('property.safety.certificate', 'property_id', 'Safety Certificate'),
                'note':fields.text('Notes'),
                'purchase_price':fields.float('Purchase Price', help='Purchase Price of the Property'),
                'multiple_owners':fields.boolean('Multiple Owners', help="Check this box if there is multiple Owner of the Property."),
                'total_owners':fields.integer('Number of Owners'),
                'purchase_cost_ids':fields.one2many('cost.cost', 'purchase_property_id', 'Costs'),
                'sale_date':fields.date('Sale Date', help='Sale Date of the Property'),
                'sale_price':fields.float('Sale Price', help='Sale Price of the Property'),
                'sale_cost_ids':fields.one2many('sale.cost', 'sale_property_id', 'Costs'),
                'rent_type_id':fields.many2one('rent.type', 'Rent Type', help='Type of the Rent'),
                'ground_rent':fields.float('Ground Rent'),
                'property_insurance_ids':fields.one2many('property.insurance', 'property_insurance_id', 'Insurance'),
                'property_rates_ids':fields.one2many('property.rates', 'property_rate_id', 'Rates'),
                'rent_payment_ids':fields.one2many('rent.payment', 'rent_payment_id', 'Payment'),
                'tenancy_property_ids':fields.one2many('account.analytic.account', 'property_id', 'Tenancy Property'),
                'contract_attachment_ids' : fields.one2many('property.attachment', 'property_id', 'Document'),
                'analytic_acc_id':fields.many2one('account.analytic.account', 'Anlytic Account'),
                'color': fields.integer('Color'),
                'sale_ids':fields.one2many('property.sale', 'sale_id', 'Sale'),
                'sale_schedule_ids':fields.one2many('sale.schedule', 'sale_id', 'Sale Schedule'),
                'gfa_feet':fields.float('GFA(Sqft)',help='Gross Floor Area in Square Feet'),
                'gfa_meter':fields.float('GFA(m)',help='Gross Floor Area in Meter'),
                'property_manager':fields.many2one('res.partner', 'Property Manager',help="Manager of Property"),
                'property_photo_ids':fields.one2many('property.photo', 'photo_id', 'Photos'),
                'image': fields.binary("Image"),
                'has_image': fields.function(_has_image, type="boolean"),
                'ownership':fields.selection([('freehold', 'Freehold'), ('freehold1', 'Freehold'), ('leasehold', 'Leasehold'), ('bot', 'BOT')], 'Ownership'),
                'green_vision_title':fields.char('Green Vision title'),
                'third_party_title':fields.char('Third Party title'),
                'conditions':fields.char('Conditions'),
                'start_date':fields.date('Start Date'),
                'end_date':fields.date('End Date'),
                'simulation_name':fields.char('Simulation name'),
                'simulation_date':fields.date('Simulation date'),
                'construction_cost':fields.char('Construction Cost'),
                'property_phase_ids':fields.one2many('property.phase', 'phase_id', 'Phase'),
                'financial_performance':fields.float('Financial performance(%)'),
                'roi':fields.function(roi_calculation, type="float", string="ROI", help="Return On Investment", store={
                                                 'account.analytic.account': (_get_rent, ['rent'], 20),
                                                'account.asset.asset': (lambda self, cr, uid, ids, c={}: ids, ['tenancy_property_ids,', 'maintenance_ids'], 10)}),
                'ten_year_roi':fields.function(ten_year_roi_calculation, type="float", string="10year ROI", help="10year Return On Investment"),
                'irr':fields.float('IRR'),
                'return_period':fields.function(return_period, type="float", string="Return Period(in Months)", store={
                                                                             'account.analytic.account': (_get_ground_rent, ['purchase_price', 'ground_rent'], 20),
                                                                             'account.asset.asset': (lambda self, cr, uid, ids, c={}: ids, ['purchase_price', 'ground_rent'], 10)}),
                'operational_costs':fields.function(operation_cost, type="float", string="Operational costs(%)", store={
                                                 'account.analytic.account': (_get_rent, ['rent'], 20),
                                                'account.asset.asset': (lambda self, cr, uid, ids, c={}: ids, ['tenancy_property_ids,','property_phase_ids'], 10)}),
                                                                                                                     #'account.analytic.account': (_get_tenancy_ids, ['tenancy_property_ids,','property_phase_ids'], 20)}),
                'sub_pro':fields.function(sub_property_calculation,type="char",string="Sub Property",store=True),
                'mmaintenance_id':fields.function(expence_calculation,type="char",string="Expence",store={
                                                 'property.maintenance': (_get_type, ['type'], 20),
                                                'property.maintenance': (lambda self, cr, uid, ids, c={}: ids, ['type'], 10)}),
                'crossovered_budget_line_property': fields.one2many('crossovered.budget.lines', 'analytic_account_id', 'Budget Lines'),
                'occupancy_rates':fields.function(occupancy_calculation, type="float", string="Occupancy rate", store={
                                                 'account.analytic.account': (get_date, ['date', 'date_start'], 20),
                                                'account.asset.asset': (lambda self, cr, uid, ids, c={}: ids, ['tenancy_property_ids,', 'purchase_date'], 10)}),
                'sales_rates':fields.function(sales_rate_calculation, type="float", string="Sales Rate"),
                'simulation' :fields.function(cal_simulation, type='float', string='Total Amount', store={
                                                'account.analytic.account': (get_amt_test, ['rent_schedule_ids'], 10),
                                                'tenancy.rent.schedule': (_get_check, ['amount'], 10),
                                                'account.asset.asset': (lambda self, cr, uid, ids, c={}: ids, ['tenancy_property_ids'], 10)}),
                'revenue' :fields.function(cal_revenue, type='float', string='Revenue',store={
                                                'tenancy.rent.schedule': (_get_check_test, [], 10),
                                                'account.asset.asset': (lambda self, cr, uid, ids, c={}: ids, ['tenancy_property_ids'], 10)}),
                'unit_price':fields.float('Unit Price'),
                'total_price':fields.function(cal_total_price, type='float', string='Total Price'),
                'depreciation_line_ids': fields.one2many('account.asset.depreciation.line', 'asset_id', 'Depreciation Lines', readonly=True, states={'draft':[('readonly', False)]}),
                'income_acc' : fields.many2one('account.account', 'Income Account'),
                'facing':fields.selection([('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')], 'Facing'),
                'age_of_property':fields.date('Age of Property'),
                'floor':fields.integer('Floor', help='Number Of Floors'),
                'doc_name' : fields.char('Filename'),
                'nearby_ids':fields.one2many('nearby.property','property_id','Nearest Property'),
                'bedroom':fields.selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5+')],'Bedrooms'),
                'bathroom':fields.selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5+')],'Bathrooms'),
                'recurring_rule_type': fields.selection([
                                        ('monthly', 'Month(s)'),
                                        ], 'Recurrency', help="Invoice automatically repeat at specified interval"),
                'end_date': fields.date('End Date'),
                'no_of_towers':fields.integer('No Of Towers', help='Number Of Towers'),
                'no_of_property':fields.integer('Property Per Floors.', help='Number Of Properties Per Floor'),
                'video_url':fields.char('Video URL', help="//www.youtube.com/embed/mwuPTI8AT7M?rel=0"),
                'current_tenant':fields.many2one('tenant.partner','Current Tenant'),
                'customer_id':fields.many2one('res.partner', 'Customer'),
                'payment_term':fields.many2one('account.payment.term', 'Payment Terms'),
                'pur_instl_chck':fields.boolean('Purchase Installment Check'),
                'sale_instl_chck':fields.boolean('Sale Installment Check'),
                }

    _defaults = {
            'state':'draft',
            'color': 4,
            'code': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'property'),
            'recurring_rule_type':'monthly',
            'pur_instl_chck':False,
            'sale_instl_chck':False,
            'furnished':'none',
                 }

    def sqft_to_meter(self, cr, uid, ids, gfa_feet, context=None):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param context: A standard dictionary
        """
        res = {}
        if gfa_feet:
            res.update({'gfa_meter':float(gfa_feet / 10.7639104)})
        return{'value':res}

    def unit_price_calc(self, cr, uid, ids, unit_price, gfa_feet, context=None):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param context: A standard dictionary
        """
        res = {}
        if unit_price and gfa_feet:
            res.update({'total_price':float(unit_price * gfa_feet),
                        'purchase_value':float(unit_price * gfa_feet)
                        })
        if unit_price and not gfa_feet:
            raise osv.except_osv(('Error!'), ('Please Insert GFA(Sqft) Please'))
        return{'value':res}


    def edit_status(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param context: A standard dictionary
        """
        for rec in self.browse(cr, uid, ids, context=context):
            if not rec.property_manager:
                raise osv.except_osv(('Warning!'), ('Please Insert Owner Name'))
            if rec.state == 'draft':
                status = {'state': 'book'}
        return self.write(cr, uid, [rec.id], status, context=context)

    def edit_status_book(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param context: A standard dictionary
        """
        for rec in self.browse(cr, uid, ids, context=context):
            context.update({'result3':rec.id})
        return {'name': ('wizard'),
                'res_model': 'book.available',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'form',
                'view_type': 'form',
                'target':'new',
                'context':{'default_current_ids':context.get('result3')},
                }

    def open_url(self, cr, uid, ids, context=None):
        for property_brw in self.browse(cr, uid, ids):
#             address = property_brw.address_id
            if property_brw.street:
                address_path = (property_brw.street and (property_brw.street + ',') or ' ') + (property_brw.street2 and (property_brw.street2 + ',') or ' ') + (property_brw.city and (property_brw.city + ',') or ' ') + (property_brw.state_id.name and (property_brw.state_id.name + ',') or ' ') + (property_brw.country_id.name and (property_brw.country_id.name + ',') or ' ')
                rep_address = address_path.replace(' ', '+')
                URL = "http://maps.google.com/maps?f=d&hl=en&geocode=&q=%s&ie=UTF8&z=18" % (rep_address)
                webbrowser.open(URL)
            else:
                raise osv.except_osv(('No Address!'), ('No Address created for this Property!'))
        return True

    def button_normal(self, cr, uid, id, context=None):
        return self.write(cr, uid, id, {'state':'normal'})

    def button_sold(self, cr, uid, id, context=None):
        return self.write(cr, uid, id, {'state':'sold'})

    def button_close(self, cr, uid, id, context=None):
        return self.write(cr, uid, id, {'state':'close'})

    def button_cancel(self, cr, uid, id, context=None):
        return self.write(cr, uid, id, {'state':'cancel'})

    def button_draft(self, cr, uid, id, context=None):
        return self.write(cr, uid, id, {'state':'draft'})

    def parent_property_onchange(self, cr, uid, ids, parent_id, context=None):
        """
            This Method is used to set parent address
        """
        value = {}
        if parent_id:
            parent_data = self.browse(cr, uid, parent_id, context=context)
            street = parent_data.street
            street2 = parent_data.street2
            township = parent_data.township
            city = parent_data.city
            state_id = parent_data.state_id.id
            zip = parent_data.zip
            country_id = parent_data.country_id.id
            value.update({'street':street or '', 'street2':street2 or '',
                         'township':township or '', 'city':city or '' , 'state_id':state_id or False,
                         'zip':zip or '', 'country_id':country_id or ''})
        return { 'value' : value}


    def create_purchase_installment(self, cr, uid, ids, context=None):
        """
            used to create purchase installment information
        """
        year_create = []
        res = self.browse(cr, uid, ids, context=context)
        period = res['recurring_rule_type']
        starting_date = res['purchase_date']
        ending_date = res['end_date']
        amount = res['purchase_price']
        tot = res['purchase_price']
        if tot == 0.0:
            raise Warning(_('Please Enter Valid Purchase Price'))
        crncy_id = res.currency_id.id
        starting_date_date = datetime.strptime(starting_date, DEFAULT_SERVER_DATE_FORMAT)
        starting_day = datetime.strptime(starting_date,DEFAULT_SERVER_DATE_FORMAT).day
        if not ending_date:
            raise Warning(_('Please Select End Date'))
        ending_date_date = datetime.strptime(ending_date, DEFAULT_SERVER_DATE_FORMAT)
        ending_day = datetime.strptime(ending_date, DEFAULT_SERVER_DATE_FORMAT).day
        if ending_day > starting_day:
            raise Warning(_("Please Select End Date's day less than purchase date's day"))
#        method used to calculate difference in month between two dates
        def diff_month(d1, d2):
            return (d1.year - d2.year)*12 + d1.month - d2.month
        difference_month = diff_month(ending_date_date, starting_date_date)
        amnt = amount/difference_month
        rent_pool = self.pool.get('cost.cost')
        cr.execute("SELECT date FROM cost_cost WHERE purchase_property_id=%s" % ids[0])
        exist_dates = cr.fetchall()
        date_add = self.date_addition(starting_date, ending_date, period)
        exist_dates = map(lambda x:x[0], exist_dates)
        result = list(set(date_add) - set(exist_dates))
        result.sort(key=lambda item:item, reverse=False)
        ramnt = amnt
        remain_amnt = 0.0
        for dates in result:
            remain_amnt = amount - ramnt
            remain_amnt_per = (remain_amnt/tot)*100
            if remain_amnt < 0 :
                remain_amnt = remain_amnt * -1
            if remain_amnt_per < 0:
                remain_amnt_per = remain_amnt_per * -1
            year_create.append((0, 0, {
                     'currency_id': crncy_id or False,
                     'date':dates,
                     'purchase_property_id':ids[0],
                     'amount':amnt,
                     'remaining_amount':remain_amnt,
                     'rmn_amnt_per':remain_amnt_per,
                    }))
            amount = remain_amnt
        return self.write(cr, uid, ids,{'purchase_cost_ids':year_create,'pur_instl_chck':True})

    def date_addition(self, starting_date, end_date, period):
        date_list = []
        if period == 'monthly':
            while starting_date < end_date:
                date_list.append(starting_date)
                res = ((datetime.strptime(starting_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(months=1)).strftime(DEFAULT_SERVER_DATE_FORMAT))
                starting_date = res
            return date_list
        else:
            while starting_date < end_date:
                date_list.append(starting_date)
                res = ((datetime.strptime(starting_date, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(years=1)).strftime(DEFAULT_SERVER_DATE_FORMAT))
                starting_date = res
            return date_list

    def genrate_payment_enteries(self, cr, uid, id, context=None):
        data = self.browse(cr, uid, id, context=context)
        payment_term_id = data.payment_term.id
        value = data.sale_price
        amount = data.sale_price
        crncy_id = data.currency_id.id
        year_create = []
        date_ref = data.sale_date
        pterm_list = self.pool.get('account.payment.term').compute(cr, uid, payment_term_id, value, date_ref)
        if amount == 0.0:
            raise Warning(_('Please Enter Valid Sale Price'))
        rmnt = 0.0
        for line in pterm_list:
            lst = list(line)
            remain_amnt = amount-lst[1]
            remain_amnt_per = (remain_amnt/value)*100
            if remain_amnt < 0 :
                remain_amnt = remain_amnt * -1
            if remain_amnt_per < 0:
                remain_amnt_per = remain_amnt_per * -1
            year_create.append((0, 0, {
                     'currency_id': crncy_id or False,
                     'date':lst[0],
                     'sale_property_id':id,
                     'amount':lst[1],
                     'remaining_amount':remain_amnt,
                     'rmn_amnt_per':remain_amnt_per,
                    }))
            amount = amount - lst[1]
        self.write(cr, uid, id,{'sale_cost_ids':year_create,'sale_instl_chck':True})
        return True
    
#    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
#            res = super(account_asset_asset,self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
#            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#            date_server = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
#            property_lst = []
#            if context:
#                if context.get('active_model') == 'account.analytic.account':
#                    analytic_ids = self.pool.get('account.analytic.account').search(cr, uid, [('date_start','<=',date_server),('date','>=',date_server)], context=context)
#    
#                    if analytic_ids:
#                        for data in self.pool.get('account.analytic.account').browse(cr, uid, analytic_ids):
#                            if data.property_id.id:
#                                property_lst.append(data.property_id.id)
#                                if data.property_id.id in res:
#                                    res.remove(data.property_id.id)
#            return res
#
#    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
#        res = super(account_asset_asset, self).name_search(cr, user, name, args, operator=operator, context=context, limit=limit)
#        asset_ids = self.search(cr, user, [], context=context)
#        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#        date_server = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
#        property_lst = []
#        if context:
#            if context.get('active_model') == 'account.analytic.account':
#                return self.name_get(cr,user,asset_ids)
#        return res