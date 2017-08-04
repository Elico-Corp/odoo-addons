# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)
from openerp.osv import orm


class event_company_def(orm.Model):

    _inherit = 'event.event'

    _defaults = {'company_id': ''}
