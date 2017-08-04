# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

import time

from report import report_sxw
import pooler

class report_delivery_route_print(report_sxw.rml_parse):
    _name = 'report.delivery.route.print'
    
    def __init__(self, cr, uid, name, context):
        super(report_delivery_route_print, self).__init__(cr, uid, name, context)


report_sxw.report_sxw('delivery.route.print', 'delivery.route',
        'addons/fc_delivery_plan/report/delivery_route_print.mako', parser=report_delivery_route_print)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
