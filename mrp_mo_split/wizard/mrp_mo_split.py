# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2009 Albert Cervera i Areny - NaN  (http://www.nan-tic.com) All Rights Reserved.
#    Copyright (c) 2010-Today Elico Corp. All Rights Reserved.
#    Author: Andy Lu <andy.lu@elico-corp.com>
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

import wizard
import pooler
from tools.translate import _

_form = """<?xml version="1.0"?>
<form string="Split Wizard" col="2">
	<label string="This process will split selected production order into two." colspan="2"/>
	<label string="" colspan="2"/>
	<label string="Please specify the quantity you want to leave in the current production order." colspan="2"/>
    <field name="quantity"/>
</form>
"""


class mrp_mo_split(wizard.interface):
    def _split(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        id = data.get('id')
        if not id:
            raise wizard.except_wizard(_('Error !'), _('You must select at least one production order!'))
        quantity = data['form']['quantity']
        if not quantity or quantity <= 0:
            raise wizard.except_wizard(_('Error !'), _('You must specify a value greater than 0.'))
        productions = pool.get('mrp.production')._split(cr, uid, id, quantity, context)
        return {
            'domain': "[('id','in',%s)]" % productions,
            'name': _('Production Orders'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }

    states = {
        'init' : {
            'actions' : [],
            'result' : {
                'type' : 'form',
                'arch' : _form,
                'fields' : {'quantity': {'string': 'Quantity', 'type': 'float'} },
                'state' : [('end', 'Cancel', 'gtk-cancel'), ('split', 'Split', 'gtk-ok') ]
            }
        },
        'split' : {
            'actions' : [],
            'result' : {
                'type' : 'action',
                'action': _split,
                'state' : 'end'
            }
    },
    }
mrp_mo_split("mrp.mo.split")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
