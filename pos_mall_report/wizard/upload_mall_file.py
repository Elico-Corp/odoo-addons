# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import osv, fields
import base64


class upload_manual_mall_file(osv.osv_memory):
    _name = 'upload.manual.mall.file'
    _columns = {
        'report_file': fields.binary(string='Report File'),
        'report_file_fname': fields.char('Report Filename', size=128, required=True),
    }

    def change_mall_file(self, cr, uid, ids, context=None):
        report_obj = self.pool.get('pos.mall.report')
        if context is None:
            context = {}
        data = self.browse(cr, uid, ids, context=context)[0]
        report = report_obj.browse(cr, uid, context['active_id'], context=context)

        #save uploaded file on attachment/pos_report_report
        file_path = report.get_filename(context=context)
        upload_file = base64.decodestring(data.report_file)
        f = open(file_path, 'wb')
        f.write(upload_file)
        f.close()

        report_obj.write(
            cr, uid, [report.id],
            {'report_file': data.report_file, 'manual_report': True,
             'report_file_fname': data.report_file_fname, 'state': 'manual'},
            context=context)
        return {'type': 'ir.actions.act_window_close'}
