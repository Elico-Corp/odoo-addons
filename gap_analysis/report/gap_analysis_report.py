# -*- encoding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


import time
from report import report_sxw
from osv import osv

class gap_analysis_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(gap_analysis_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })        
        
report_sxw.report_sxw('report.webkit_gap_analysis',
                       'gap_analysis', 
                       'gap_analysis/report/report_webkit_gap_analysis.mako',
                       parser=report_webkit_html)
