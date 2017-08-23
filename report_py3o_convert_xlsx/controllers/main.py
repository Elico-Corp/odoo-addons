# -*- coding: utf-8 -*-
# © 2017 Elico Corp (https://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import json
import os
import mimetypes

from odoo.http import route, request

from odoo.addons.report_py3o.controllers import main
from odoo.addons.web.controllers.main import (
    _serialize_exception,
    content_disposition
)
from odoo.tools import html_escape


class ReportController(main.ReportController):

    ODS_FILE_TYPE = 'spreadsheet'

    @route()
    def report_download(self, data, token):
        """This function is used by 'qwebactionmanager.js' in order to trigger
        the download of a py3o/controller report, and convert report from ods
        to xlsx with libreoffice

        :param data: a javascript array JSON.stringified containg report
        internal url ([0]) and type [1]
        :returns: Response with a filetoken cookie and an attachment header
        """
        response = super(ReportController, self).report_download(data, token)
        if self.ODS_FILE_TYPE in response.content_type:
            requestcontent = json.loads(data)
            url, type = requestcontent[0], requestcontent[1]
            if type != 'py3o':
                return super(ReportController, self).report_download(
                    data,
                    token
                )
            try:
                reportname = url.split('/report/py3o/')[1].split('?')[0]
                if '/' in reportname:
                    reportname, docids = reportname.split('/')
                with open(os.path.dirname(__file__) + '/' +
                          reportname + '.ods', 'a+') as create_ods:
                    create_ods.write(response.data)
                os.system(
                    "libreoffice --headless --convert-to xlsx --outdir '" +
                    os.path.dirname(
                        __file__) + "' '" + os.path.dirname(
                        __file__) + "/" + reportname + ".ods'")
                with open(os.path.dirname(__file__) + '/' +
                          reportname + '.xlsx', 'r+') as create_xlsx:
                    res = create_xlsx.read()
                os.remove(
                    os.path.dirname(__file__) + '/' + reportname + '.ods'
                )
                os.remove(
                    os.path.dirname(__file__) + '/' + reportname + '.xlsx'
                )
                ir_action = request.env['ir.actions.report.xml']
                action_py3o_report = ir_action.get_from_report_name(
                    reportname, "py3o").with_context(request.env.context)
                filename = action_py3o_report.gen_report_download_filename(
                    docids, data)
                filename_without_type = filename.split('.')[0]
                content_type = mimetypes.guess_type("x.xlsx")[0]
                http_headers = [
                    ('Content-Type',
                     content_type),
                    ('Content-Length',
                     len(res)),
                    ('Content-Disposition',
                     content_disposition(
                         filename_without_type +
                         '.xlsx'))]
                response = request.make_response(res, headers=http_headers)
                response.set_cookie('fileToken', token)
                return response
            except Exception as e:
                se = _serialize_exception(e)
                error = {
                    'code': 200,
                    'message': "Odoo Server Error",
                    'data': se
                }
                return request.make_response(html_escape(json.dumps(error)))
        else:
            return response
