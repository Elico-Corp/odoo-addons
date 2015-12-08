# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-Today Serpent Consulting Services PVT LTD
#    (<http://www.serpentcs.com>)
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
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
############################################################################
from openerp.osv import osv, fields
from openerp.tools.translate import _


class property_creation(osv.osv):
    _name = "property.created"
    _inherits = {'account.asset.asset': 'asset_id'}

    _columns = {
                'asset_id': fields.many2one('account.asset.asset', 'asset', required=True, ondelete='cascade'),
                'prefix2':fields.char('Prefix For Floor', help='Prefix or label For Floor.'),
                'prefix3':fields.selection([('1', 'ABCD'), ('2', '101'), ('3', '1001'), ('4', '10001')], 'Prefix For Property', help='Prefix Or Label For Property.'),
                'floor_number':fields.char('Floor no'),
                'tower_num':fields.char('Tower no'),
                'is_sub_property':fields.boolean('Sub Property', help='Select If your property Is Sub Property.'),
                'change_lable':fields.boolean('Change Label', help='Select If you wan\'t to change label.'),
                'prop_number':fields.char('property Number', help='property Number.'),
                'lable_bool':fields.boolean('Label Boolean'),
                'merge_prop1':fields.boolean('Label Boolean'),
                'parent_related':fields.related('asset_id', 'parent_id', type='many2one', relation='account.asset.asset', string='parent property'),
                'parent_property_rel':fields.related('parent_related', 'parent_id', type='many2one', relation='account.asset.asset', string='Parent Property' ),
                }

    _defaults = {'prefix2': '1', 'prefix3': '2', 'state': 'draft'}

    def create_property(self, cr, uid, ids, context=None):
        """
        This method create property.
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param context: A standard dictionary
        """
        property_rec = self.browse(cr, uid, ids[0], context=context)
        if property_rec.is_sub_property == True and property_rec.no_of_property == 0 or property_rec.floor == 0:
#            if property_rec.no_of_property == 0 or property_rec.floor == 0:
            raise osv.except_osv(('Warning!'), ('Property per floor and number of property should not be Zero'))
        tower_list = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        values = {'purchase_value': property_rec.purchase_value,
                  'category_id': property_rec.category_id.id,
                  'furnished': property_rec.furnished,
                  'parent_id': property_rec.asset_id.id,
                  'ground_rent': property_rec.ground_rent,
                  'floor': property_rec.floor,
                  'no_of_property': property_rec.no_of_property,
                  'state': 'draft',
                  'color': 4,
                  'lable_bool':True,
                  'is_sub_property': True,
                  'street': property_rec.street,
                  'street2': property_rec.street2,
                  'township': property_rec.township,
                  'city': property_rec.city,
                  'state_id': property_rec.state_id.id,
                  'country_id': property_rec.country_id.id,
                  'zip': property_rec.zip,
                  'image':property_rec.image
                  }
        if property_rec.prefix3 != '1':
            for floor_rec in range(1, int(property_rec.floor) + 1):
                for pro_rec in range(1, int(property_rec.no_of_property) + 1):
                    pre3 = str("%." + str(property_rec.prefix3) + "d")
                    values.update({'name': property_rec.name + "-" + str(floor_rec) + str(pre3 % pro_rec),
                                   'tower_num': property_rec.name,
                                   'prop_number': str(pre3 % pro_rec),
                                   'floor_number': floor_rec,
                                   })
                    self.create(cr, uid, values, context=context)
            self.write(cr, uid, ids, {'state': 'new_draft'}, context=context)
        if property_rec.prefix3 == '1':
            for floor_rec in range(1, int(property_rec.floor) + 1):
                counter = 0
                for pro_rec in range(1, int(property_rec.no_of_property) + 1):
                    values.update({'floor_number': floor_rec})
                    if counter < len(tower_list):
                        values.update({'name': property_rec.name + "-" + str(floor_rec) + tower_list[counter % len(tower_list)],
                                      'tower_num': property_rec.name,
                                      'prop_number': tower_list[counter % len(tower_list)],
                                        })
                    if counter >= len(tower_list):
                        values.update({'name': property_rec.name + "-" + str(floor_rec) + tower_list[counter % len(tower_list)] + str(counter / 26),
                                      'tower_num': property_rec.name,
                                      'prop_number': tower_list[counter % len(tower_list)] + str(counter / 26),
                                        })
                    self.create(cr, uid, values, context=context)
                    counter += 1
            self.write(cr, uid, ids, {'state': 'new_draft'}, context=context)
        return True

    def parent_prop_change(self, cr, uid, ids, parent_id, context=None):
        """
            This Method is used to set parent address
        """
        value = {}
        if parent_id:
            parent_data = self.pool.get('account.asset.asset').browse(cr, uid, parent_id, context=context)
            value.update({'street': parent_data.street or '',
                          'street2': parent_data.street2 or '',
                          'township': parent_data.township or '',
                          'city': parent_data.city or '',
                          'state_id' : parent_data.state_id.id or False,
                          'zip' : parent_data.zip or '',
                          'country_id' : parent_data.country_id.id or False,
                          'category_id':parent_data.category_id.id or False,
                          })
        return {'value': value}

    def property_unlink(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param context: A standard dictionary
        """
        property_rec = self.browse(cr, uid, ids[0], context=context).child_ids
        if property_rec.ids:
            self.pool.get('account.asset.asset').unlink(cr, uid , property_rec.ids, context=context)
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def unlink(self, cr, uid, ids, context=None):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param context: A standard dictionary
        @return: True/False.
        """
        for property_rec in self.browse(cr, uid, ids, context=context):
            unlink_ids = property_rec.child_ids.ids
            for rec in unlink_ids:
                acc_un_id = self.pool.get('account.asset.asset').search(cr, uid, [('parent_id', '=', rec)], context=context)
                if len(acc_un_id) != 0:
                    unlink_ids += acc_un_id
            unlink_ids.append(property_rec.asset_id.id)
            self.pool.get('account.asset.asset').unlink(cr, uid , unlink_ids, context=context)
        return super(property_creation, self).unlink(cr, uid , ids, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param vals: dictionary of new values to be set
        @param context: A standard dictionary
        @return: True/False.
        """
        super(property_creation, self).write(cr, uid, ids, vals, context=context)
        property_rec = self.browse(cr, uid, ids, context=context)
        write_ids = property_rec.child_ids.ids
        if write_ids:
            values = {'purchase_value': property_rec.purchase_value,
                      'category_id': property_rec.category_id.id,
                      'furnished': property_rec.furnished,
                      'ground_rent': property_rec.ground_rent,
                      }
            self.pool.get('account.asset.asset').write(cr, uid , write_ids, values, context=context)
        return True

    def edit_prop_wizzard(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param context: A standard dictionary
        """
        if context is None:
            context = {}
        floor = []
        tower = []
        property_id2 = self.browse(cr, uid, ids, context=context).asset_id.id
        prop_ids = self.search(cr, uid, [('parent_id', '=', property_id2)], context=context)
        for rec in self.browse(cr, uid, prop_ids, context=context):
            floor.append(str(rec.floor_number))
            tower.append(str(rec.tower_num))
        tower_list = list(set(tower))
        floor_list = list(set(floor))
        context.update({'result3': ids[0], 'result2': tower_list, 'result1':floor_list})
        return {'name': ('Filter Wizard'),
                'res_model': 'property.wizzard',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': {'default_property_id': context.get('result3'),
                           'default_floor_count': context.get('result1'),
                           'default_tower2': context.get('result2')},
                'nodestroy': True,
                }

    def split_property(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param context: A standard dictionary
        """
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state == 'cancel':
                prop_name = rec.name
                proplist = prop_name.split('->Merge->')
                if len(proplist) > 1:
                    status = {'state': 'draft','property_manager':False,
                              'name': str(proplist[0])
                              }
                    self.write(cr, uid, rec.id, status, context=context)
                    uncheck_ids = self.search(cr, uid, [('name', '=', _(str(proplist[1])))], context=context)
                    if len(uncheck_ids) != 0:
                        cur_id = self.browse(cr, uid, uncheck_ids, context=context)
                        newlabel = int(cur_id.label_id.name) - int(rec.label_id.name) 
                        self.write(cr, uid, uncheck_ids, {'label_id':newlabel}, context=context)
                else:
                    raise osv.except_osv(('Error!'), ('Please select Property which are Merged'))
        return True

    def merge_prop_wizzard(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param context: A standard dictionary
        """
        if context is None:
            context = {}
        property_id2 = self.browse(cr, uid, ids, context=context).asset_id.id
        context.update({'current_prop': ids[0]})
        return {'name': ('Merge Property'),
                'res_model': 'property.parent.merge.wizard',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': {'default_new_prop_id': context.get('current_prop')},
                'nodestroy': True,
                }


class property_label(osv.osv):
    _name = "property.label"

    def name_get(self, cr, uid, ids, context=None):
        """
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: list of ids for which name should be read
        @param context: context arguments, like lang, time zone
        @return: Returns a list of tupples containing id, name
        """
        res = []
        for rec in self.browse(cr, uid, ids, context=context):
            rec_str = ''
            if rec.name:
                rec_str += rec.name
            if rec.code:
                rec_str += rec.code
            res.append((rec.id, rec_str))
        return res

    def name_search(self, cr, uid, name='', args=[], operator='ilike', limit=100, context=None):
        args += ['|', ('name', operator, name), ('code', operator, name)]
        ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context=context)

    _columns = {
                'name': fields.char('Number of BHK', help='Number of BHK'),
                'code': fields.char('Code', help='Code For BHK'),
                }

    _defaults = {'code': 'BHK'}


class account_asset_asset(osv.osv):

    _inherit = 'account.asset.asset'

    def _total_property_available(self, cr, uid, ids, name, arg, context=None):
        """
        used to calculate total available Properties.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: list of ids for which name should be read
        @param context: context arguments, like lang, time zone
        @return: Returns a list of tupples containing id, name
        """
        res = {}
        tot = 0.0
        for property_brw in self.browse(cr, uid, ids,context=context):
            avail_ids = self.search(cr,uid,[('parent_id','=',property_brw.id),('state','=','draft')],context=context)
            if avail_ids:
                tot = len(avail_ids)
            res[property_brw.id] = tot
        return res

    def _total_property_booked(self, cr, uid, ids, name, arg, context=None):
        """
        used to calculate total Booked Properties.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: list of ids for which name should be read
        @param context: context arguments, like lang, time zone
        @return: Returns a list of tupples containing id, name
        """
        res = {}
        tot = 0.0
        for property_brw in self.browse(cr, uid, ids,context=context):
            booked_ids = self.search(cr,uid,[('parent_id','=',property_brw.id),('state','=','book')],context=context)
            if booked_ids:
                tot = len(booked_ids)
            res[property_brw.id] = tot
        return res

    _columns = {
                'label_id': fields.many2one('property.label', 'Label Name', help='Name Of Label For Ex. 1-BHK , 2-BHK etc.'),
                'Avalbl_property': fields.function(_total_property_available, method=True, type='float', string='Available',
                                                   help='It shows how many properties are available'),
                'book_property': fields.function(_total_property_booked, method=True, type='float', string='Book',
                                                   help='It shows how many properties are booked'),
                }

    def o2m_rec_ids(self, cr, uid, rec_ids, context=None):
        """ 
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param context: A standard dictionary
        """ 
        if context is None:
            context = {}
        prop_obj = self.pool.get('property.created')
        if rec_ids:
            for property_brw in self.browse(cr, uid, rec_ids, context=context):
                parentid = property_brw.parent_id.id
                par_ids = prop_obj.search(cr, uid, [('asset_id', '=', parentid)], context=context)
                prop_brw = prop_obj.browse(cr, uid, par_ids, context=context)
                if prop_brw.label_id.id:
                    values = {'label_id':prop_brw.label_id.id,
                              }
                    self.write(cr, uid , property_brw.id, values, context=context)
            super(account_asset_asset, self).o2m_rec_ids(cr, uid, rec_ids, context=context)
        return rec_ids
