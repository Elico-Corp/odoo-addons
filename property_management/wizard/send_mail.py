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


import openerp.netsvc
import openerp.tools
from openerp.osv import fields, osv
from openerp.osv import orm, fields, osv
import re
import datetime

class partner_wizard_spam(orm.TransientModel):
    """ Mass Mailing """

    _name = "tenant.wizard.mail"
    _description = "Mass Mailing"

    def mass_mail_send(self, cr, uid, ids, context):
        partner_pool = self.pool.get('tenancy.rent.schedule')
        active_ids = partner_pool.search(cr, uid, [('start_date' , '<', datetime.date.today().strftime('%Y-%m-%d')), ('paid' , '=', False)])
        partners = partner_pool.browse(cr, uid, active_ids, context)
        
        for partner in partners:
                if partner.rel_tenant_id.parent_id:
                    if partner.rel_tenant_id.parent_id[0].email:
                        
                        to = '"%s" <%s>' % (partner.rel_tenant_id.name, partner.rel_tenant_id.parent_id[0].email)
        #TODO: add some tests to check for invalid email addresses
        #CHECKME: maybe we should use res.partner/email_send
                        tools.email_send(tools.config.get('email_from', False),
                                         [to],
                                         'Reminder for rent payment',
                                         '''
                                         Hello Mr %s,\n
                                         Your rent QAR %d of %s is unpaid so kindly pay as soon as possible.
                                         \n
                                         Regards,
                                         Administrator.
                                         Property management firm.
                                         ''' %(partner.rel_tenant_id.name, partner.amount,partner.start_date))
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
        