# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-Today Serpent Consulting Services PVT LTD (<http://www.serpentcs.com>)
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
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from openerp import tools, api
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import webbrowser
from openerp.exceptions import except_orm, Warning, RedirectWarning


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    _columns = {
                'property_id': fields.many2one('account.asset.asset', 'Property'),
                'is_property':fields.boolean('Is Property'),
               }
    
class sale_order(osv.osv):
    _inherit = "sale.order"

    _columns = {
                'is_property':fields.boolean('Is Property'),
               }
    _defaults = {
        'is_property': False,
    }