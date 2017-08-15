# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2013 Serpent Consulting Services PVT LTD (<http://www.serpentcs.com>)
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

# import wizard
import openerp.netsvc
import openerp.tools
import datetime
import urllib
from openerp.osv import fields, osv
from openerp.osv import orm, fields, osv
import webbrowser

class tenant_sms_send(orm.TransientModel):
    """ Create Menu """

    _name = "tenant.sms.send"
    _description = "Send SMS"

    _columns = {
        'user': fields.char('Login', size=256,required=True),
        'password': fields.char('Password', size=256,required=True)
    }
    def sms_send(self, cr, uid, ids, context):
        
        partner_pool = self.pool.get('tenancy.rent.schedule')
        active_ids = partner_pool.search(cr, uid, [('start_date' , '<', datetime.date.today().strftime('%Y-%m-%d')), ('paid' , '=', False)])
        partners = partner_pool.browse(cr, uid, active_ids, context)
        
        for partner in partners:
                if partner.rel_tenant_id.parent_id:
                    if partner.rel_tenant_id.parent_id[0].mobile:
                        for data in self.browse(cr, uid, ids, context) :
# bulksms API is used for messege sending
                            urllib.urlopen('''http://bulksms.vsms.net:5567/eapi/submission/send_sms/2/2.0?username=%s&password=%s&message=Hello Mr %s,\nYour rent QAR %d of %s is unpaid so kindly pay as soon as possible.\nRegards,\nProperty management firm.&msisdn=%s''' %(data.user,data.password,partner.rel_tenant_id.name, partner.amount,partner.start_date,partner.rel_tenant_id.parent_id[0].mobile))
                            
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: