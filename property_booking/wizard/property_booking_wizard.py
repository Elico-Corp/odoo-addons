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


class propert_Wizzard(osv.TransientModel):

    _name = "property.wizzard"

    def get_floor(self, cr, uid, context=None):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param context: A standard dictionary
        """
        if context is None:
            context = {}
        rec = []
        if context.get('default_floor_count', False):
            for i in range(1, len(context['default_floor_count']) + 1):
                res = (str(i), str(i))
                rec.append(res)
        return rec

    def get_tower(self, cr, uid, context=None):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param context: A standard dictionary
        """
        rec = []
        if 'default_tower2' in context:
            for i in context['default_tower2']:
                res = (str(i), str(i))
                rec.append(res)
        return rec

    _columns = {
                'property_created_ids': fields.many2many('property.created', 'rel_wizz_id', 'wizz_id', 'propert_id', string='Property Line'),
                'property_id': fields.many2one('property.created', 'Property'),
                'tower': fields.selection(get_tower, 'Tower', help='Prefix Or First Letter Of Tower.'),
                'tower2': fields.char('Prefix Of Tower'),
                'floor_count': fields.char('Number Of Floor', help='Number Of Tower.'),
                'floor': fields.selection(get_floor, 'Floor No.'),
                }

    def property_change(self, cr, uid, ids, property_id, context=None):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param context: A standard dictionary
        """
        res = {}
        rec = []
        if property_id:
            property_id2 = self.pool.get('property.created').browse(cr, uid, property_id, context=context).asset_id.id
            prop_ids = self.pool.get('property.created').search(cr, uid, [('parent_id', '=', property_id2)], context=context)
            rec.append((6, 0, prop_ids))
            res.update({'property_created_ids': rec})
        return {'value': res}

    def property_method(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param context: A standard dictionary
        """
        res = []
        property_rec = self.browse(cr, uid, ids[0], context=context)
        towerid = str(property_rec.tower)
        floorid = property_rec.floor
        subpro_ids = property_rec.property_created_ids
        if floorid:
            for rec in subpro_ids:
                old_name = rec.name
                bool1 = old_name.startswith(towerid)
                if int(rec.floor_number) == int(floorid) and bool1 == True and rec.state != 'cancel':
                    res.append(rec.id)
                context.update({'result3': res})
        return {'name': ('Property Wizard'),
                'res_model': 'sub.wizzard',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': {'default_property_created_ids2': context.get('result3')},
                'nodestroy': True,
                }


class property_parent_merge_wizard(osv.TransientModel):

    _name = "property.parent.merge.wizard"

    _columns = {
                'new_prop_id': fields.many2one('property.created', 'Property'),
                'property_created_ids1234': fields.many2many('property.created', 'rel_wizz_id2121', 'wizz_id2121', 'propert_id2121', string='Property Line123'),
                }

    def onchange_property(self,cr,uid,ids,new_prop_id,context=None):
        if context is None:
            context = {}
        property_obj = self.pool.get('property.created')
        if new_prop_id:
            for prop_merge_obj in property_obj.browse(cr,uid,new_prop_id,context=context):
                pareid = prop_merge_obj.asset_id.id
                res_obj = property_obj.search(cr,uid,[('parent_id','=',pareid)],context=context)
                return {'domain':{'property_created_ids1234':[('id','in',res_obj)]}}

    def property_merge_parent(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param context: A standard dictionary
        """
        if context is None:
            context = {}
        property_obj = self.pool.get('property.created')
        activeids = self.browse(cr,uid,ids,context=context).property_created_ids1234.ids
        if activeids:
            if len(activeids) <= 1:
                raise osv.except_osv(_('Warning!'), _("Please select atleast two properties."))
            data_prop = property_obj.read(cr, uid, activeids, ['state', 'parent_id', 'floor_number'], context=context)
            for x in data_prop:
                if x['parent_id'] == False:
                    raise osv.except_osv(_('Warning!'), _("Please select sub properties. \n Not parent property!."))
            states = [x['state'] for x in data_prop if x['state'] != 'draft']
            if states:
                raise osv.except_osv(_('Warning!'), _("Only Available state properties are allowed to be merged!"))
            parents = list(set([x['parent_id'][0] for x in data_prop]))
            if len(parents) != 1:
                raise osv.except_osv(_('Warning!'), _("Please select sub properties from the same Parent property!"))
            check_property = False
            maxm = 0
            prop_f_no = 0
            prop_p_no = False
            for prop in property_obj.browse(cr, uid, activeids, context=context):
                if not check_property:
                    check_property = prop
                    prop_f_no = int(prop.floor_number)
                    prop_p_no = str(prop.prop_number)
                    maxm = int(prop.label_id.name)
                    continue
                maxm += int(prop.label_id.name)
                vals = {'name': prop.name + "->" + "Merge" + "->" + check_property.name,
                        'state': 'cancel',
                        }
                floor_no = list(set([x['floor_number'][0] for x in data_prop]))
                if len(floor_no) != 1:
                    if int(prop.floor_number) in (prop_f_no + 1, prop_f_no - 1) and str(prop.prop_number) == prop_p_no:
                        property_obj.write(cr, uid, prop.id, vals, context=context)
                    else:
                        raise osv.except_osv(_('Warning!'), _("Please select sub properties from the same Floors!"))
                property_obj.write(cr, uid, prop.id, vals, context=context)
            requ_id = self.pool.get('property.label').search(cr, uid, [('name', '=', int(maxm))], context=context)
            if len(requ_id) != 1 and int(maxm) != 0:
                raise osv.except_osv(_('Warning!'), _('Please Create label of %s ' % (str(maxm) + " " + str(prop.label_id.code))))
            property_obj.write(cr, uid, check_property.id, {'label_id': maxm}, context=context)
        return {'type': 'ir.actions.act_window_close'}


class property_sub_wizard(osv.TransientModel):

    _name = "sub.wizzard"

    _columns = {
                'property_created_ids2': fields.many2many('property.created', 'rel_wizz_id21', 'wizz_id21', 'propert_id21', string='Property Line'),
                'name_obj': fields.char('New Name Of Property', help='New Name Of Property.'),
                'furnish': fields.selection([('none', 'None'),
                                             ('semi_furnished', 'Semi Furnished'),
                                             ('full_furnished', 'Full Furnished')], 'Furnishing', help='Furnishing.'),
                'is_other':fields.boolean('Is Shop', help='Check if it is other property.'),
                }

    _defaults = {'furnish': 'full_furnished'}

    def sub_method(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param context: A standard dictionary
        """
        if context is None:
            context = {}
        res = self.browse(cr, uid, ids, context=context)
        prop_ids = res.property_created_ids2
        label_change = False
        for rec in prop_ids:
            if res.is_other != True:
                label_change = rec.label_id.id
            old_name = rec.name
            new_name = old_name.replace(str(rec.tower_num), str(res.name_obj))
            stval = {'name': new_name,
                     'tower_num': res.name_obj,
                     'furnished': res.furnish,
                     'property_manager': rec.property_manager.id,
                     'state': rec.state,
                     'label_id': label_change,
                     }
            self.pool.get('property.created').write(cr, uid, rec.ids, stval, context=context)
        return True

