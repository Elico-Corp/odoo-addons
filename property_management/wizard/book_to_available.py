# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>)
#    Copyright (C) 2004 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp.osv import orm, fields

class wizard_book_to_available(orm.TransientModel):
    _name = 'book.available'

    _columns={
        'current_ids' : fields.char('My ids'),
              }

    def print_yes(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param context: A standard dictionary
        """
        curr_id = self.browse(cr, uid, ids, context=context).current_ids
        curr_id1 = int(curr_id)
        asset_obj = self.pool.get('account.asset.asset')
        prop_obj = self.pool.get('property.created')
        for rec in asset_obj.browse(cr, uid, curr_id1, context=context):
            if rec.state in ('book','normal','close','sold'):
                status = {'state': 'draft','property_manager':False}
                asset_obj.write(cr, uid, [rec.id], status, context=context)
        return True


    def print_no(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of IDs
        @param context: A standard dictionary
        """
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: