# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import werkzeug
from openerp import http
from openerp.http import request
import openerp.addons.website_sale.controllers.main
from openerp import http, SUPERUSER_ID
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.http import request, serialize_exception as _serialize_exception
from openerp import SUPERUSER_ID
PPG = 6

# QueryURL Class Call
class QueryURL(object):
    def __init__(self, path='', **args):
        self.path = path
        self.args = args

    def __call__(self, path=None, **kw):
        if not path:
            path = self.path
        for k,v in self.args.items():
            kw.setdefault(k,v)
        l = []
        for k,v in kw.items():
            if v:
                if isinstance(v, list) or isinstance(v, set):
                    l.append(werkzeug.url_encode([(k,i) for i in v]))
                else:
                    l.append(werkzeug.url_encode([(k,v)]))
        if l:
            path += '?' + '&'.join(l)
        return path

# Property List Display
class website_property(http.Controller):

    @http.route(['/agent_modal'], type='json', auth="public", website=True)
    def agent_modal(self, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        rec = pool['account.asset.asset'].browse(cr, SUPERUSER_ID, int(kwargs.get('property_id')), context=context)
        return request.website._render("website_pms.contact_agent_modal", {'property_rec': rec})

    @http.route(['/demand_modal'], type='json', auth="public", website=True)
    def demand_modal(self, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        country_value = []
        property_type_values = []
        state_value = []
        country_obj = pool['res.country']
        state_obj = pool['res.country.state']
        type_obj = pool['property.type']
        country_ids = country_obj.search(cr, SUPERUSER_ID, [], context = context)
        state_ids = state_obj.search(cr, SUPERUSER_ID, [], context = context)
        type_ids = type_obj.search(cr, SUPERUSER_ID, [], context = context)
        for country_rec in country_obj.browse(cr, SUPERUSER_ID, country_ids, context = context):
            country_value.append(country_rec)
        for state_rec in state_obj.browse(cr, SUPERUSER_ID, state_ids, context = context):
            state_value.append(state_rec)
        for type_rec in type_obj.browse(cr, SUPERUSER_ID, type_ids, context = context):
            property_type_values.append(type_rec)
        return request.website._render("website_pms.demand_modal", { 'country_names':country_value , 'state_names': state_value, 'property_types':property_type_values})

    @http.route(['/fav_agent_modal'], type='json', auth="public", website=True)
    def fav_agent_modal(self, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        rec = pool['account.asset.asset'].browse(cr, SUPERUSER_ID, int(kwargs.get('property_id')), context=context)
        return request.website._render("website_pms.contact_agent_modal_id", {'property_rec': rec})

    # common method call 
    def browse_property(self, property_ids = []):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        property_values = []
        property_obj = pool['account.asset.asset']
        for property_rec in property_obj.browse(cr, SUPERUSER_ID, property_ids, context=context):
            property_values.append(property_rec)
            dta = property_rec.create_date
            start_date = datetime.strptime(dta, '%Y-%m-%d %H:%M:%S')
            end_date = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
#             added_time = (end_date - start_date).days * 24 * 60
#             print "added_time..............",added_time
        return property_values

    @http.route(['/property_list','/property_list/page/<int:page>'], type='http', auth="public", website=True)
    def property_list(self, page = 0, category = None, order = None,search = '', **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        domain=[]
        values = {}
        property_values = []
        property_obj = pool['account.asset.asset']
        if post.get('search'):
            domain = [('name','ilike',post.get('search'))]

        values.update({'type_of_property': post.get('type_of_property')})
        if post.get('type_of_property') == 'sale':
            dropdown_price = post.get('dropdown_price')
            if dropdown_price =='lowest':
                order = 'sale_price asc'
                values.update({'dropdown_price': 'lowest'})
            elif dropdown_price =='highest':
                order = 'sale_price desc'
                values.update({'dropdown_price': 'highest'})
            elif dropdown_price =='newest':
                order = 'create_date desc'
                values.update({'dropdown_price': 'newest'})
            elif dropdown_price =='all':
                order = None
                values.update({'dropdown_price': 'all'})

        if post.get('type_of_property') == 'rent':
            dropdown_price = post.get('dropdown_price')
            if dropdown_price =='lowest':
                order = 'ground_rent asc'
                values.update({'dropdown_price': 'lowest'})
            elif dropdown_price =='highest':
                order = 'ground_rent desc'
                values.update({'dropdown_price': 'highest'})
            elif dropdown_price =='newest':
                order = 'create_date desc'
                values.update({'dropdown_price': 'newest'})
            elif dropdown_price =='all':
                order = None
                values.update({'dropdown_price': 'all'})

        dropdown_furnished = post.get('dropdown_furnish')
        if dropdown_furnished =='full_furnished':
            domain += [('furnished', '=', 'full_furnished')]
            values.update({'dropdown_furnish': 'full_furnished'})
        elif dropdown_furnished =='semi_furnished':
            domain += [('furnished', '=', 'semi_furnished')]
            values.update({'dropdown_furnish': 'semi_furnished'})
        elif dropdown_furnished =='none':
            domain += [('furnished', '=', 'none')]
            values.update({'dropdown_furnish': 'none'})
        elif dropdown_furnished =='all':
            values.update({'dropdown_furnish': 'all'})

        dropdown_facing = post.get('dropdown_facing')
        if dropdown_facing =='east':
            domain += [('facing', '=', 'east')]
            values.update({'dropdown_facing': 'east'})
        elif dropdown_facing =='west':
            domain += [('facing', '=', 'west')]
            values.update({'dropdown_facing': 'west'})
        elif dropdown_facing =='north':
            domain += [('facing', '=', 'north')]
            values.update({'dropdown_facing': 'north'})
        elif dropdown_facing =='south':
            domain += [('facing', '=', 'south')]
            values.update({'dropdown_facing': 'south'})
        elif dropdown_facing =='all':
            values.update({'dropdown_facing': 'all'})

        # bedroom slider domain        
        values.update({'min_bead': 1,'max_bead': 5})
        if post.get('min_bead') and post.get('max_bead'):
            values.update({'min_bead': post.get('min_bead'),'max_bead': post.get('max_bead')})
            domain += [('bedroom','>=',post.get('min_bead')),('bedroom','<=',post.get('max_bead'))]

        #bathroom slider domain
        values.update({'min_bath': 1,'max_bath': 5})
        if post.get('min_bath') and post.get('max_bath'):
            values.update({'min_bath': post.get('min_bath'),'max_bath': post.get('max_bath')})
            domain += [('bathroom','>=',post.get('min_bath')),('bathroom','<=',post.get('max_bath'))]

        # new search domain
        values.update({'postcode': post.get('postcode')})
        if post.get('postcode'):
            domain += [('zip','like',post.get('postcode'))]
        values.update({'area': post.get('area')})
        if post.get('area'):
            domain += [('street','like',post.get('area'))]
        values.update({'city': post.get('city')})
        if post.get('city'):
            domain += [('city','like',post.get('city'))]

        values.update({'min_range': post.get('min_range'),'max_range': post.get('max_range')});
        if post.get('type_of_property') == 'rent':
            domain += [('state','=','normal')]
            if post.get('min_range') and post.get('min_range'):
                domain += [('ground_rent','>=',post.get('min_range')),('ground_rent','<=',post.get('max_range'))]
        if post.get('type_of_property') == 'sale':
            domain += [('state','=','close')]
            if post.get('min_range') and post.get('max_range'):
                domain += [('sale_price','>=',post.get('min_range')),('sale_price','<=',post.get('max_range'))]

        keep = QueryURL('/selected_property', property_id=[])
        url = "/property_list"
        pager = request.website.pager(url = url, total = len(property_obj.search(cr, SUPERUSER_ID, domain, order=order)), page = page, step = PPG, scope = 7, url_args = post)
        property_ids = property_obj.search(cr, SUPERUSER_ID, domain, limit=PPG, offset=pager['offset'], order=order,context=context)
        property_values = self.browse_property(property_ids)
        keep = QueryURL('/selected_property', property_id = [])
        user = pool['res.users'].browse(cr, SUPERUSER_ID, request.uid, context=context)
        assets_list=[]
        for asset_id in user.partner_id.fav_assets_ids:
                assets_list.append(asset_id.id)
        values.update({
            'fav_assets_list':assets_list,
            'property_rec': property_values,
            'keep': keep,
            'pager': pager,
        })
        if post.get('search'):
            values.update({'search':post.get('search')})
        return request.website.render("website_pms.property_extended", values)

    # Get selected id when click in property images 
    @http.route(['/selected_property'], type='http', auth="public", website=True)
    def selected_property(self, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        property_obj = pool['account.asset.asset']
        propertys = property_obj.browse(cr, SUPERUSER_ID, int(post.get('id')), context=context)
        property_ids = property_obj.search(cr, SUPERUSER_ID, [], context=context)
        property_values = self.browse_property(property_ids)
        keep = QueryURL('/selected_property', property_id = [])
        user = pool['res.users'].browse(cr, SUPERUSER_ID, request.uid, context=context)
        assets_list=[]
        for asset_id in user.partner_id.fav_assets_ids:
                assets_list.append(asset_id.id)
        return request.website.render("website_pms.property_list_view", {'fav_assets_list':assets_list, 'propertys': propertys, 'keep': keep, 'property_rec': property_values})

class website_register (http.Controller):
    _name = 'website.register'

    @http.route('/user_create', type='http', auth="public", website=True)
    def user_create(self, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        res_user_obj = pool['res.users']
        email = kwargs.get('email')
        user_id = False
        user_id = res_user_obj.search(cr, SUPERUSER_ID, [('login', '=', email)], context=context)
        if user_id:
            return request.website.render('website_pms.user_registration',{'error': "User with same email address already exists."})
        vals = {
                'name': kwargs.get('name'),
                'phone':kwargs.get('phone'),
                'login': email,
                'password':kwargs.get('password'),
                'country_id':kwargs.get('Country'),
                'state_id':kwargs.get('State'),
                'street':kwargs.get('Street'),
                'city':kwargs.get('City'),
                'customer':True,
                }
        user_id = res_user_obj.create(cr, SUPERUSER_ID, vals, context=context)
        user_rec = res_user_obj.browse(cr,SUPERUSER_ID, user_id, context= context)
        request.session['p_id'] = user_rec.partner_id.id
        url = "/login?db=%s&login=%s&key=%s&redirect=/web/login" % (request.session.db, kwargs.get('email'), kwargs.get('password'))
        return request.redirect(url)

    @http.route(['/get_country'],type='json',auth='public',website=True)
    def get_country(self):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        country_list = []
        country_obj = pool['res.country']
        country_ids = country_obj.search(cr, SUPERUSER_ID, [], context = context)
        country_ids = country_obj.browse(cr, SUPERUSER_ID, country_ids, context = context)
        for country_rec in country_ids:
            country_list.append((country_rec.id, country_rec.name))
        return country_list

    @http.route(['/get_state'],type='json',auth='public',website=True)
    def get_state(self):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        state_list = []
        state_obj = pool['res.country.state']
        state_ids = state_obj.search(cr, SUPERUSER_ID, [], context = context)
        state_ids = state_obj.browse(cr, SUPERUSER_ID, state_ids, context = context)
        for state_rec in state_ids:
            state_list.append((state_rec.id, state_rec.name))
        return state_list

    @http.route(['/min_max_price'],type='json',auth='public',website=True)
    def min_max_price(self):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        asset_obj = pool["account.asset.asset"]
        cr.execute("SELECT MIN(ground_rent) as min_rent, MIN(sale_price) as min_sale, MAX(ground_rent) as max_rent, MAX(sale_price) as max_sale FROM account_asset_asset")
        value = cr.dictfetchall()[0]
        price = {
            'min_value' : min(value.get('min_rent'), value.get('min_sale')),
            'max_value' : max(value.get('max_rent'), value.get('max_sale')),
        }
        return price

    @http.route(['/create_lead'], type="json", auth='public', methods=['POST'], website=True)
    def create_lead(self, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        crm_lead_obj = pool['crm.lead']
        property_obj = pool['account.asset.asset']
        inquiry = ' '
        if kwargs.get('asset'):
            property = property_obj.browse(cr, SUPERUSER_ID, int(kwargs.get('asset')), context=context)
            val = ''
            if str(property.state) == 'draft':
                val = 'Available'
            elif str(property.state) == 'normal':
                val = 'On Lease'
            elif str(property.state) == 'close':
                val = 'Sale'
            elif str(property.state) == 'sold':
                val = 'Sold'
            inquiry = 'Inquiry of ' + str(property.name) + ' for ' + val
        data = {
            'name':inquiry or ' ',
            'contact_name': str(kwargs.get('firstname')) + ' ' + str(kwargs.get('surname')),
            'email_from' : kwargs.get('email'),
            'phone' : kwargs.get('tel'),
            'phone_type' : kwargs.get('telType'),
            'when_to_call' : kwargs.get('telTime'),
            'description' : kwargs.get('msg'),
            'property_id' : kwargs.get('asset'),
        }
        if val == 'On Lease':
            data.update({'is_rent':True})
            
        if val == 'Sale':
            data.update({'is_buy':True})
        lead_id = crm_lead_obj.create(cr, SUPERUSER_ID, data, context=context)
        return lead_id

    @http.route(['/create_lead_demand'], type="json", auth='public', methods=['POST'], website=True)
    def create_lead_demand(self, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        crm_lead_obj = pool['crm.lead']
        inquiry = ' '
        data = {
            'name':inquiry or ' ',
            'contact_name': str(kwargs.get('firstname')) + ' ' + str(kwargs.get('surname')),
            'email_from' : kwargs.get('email'),
            'phone' : kwargs.get('tel'),
            'phone_type' : kwargs.get('telType'),
            'when_to_call' : kwargs.get('telTime'),
            'description' : kwargs.get('msg'),
            'demand' : True,
            'street':kwargs.get('street'),
            'street2':kwargs.get('street2'),
            'city':kwargs.get('city'),
            'zip':kwargs.get('zip'),
            'furnished':kwargs.get('furnished'),
            'facing':kwargs.get('facing'),
            'min_bathroom':int(kwargs.get('min_bathroom')),
            'max_bathroom':int(kwargs.get('max_bathroom')),
            'min_bedroom':int(kwargs.get('min_bedroom')),
            'max_bedroom':int(kwargs.get('max_bedroom')),
            'type_id':int(kwargs.get('type_id')),
            'priority':str(4),
        }
        if kwargs.get('min_price') == "0" or kwargs.get('min_price') == "":
            data.update({'min_price':0.0})
        else:
            data.update({'min_price':int(kwargs.get('min_price'))})
        if kwargs.get('max_price') == "0" or kwargs.get('min_price') == "":
            data.update({'max_price':0.0})
        else:
            data.update({'max_price':int(kwargs.get('max_price'))})
        if kwargs.get('state') == "Select State":
            data.update({'state_id':False})
        else:
            data.update({'state_id':int(kwargs.get('state'))})
        if kwargs.get('country') == "Select Country":
            data.update({'country_id':False})
        else:
            data.update({'country_id':int(kwargs.get('country'))})
            
        lead_id = crm_lead_obj.create(cr, SUPERUSER_ID, data, context=context)
        return lead_id


    @http.route(['/change_fav_property'], type='json', auth="public", website=True)
    def change_fav_property(self, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        partner_dic = {}
        user_obj = pool['res.users']
        partner_obj = pool['res.partner']
        user = user_obj.browse(cr, SUPERUSER_ID, request.uid, context=context)
        for partner in user:
            partner_id = partner.partner_id.id
        if post.get('fav_property'):
            property = pool['account.asset.asset'].browse(cr, SUPERUSER_ID, post.get('fav_property'), context=context)
            if post.get('fav_checked'):
                selected_property = partner_obj.write(cr, SUPERUSER_ID, partner_id, {'fav_assets_ids': [(4, property.id)]}, context=context)
            else:
                deleted_property = partner_obj.write(cr, SUPERUSER_ID, partner_id, {'fav_assets_ids': [(3, property.id)]}, context=context)
        partner_dic = partner_obj.read(cr, SUPERUSER_ID, partner_id, ['fav_assets_ids'], context=context)
        return {'fav_assets':len(partner_dic.get('fav_assets_ids')) or 0}

    @http.route(['/page/homepage'], type = 'http', auth = 'public', website = True)
    def homepage_counter(self, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        property_rec = pool['account.asset.asset'].search(cr, SUPERUSER_ID, [], context = context)
        return request.website.render('website.homepage',{'total_prop':len(property_rec)})

    @http.route(['/page/website_pms.favourite_property'], type = "http", auth = 'public', website = True)
    def favourite_property(self,**kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        user = pool['res.users'].browse(cr, SUPERUSER_ID, request.uid, context=context)
        fav_assets_list=[]
        for asset_id in user.partner_id.fav_assets_ids:
                fav_assets_list.append(asset_id.id)
        keep = QueryURL('/selected_property', property_id=[])
        data={
          'fav_property_rec': pool['account.asset.asset'].browse(cr, SUPERUSER_ID, fav_assets_list, context=context),
          'fav_assets_list':fav_assets_list,
          'keep': keep,
              }
        return request.website.render('website_pms.favourite_property', data)

#     @http.route(['/page/homepage'], type = 'http', auth = 'public', website = True)
#     def homepage_popup(self, **kwargs):
#         cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
#         website_settings_obj = pool['website.setting']
#         website_settings_ids = website_settings_obj.search(cr, uid, [],context=context)
#         data = {
#                 'media': website_settings_obj.browse(cr, uid, website_settings_ids, context = context)
#         }
#         return request.website.render('website.homepage',data)

# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4: