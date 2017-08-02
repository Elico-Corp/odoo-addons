    # -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (c) 2010 Elico Corp. All Rights Reserved.
#    Author:            Eric CAUDAL <elicoidal@hotmail.com>
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

import time
import tools
from osv import fields, osv, orm
import os
import mx.DateTime
import base64
import pooler

SECTION_NAME = {
    'lead':'Prospects', 
    'opportunity':'Opportunities', 
                }

ICS_TAGS = {
        'summary':'Description', 
        'uid':'Calendar Code' , 
        'dtstart':'Date' , 
        'dtend':'Deadline' , 
        'url':'Partner Email' , 
        'description':'Your action', 
            }

class document_ics_purchasing_srm_wizard(osv.osv_memory):
    _name='document.ics.srm.wizard'
    _columns = {
        'name':fields.char('Name', size=64), 
        'lead' : fields.boolean('Prospect Supplier', help="Allows you to track and manage supplier prospects which are pre-sales requests or contacts, the very first contact with a supplier request."), 
        'opportunity' : fields.boolean('Purchasing Opportunities', help="Tracks identified purchasing business opportunities for your purchasing pipeline."), 
    }
    _defaults = {
        'lead': lambda *args: True, 
        'opportunity': lambda *args: True, 
    }
    
    def action_create(self, cr, uid, ids, context=None):
        data=self.read(cr, uid, ids, [])[0]
        dir_obj = self.pool.get('document.directory')
        dir_cont_obj = self.pool.get('document.directory.content')
        dir_id = dir_obj.search(cr, uid, [('name', '=', 'Calendars')])
        if dir_id:
            dir_id = dir_id[0]
        else:
            dir_id = dir_obj.create(cr, uid, {'name': 'Calendars' ,'user_id' : uid, 'type': 'directory'})
        for section in ['lead', 'opportunity']:
            if (not data[section]):
                continue
            else:
                section_id=self.pool.get('crm.case.section').search(cr, uid, [('name', '=', SECTION_NAME[section])])
                if not section_id:
                    continue
                else:                    
                    object_id=self.pool.get('ir.model').search(cr, uid, [('name', '=', 'Case')])[0]
                    
                    vals_cont={
                          'name': SECTION_NAME[section], 
                          'sequence': 1, 
                          'directory_id': dir_id, 
                          'suffix': section, 
                          'extension': '.ics', 
                          'ics_object_id': object_id, 
                          'ics_domain': [('section_id', '=', section_id[0])], 
                          'include_name' : False
                        } 
                    
                    content_id = dir_cont_obj.create(cr, uid, vals_cont)
                    
                    ics_obj=self.pool.get('document.directory.ics.fields')
                    for tag in ['description', 'url', 'summary', 'dtstart', 'dtend', 'uid']:
                        field_id =  self.pool.get('ir.model.fields').search(cr, uid, [('model_id.name', '=', 'Case'), ('field_description', '=', ICS_TAGS[tag])])[0]
                        vals_ics={ 
                                'field_id':  field_id , 
                                'name':  tag , 
                                'content_id': content_id , 
                                  }
                        ics_obj.create(cr, uid, vals_ics)

        return {
                'view_type': 'form', 
                "view_mode": 'form', 
                'res_model': 'ir.actions.configuration.wizard', 
                'type': 'ir.actions.act_window', 
                'target':'new', 
         }
    def action_cancel(self, cr, uid, ids, conect=None):
        return {
                'view_type': 'form', 
                "view_mode": 'form', 
                'res_model': 'ir.actions.configuration.wizard', 
                'type': 'ir.actions.act_window', 
                'target':'new', 
         }

document_ics_purchasing_srm_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
