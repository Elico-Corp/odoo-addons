##############################################################################
#
# Copyright (c) 2008-2012 Alistek Ltd (http://www.alistek.com) All Rights Reserved.
#                    General contacts <info@alistek.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This module is GPLv3 or newer and incompatible
# with OpenERP SA "AGPL + Private Use License"!
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import wizard
import pooler
from tools.translate import _

def ir_set(cr, uid, key, key2, name, models, value, replace=True, isobject=False, meta=None):
    obj = pooler.get_pool(cr.dbname).get('ir.values')
    return obj.set(cr, uid, key, key2, name, models, value, replace, isobject, meta)

special_reports = [
    'printscreen.list'
]

class report_actions_wizard(wizard.interface):
    '''
    Add Print Button
    '''
    form = '''<?xml version="1.0"?>
    <form string="Add Print Button">
        <!--<field name="print_button"/>-->
        <field name="open_action"/>
    </form>'''

    exist_form = '''<?xml version="1.0"?>
    <form string="Add Print Button">
        <label string="Report Action already exist for this report."/>
    </form>'''

    exception_form = '''<?xml version="1.0"?>
    <form string="Add Print Button">
        <label string="Can not be create print button for the Special report."/>
    </form>'''

    done_form = '''<?xml version="1.0"?>
    <form string="Remove print button">
        <label string="The print button is successfully added"/>
    </form>'''

    fields = {
        'open_action': {'string': 'Open added action', 'type': 'boolean', 'default': False},
    }

    def _do_action(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        report = pool.get(data['model']).browse(cr, uid, data['id'], context=context)
        res = ir_set(cr, uid, 'action', 'client_print_multi', report.report_name, [report.model], 'ir.actions.report.xml,%d' % data['id'], isobject=True)
        if report.report_wizard:
            report._set_report_wizard()
        return {'value_id':res[0]}

    def _check(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        ir_values_obj = pool.get('ir.values')
        report = pool.get(data['model']).browse(cr, uid, data['id'], context=context)
        if report.report_name in special_reports:
            return 'exception'
        if report.report_wizard:
            act_win_obj = pool.get('ir.actions.act_window')
            act_win_ids = act_win_obj.search(cr, uid, [('res_model','=','aeroo.print_actions')], context=context)
            for act_win in act_win_obj.browse(cr, uid, act_win_ids, context=context):
                act_win_context = eval(act_win.context, {})
                if act_win_context.get('report_action_id')==report.id:
                    return 'exist'
            return 'add'
        else:
            ids = ir_values_obj.search(cr, uid, [('value','=',report.type+','+str(data['id']))])
            if not ids:
	            return 'add'
            else:
	            return 'exist'

    def _action_open_window(self, cr, uid, data, context):
        form=data['form']
        if not form['open_action']:
            return {}

        mod_obj = pooler.get_pool(cr.dbname).get('ir.model.data')
        act_obj = pooler.get_pool(cr.dbname).get('ir.actions.act_window')

        mod_id = mod_obj.search(cr, uid, [('name', '=', 'act_values_form_action')])[0]
        res_id = mod_obj.read(cr, uid, mod_id, ['res_id'])['res_id']
        act_win = act_obj.read(cr, uid, res_id, [])
        act_win['domain'] = [('id','=',form['value_id'])]
        act_win['name'] = _('Client Events')
        return act_win
    
    states = {
        'init': {
			'actions': [],
			'result': {'type':'choice','next_state':_check}
        },
        'add': {
            'actions': [],
            'result': {'type': 'form', 'arch': form, 'fields': fields, 'state': (('end', _('_Cancel')), ('process', _('_Ok')))},
        },
        'exist': {
            'actions': [],
            'result': {'type': 'form', 'arch': exist_form, 'fields': {}, 'state': (('end', _('_Close')),)},
        },
        'exception': {
            'actions': [],
            'result': {'type': 'form', 'arch': exception_form, 'fields': {}, 'state': (('end', _('_Close')),)},
        },
        'process': {
            'actions': [_do_action],
            'result': {'type': 'state', 'state': 'done'},
        },
        'done': {
            'actions': [],
            'result': {'type': 'form', 'arch': done_form, 'fields': {}, 'state': (('exit', _('_Close')),)},
        },
        'exit': {
            'actions': [],
            'result': {'type': 'action', 'action': _action_open_window, 'state': 'end'},
        },
    }
report_actions_wizard('aeroo.report_actions')

