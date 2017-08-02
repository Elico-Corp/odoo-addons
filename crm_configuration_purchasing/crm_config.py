# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010 Eric CAUDAL. All Rights Reserved
#    $Id$
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import tools
from osv import fields, osv
import os
import pooler

class crm_cases(osv.osv):
    _name = "crm.case"
    _inherit = "crm.case"
    _columns = {
        'tags': fields.text('Tags', help='Enter here the tags for search'),
        'collected_material': fields.char('Collected Material', size=64,help='Material given by the supplier (catalogs, CD, DVD, samples).'),
        'fair_name': fields.char('Fair Name', size=64, help='Fair where the supplier was met.'),
        'website': fields.char('Website', size=64, help='Supplier Website.'),
    }
    _defaults = {
       'website': lambda *args: 'http://www',
    }

crm_cases()


class srm_menu_config_wizard(osv.osv_memory):
    _name = 'srm.menu.config_wizard'
    _columns = {
        'name': fields.char('Name', size=64),
        'lead_purchasing': fields.boolean('Leads (Purchases)', help="Allows you to track and manage leads which are pre-purchasings requests or contacts, the very first contact with a supplier's request."),
        'opportunity_purchasing': fields.boolean('Business Opportunities (Purchases)', help="Tracks identified business purchasing opportunities for your purchasing pipeline."),
        'document_ics': fields.boolean('Shared Calendar', help=" Will allow you to synchronise your Open ERP calendars with your phone, outlook, Sunbird, ical, ..."),
    }
    _defaults = {
        'opportunity_purchasing': lambda *args: True,
        'lead_purchasing': lambda *args: True,
    }

    def action_create(self, cr, uid, ids, context=None):
        module_proxy = self.pool.get('ir.module.module')
        modid = module_proxy.search(cr, uid, [('name', '=', 'crm_configuration_purchasing')])
        moddemo = module_proxy.browse(cr, uid, modid[0]).demo
        lst = ('data', 'menu')
        if moddemo:
            lst = ('data', 'menu', 'demo')
        res = self.read(cr, uid, ids)[0]
        idref = {}
        for section in ['lead_purchasing', 'opportunity_purchasing']:
            if (not res[section]):
                continue
            for fname in lst:
                file_name = 'crm_' + section + '_' + fname + '.xml'
                try:
                    fp = tools.file_open(os.path.join('crm_configuration_purchasing', file_name))
                except IOError, e:
                    fp = None
                if fp:
                    tools.convert_xml_import(cr, 'crm_configuration_purchasing', fp, idref, 'init', noupdate=True)
        cr.commit()
        modobj = self.pool.get('ir.module.module')
        modids = modobj.search(cr, uid, [('name', '=', 'crm_configuration_purchasing')])
        modobj.update_translations(cr, 1, modids, None)

        if res['document_ics']:
            ids = module_proxy.search(cr, uid, [('name', '=', 'document_ics_purchasing')])
            module_proxy.button_install(cr, uid, ids, context=context)
            cr.commit()
            db, pool = pooler.restart_pool(cr.dbname, update_module=True)

        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
         }

    def action_cancel(self, cr, uid, ids, context=None):
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
         }
srm_menu_config_wizard()
