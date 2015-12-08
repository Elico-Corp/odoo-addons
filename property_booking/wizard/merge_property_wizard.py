# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-Today Serpent Consulting Services Pvt. Ltd.
#    (<http://serpentcs.com>).
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
##############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _


class merge_property_wizard(osv.TransientModel):

    _name = 'merge.property.wizard'
    _description = 'Merge properties'


    def merge_property(self, cr, uid, ids, context=None):
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
        if context.get('active_ids', []):
            if len(context['active_ids']) <= 1:
                raise osv.except_osv(_('Warning!'), _("Please select atleast two properties."))
            data_prop = property_obj.read(cr, uid, context['active_ids'], ['state', 'parent_id', 'floor_number'], context=context)
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
            for prop in property_obj.browse(cr, uid, context['active_ids'], context=context):
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
