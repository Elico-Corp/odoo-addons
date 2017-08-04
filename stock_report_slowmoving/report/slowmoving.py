# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


import time
import decimal_precision as dp
from report import report_sxw
import pooler

class Slowmove(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        res_user = pooler.get_pool(cr.dbname).get('res.users')
        self.context = context
        user = res_user.browse(cr, uid, uid)
        self.context.update({'lang':user.context_lang or 'en_US'})
        super(Slowmove, self).__init__(cr, uid, name, context=self.context)
        self.localcontext.update( {
            'time': time, 
            'dp': dp,
            'loginuser': user,
        })


report_sxw.report_sxw('report.stock.slowmove', 'stock.slowmove',
        'addons/stock_report_slowmoving/report/slowmoving_webkit.mako', parser=Slowmove)


