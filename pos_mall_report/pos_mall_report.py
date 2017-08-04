# -*- coding: utf-8 -*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import fields, osv, orm
import base64
import csv
from datetime import datetime
from dateutil import tz
import time
import ftplib
import os
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval
import codecs
import openerp.addons.decimal_precision as dp


class pos_mall_report_config(orm.Model):
    _name = 'pos.mall.report.config'
    _description = 'Configuration of mall Report'

    def _get_csv_delimiter(self, cr, uid, context=None):
        return [('\t', 'Tab'), (';', ';'), (',', ',')]

    def _get_csv_quotechar(self, cr, uid, context=None):
        return [('"', '"'), ('|', '|')]

    def _get_file_encoding(self, cr, uid, context=None):
        return [
            ('ascii', 'ascii'),
            ('big5', 'big5'),
            ('big5hkscs', 'big5hkscs'),
            ('cp037', 'cp037'),
            ('cp424', 'cp424'),
            ('cp437', 'cp437'),
            ('cp500', 'cp500'),
            ('cp720', 'cp720'),
            ('cp737', 'cp737'),
            ('cp775', 'cp775'),
            ('cp850', 'cp850'),
            ('cp852', 'cp852'),
            ('cp855', 'cp855'),
            ('cp856', 'cp856'),
            ('cp857', 'cp857'),
            ('cp858', 'cp858'),
            ('cp860', 'cp860'),
            ('cp861', 'cp861'),
            ('cp862', 'cp862'),
            ('cp863', 'cp863'),
            ('cp864', 'cp864'),
            ('cp865', 'cp865'),
            ('cp866', 'cp866'),
            ('cp869', 'cp869'),
            ('cp874', 'cp874'),
            ('cp875', 'cp875'),
            ('cp932', 'cp932'),
            ('cp949', 'cp949'),
            ('cp950', 'cp950'),
            ('cp1006', 'cp1006'),
            ('cp1026', 'cp1026'),
            ('cp1140', 'cp1140'),
            ('cp1250', 'cp1250'),
            ('cp1251', 'cp1251'),
            ('cp1252', 'cp1252'),
            ('cp1253', 'cp1253'),
            ('cp1254', 'cp1254'),
            ('cp1255', 'cp1255'),
            ('cp1256', 'cp1256'),
            ('cp1257', 'cp1257'),
            ('cp1258', 'cp1258'),
            ('euc_jp', 'euc_jp'),
            ('euc_jis_2004', 'euc_jis_2004'),
            ('euc_jisx0213', 'euc_jisx0213'),
            ('euc_kr', 'euc_kr'),
            ('gb2312', 'gb2312'),
            ('gbk', 'gbk'),
            ('gb18030', 'gb18030'),
            ('hz', 'hz'),
            ('iso2022_jp', 'iso2022_jp'),
            ('iso2022_jp_1', 'iso2022_jp_1'),
            ('iso2022_jp_2', 'iso2022_jp_2'),
            ('iso2022_jp_2004', 'iso2022_jp_2004'),
            ('iso2022_jp_3', 'iso2022_jp_3'),
            ('iso2022_jp_ext', 'iso2022_jp_ext'),
            ('iso2022_kr', 'iso2022_kr'),
            ('latin_1', 'latin_1'),
            ('iso8859_2', 'iso8859_2'),
            ('iso8859_3', 'iso8859_3'),
            ('iso8859_4', 'iso8859_4'),
            ('iso8859_5', 'iso8859_5'),
            ('iso8859_6', 'iso8859_6'),
            ('iso8859_7', 'iso8859_7'),
            ('iso8859_8', 'iso8859_8'),
            ('iso8859_9', 'iso8859_9'),
            ('iso8859_10', 'iso8859_10'),
            ('iso8859_13', 'iso8859_13'),
            ('iso8859_14', 'iso8859_14'),
            ('iso8859_15', 'iso8859_15'),
            ('iso8859_16', 'iso8859_16'),
            ('johab', 'johab'),
            ('koi8_r', 'koi8_r'),
            ('koi8_u', 'koi8_u'),
            ('mac_cyrillic', 'mac_cyrillic'),
            ('mac_greek', 'mac_greek'),
            ('mac_iceland', 'mac_iceland'),
            ('mac_latin2', 'mac_latin2'),
            ('mac_roman', 'mac_roman'),
            ('mac_turkish', 'mac_turkish'),
            ('ptcp154', 'ptcp154'),
            ('shift_jis', 'shift_jis'),
            ('shift_jis_2004', 'shift_jis_2004'),
            ('shift_jisx0213', 'shift_jisx0213'),
            ('utf_32', 'utf_32'),
            ('utf_32_be', 'utf_32_be'),
            ('utf_32_le', 'utf_32_le'),
            ('utf_16', 'utf_16'),
            ('utf_16_be', 'utf_16_be'),
            ('utf_16_le', 'utf_16_le'),
            ('utf_7', 'utf_7'),
            ('utf_8', 'utf_8'),
            ('utf_8_si', 'utf_8_si')
        ]

    def _get_code(self, cr, uid, ids, name, args, context=None):
        res = {}
        for config in self.browse(cr, uid, ids, context=context):
            res[config.id] = config.name.strip().replace(' ', '-')
        return res

    _columns = {
        'name': fields.char('Name', required=True),
        'code': fields.function(
            _get_code,
            type='char',
            method=True,
            string='Code',
            store=True),
        'saving_path': fields.char('Saving Path', required=True),
        'ftp_server': fields.char('FTP Server', size=64),
        'ftp_user': fields.char('FTP User', size=64),
        'ftp_password': fields.char('FTP Password', size=64),
        'active': fields.boolean('Active'),
        'cron': fields.boolean(
            'Cron',
            help="check to indicate cron job will use this configuration to generate report."),
        'pos_config_id': fields.many2one('pos.config', 'Point of Sale', required=True),
        'payment_method_ids': fields.one2many(
            'pos.mall.report.payment.method',
            'config_id', string="Payment Methods"
        ),
        'tmpl_lines': fields.one2many(
            'pos.mall.report.template.line',
            'config_id',
            'Template Lines',
            required=True
        ),
        'csv_delimiter': fields.selection(_get_csv_delimiter, 'Separated by', required=True),
        'csv_quotechar': fields.selection(_get_csv_quotechar, 'Text delimiter', required=True),
        'filename': fields.char('Filename'),
        'file_extension': fields.char('File extension'),
        'file_encoding': fields.selection(_get_file_encoding, string="File encoding", required=True)
    }

    _defaults = {
        'active': True,
        'csv_delimiter': u'\t',
        'csv_quotechar': u'"',
        'file_encoding': 'utf-8'
    }


class pos_mall_report(orm.Model):
    _name = 'pos.mall.report'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Mall Report'

    def get_filename(self, cr, uid, ids, context=None):
        if isinstance(ids, list):
            ids = ids[0]
        report = self.browse(cr, uid, ids, context=context)
        config = report.config_id
        filename = (config.filename if config.filename else report.name)
        file_extension = config.file_extension if config.file_extension else ''
        path = os.path.join(config.saving_path, filename + file_extension)
        return path

    def _get_file_short_fname(self, cr, uid, ids, name, args, context=None):
        res = {}
        for report in self.browse(cr, uid, ids, context=context):
            if not report.report_file_fname:
                res[report.id] = None
                continue
            res[report.id] = report.report_file_fname.rpartition('/')[-1]
        return res

    _columns = {
        'name': fields.char(
            'Name', readonly=True, size=128),
        'date': fields.date('Date', readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('report', 'Report'),
            ('error', 'Error'),
            ('manual', 'Manual'),
            ('transferred', 'Transferred'),
        ], 'Status', track_visibility='onchange'),
        'manual_report': fields.boolean(
            'Manual Report', readonly=True, states={'draft': [('readonly', False)]},
            help='Indicating if the report should not be generated automatically'),
        'line_ids': fields.one2many(
            'pos.mall.report.line', 'mall_id', 'Mall Lines', readonly=True,
            states={'draft': [('readonly', False)]}),
        'config_id': fields.many2one(
            'pos.mall.report.config', 'Mall Config', readonly=True,
            states={'draft': [('readonly', False)]}),
        'report_file': fields.binary(string='Report File', readonly="1"),
        'report_file_fname': fields.char(
            'Report Filename', size=128, readonly=True,
            states={'draft': [('readonly', False)]}),
        'report_file_short_fname': fields.function(
            _get_file_short_fname,
            type='char',
            method=True,
            string='Short Filename',
            store=False),
    }

    _defaults = {
        'state': 'draft',
        'report_file_fname': lambda *a: '',
        'name': lambda obj, cr, uid, context: '/',
        'date': lambda obj, cr, uid, context: fields.date.context_today(
            obj, cr, uid, context=context)
    }

    def _get_name(self, cr, uid, vals, context=None):
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'pos.mall.report') or '/'
            if 'config_id' in vals:
                config = self.pool.get('pos.mall.report.config').browse(
                    cr, uid, vals['config_id'], context=context)
                vals['name'] = config.code + vals['name']
        return vals['name']

    def create(self, cr, uid, vals, context=None):
        vals['name'] = self._get_name(cr, uid, vals, context=context)
        return super(pos_mall_report, self).create(cr, uid, vals, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        report = self.browse(cr, uid, id, context=context)
        vals = {'config_id': report.config_id.id}
        default.update({
            'date': fields.date.context_today(self, cr, uid, context=context),
            'name': self._get_name(cr, uid, vals, context=context),
        })
        return super(pos_mall_report, self).copy(cr, uid, id, default, context=context)

    def _generate_mall_text_file(self, cr, uid, ids, context=None):
        def _generate_details(tmpl_lines, line, encoding):
            details = []
            for tmpl_line in tmpl_lines:
                val = tmpl_line.compute_line(line)
                details.append(val)
            return details

        report_detail = []
        for order in self.browse(cr, uid, ids, context=context):
            config = order.config_id
            for line in order.line_ids:
                detail = _generate_details(config.tmpl_lines, line, config.file_encoding)
                report_detail.append(detail)
        if not os.path.isdir(config.saving_path):
            os.mkdir(config.saving_path)
        filename = order.get_filename(context=context)
        csv_file = codecs.open(filename, 'wb', encoding=config.file_encoding)
        fl = csv.writer(
            csv_file, delimiter=config.csv_delimiter.encode(config.file_encoding),
            quotechar=config.csv_quotechar.encode(config.file_encoding))
        if not report_detail:
            # generate blank fine if there are not any pos order
            report_detail = [()]
        for ln in report_detail:
            fl.writerow(ln)
        csv_file.close()
        result_file = codecs.open(filename, 'rb', encoding=config.file_encoding).read()
        gen_file = base64.encodestring(result_file)
        if not result_file:
            os.remove(filename)

        self.write(cr, uid, ids, {
                   'report_file': gen_file, 'report_file_fname': filename}, context=context)

    def _prepare_mall_order(self, cr, uid, config, context=None):
        if not config:
            raise osv.except_osv(_('Warning!'), _(
                "mall configuration is required to generate pos mall report"))
        return {
            'name': time.strftime('%Y/%m/%d %H:%M:%S'),  # TO DO
            'date': time.strftime('%Y/%m/%d'),
            'config_id': config and config.id or False
        }

    # prepare one mall line per one pos order
    def _prepare_mall_line(self, cr, uid, pos, mall_id, context=None):
        res = {}
        line_obj = self.pool.get('pos.mall.report.line')
        payment_methods = [pm[0] for pm in line_obj._get_payement_method(cr, uid, context=context)]
        report = self.browse(cr, uid, mall_id, context)
        res.update(dict((method, 0.00) for method in payment_methods))
        tdldiscount = 0.00
        total_qty = 0
        for line in pos.lines:
            tdldiscount += (line.qty * line.price_unit) - \
                line.price_subtotal_incl
            total_qty += int(line.qty)

        payment_method = None
        max_val = -1
        for pm in report.config_id.payment_method_ids:
            for statement in pos.statement_ids:
                if pm.journal_id.id == statement.journal_id.id:
                    res[pm.payment_method] += statement.amount
            if abs(res[pm.payment_method]) > max_val:
                payment_method = pm.payment_method
                max_val = abs(res[pm.payment_method])

        if pos.return_date:
            txdate = pos.return_date
        else:
            txdate = pos.date_order
        res.update({
            'date': txdate,
            'tdldiscount': tdldiscount,
            'payment_method': payment_method,
            'mall_id': mall_id,
            'pos_order_id': pos.id,
            'qty': total_qty
        })

        return res

    def _create_mall_data(self, cr, uid, pos_ids, mall_config, mall_id=False, context=None):
        mall_obj = self.pool.get('pos.mall.report')
        pos_obj = self.pool.get('pos.order')
        mall_line_obj = self.pool.get('pos.mall.report.line')
        if not mall_id and not pos_ids:
            mall_id = mall_obj.create(
                cr, uid, self._prepare_mall_order(cr, uid, mall_config, context=context))
            return mall_id
        i = 1
        for pos in pos_obj.browse(cr, uid, pos_ids, context=context):
            if not mall_id:
                mall_id = mall_obj.create(
                    cr, uid, self._prepare_mall_order(cr, uid, mall_config, context=context))
            line = self._prepare_mall_line(cr, uid, pos, mall_id, context=context)
            i += 1
            mall_line_obj.create(cr, uid, line, context=context)
        return mall_id

    # this method call by scheduler
    def create_mall_report(self, cr, uid, ids=[], context=None):
        mall_obj = self.pool.get('pos.mall.report.config')
        config_ids = mall_obj.search(
            cr, uid, [('cron', '=', True)], context=context)
        for config in mall_obj.browse(cr, uid, config_ids, context=context):
            data = {'config_id': config.id}
            report_id = self.create(cr, uid, data, context=context)
            report = self.browse(cr, uid, report_id, context=context)
            report.generate_mall_report_line(context=context)
            report.transfer_report(context=context)

        return True

    # call by generate(manually) report button
    def generate_mall_report_line(self, cr, uid, ids, context=None):
        pos_obj = self.pool.get('pos.order')
        record = self.browse(cr, uid, ids[0], context=context)
        try:
            pos_ids = pos_obj.search(
                cr, uid, [
                    ('date_order', '>=', record.date + ' 00:00:00'),
                    ('date_order', '<=', record.date + ' 23:59:59'),
                    ('session_id.config_id', '=', record.config_id.pos_config_id.id),
                    '|',
                    ('state', '=', 'paid'), ('state', '=', 'done')
                ])
            pos_ids.extend(pos_obj.search(
                cr, uid,
                [
                    ('return_date', '>=', record.date + ' 00:00:00'),
                    ('return_date', '<=', record.date + ' 23:59:59'),
                    ('session_id.config_id', '=', record.config_id.pos_config_id.id),
                    '|', ('state', '=', 'paid'), ('state', '=', 'done')
                ]
            ))
            pos_ids = list(set(pos_ids))
            self._create_mall_data(
                cr, uid, pos_ids, record.config_id, record.id, context=context)
            self._generate_mall_text_file(cr, uid, ids)
            self.write(cr, uid, ids, {'state': 'report'}, context=context)
        except:
            self.write(cr, uid, ids, {'state': 'error'}, context=context)
        return True

    # transfer mall text file on ftp server
    def transfer_report(self, cr, uid, ids, context=None):
        if isinstance(ids, list):
            ids = ids[0]
        record = self.browse(cr, uid, ids, context=context)
        filename = record.get_filename(context=context)
        upload_file_path = filename
        if not os.path.isfile(upload_file_path):
            raise osv.except_osv(_('Warning!'), _(
                "Report File Missing.\n Generate or upload manually report file"))
        try:
            ftp = ftplib.FTP(record.config_id.ftp_server)
            ftp.login(record.config_id.ftp_user, record.config_id.ftp_password)
            upload_file = open(upload_file_path, 'r')
            # get the file name
            path_split = upload_file_path.split('/')
            file_name = path_split[len(path_split) - 1]
            # transfer the file to ftp sever
            ftp.storlines('STOR ' + file_name, upload_file)
            ftp.close()
            self.write(cr, uid, ids, {'state': 'transferred'}, context=context)
        except:
            self.message_post(
                cr, uid, ids,
                body="Please check your configuration connection settings.\
                We could not access to the FTP server.",
                subject="Transfer ERROR"
            )
            self.write(cr, uid, ids, {
                       'state': 'error', 'error_message': 'Check Your FTP logins'}, context=context)
        return True

    def action_cancel_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft', 'manual_report': 0,
                                  'report_file': '', 'report_file_fname': '',
                                  'line_ids': [(6, 0, [])]}, context=context)
        return True


class pos_mall_report_line(orm.Model):
    _name = 'pos.mall.report.line'
    _description = 'mall Report Lines'

    def _get_payement_method(self, cr, uid, context=None):
        method = []
        for column in self._columns.keys():
            if not column.endswith('_amount'):
                continue
            key = column.replace('_amount', '').upper()
            method.append((column, key))
        sorted(method, key=lambda m: m[0])
        return method

    def _get_payment_method_uppercase(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.payment_method.replace('_amount', '').upper()\
                if line.payment_method else False
        return res

    _columns = {
        'mall_id': fields.many2one('pos.mall.report', 'mall'),
        'date': fields.datetime('Date'),
        'no_of_transation': fields.related(
            'pos_order_id',
            'name',
            type='char',
            string='# of Transations'),
        'tdldiscount': fields.float('Discount for mall'),
        'netamount': fields.related(
            'pos_order_id',
            'amount_total',
            type='float',
            string='Total'),
        'payment_method': fields.selection(_get_payement_method, string="Payment Method"),
        'payment_method_uppercase': fields.function(
            _get_payment_method_uppercase,
            type='char',
            method=True,
            string="Payment Method (Uppercase)",
            store=True),
        'ch_amount': fields.float('CH'),
        'ci_amount': fields.float('CI'),
        'co_amount': fields.float('CO'),
        'ot_amount': fields.float('OT'),
        'cz_amount': fields.float('CZ'),
        'xy_amount': fields.float('XY'),
        'zp_amount': fields.float('ZP'),
        'vip_code': fields.char('VIP Code', size=64),
        'pos_order_id': fields.many2one('pos.order', 'POS Order'),
        'qty': fields.integer('Qty')
    }


class pos_mall_report_payment_method(orm.Model):
    _name = 'pos.mall.report.payment.method'
    _description = 'Mall report payment method'

    def _get_payement_method(self, cr, uid, context=None):
        return self.pool.get('pos.mall.report.line')._get_payement_method(
            cr, uid, context=None)

    _columns = {
        'config_id': fields.many2one('pos.mall.report.config', string="Config"),
        'journal_id': fields.many2one('account.journal', string="Journal", required=True),
        'payment_method': fields.selection(_get_payement_method, string="Payment Method",
                                           required=True)
    }


class pos_mall_report_template_line(orm.Model):
    _name = 'pos.mall.report.template.line'
    _description = 'POS Report mall Template Rel'

    _columns = {
        'config_id': fields.many2one('pos.mall.report.config', string="Config"),
        'type': fields.selection(
            [('field_id', 'Field'), ('python_code', 'Python code'), ('value', 'Value')],
            string="Type", required=True),
        'model_id': fields.many2one('ir.model', string='Model', required=True),
        'field_id': fields.many2one(
            'ir.model.fields', 'Field', domain="[('model_id', '=', model_id)]"),
        'python_code': fields.text('Python code'),
        'value': fields.char('Value'),
        'sequence': fields.integer(
            'Sequence',
            help="Gives the sequence order when displaying a list of pos report mall line."),
    }

    _order = 'config_id desc, sequence, id'

    def compute_line(self, cr, uid, ids, obj, context=None):
        if isinstance(ids, list):
            ids = ids[0]
        tmpl_line = self.browse(cr, uid, ids, context=context)
        res = None
        if tmpl_line.type == 'python_code':
            env = {'line': obj, 'datetime': datetime}
            if hasattr(obj, 'date'):
                user_obj = self.pool.get('res.users')
                user = user_obj.browse(cr, uid, uid, context=context)
                timezone = user.tz
                from_zone = tz.gettz('UTC')
                to_zone = tz.gettz(timezone)
                utc = datetime.strptime(obj.date, '%Y-%m-%d %H:%M:%S')
                utc = utc.replace(tzinfo=from_zone)
                central = utc.astimezone(to_zone)
                env['txdate'] = central
            res = eval(tmpl_line.python_code, env)
        elif tmpl_line.type == 'field_id':
            field = tmpl_line.field_id
            if field.model == obj._name:
                res = getattr(obj, field.name)
                if field.ttype == 'many2one':
                    res = res.name_get(context=context)[0][1]
                elif field.ttype == 'float' and not res:
                    res = 0.0
                elif field.ttype == 'float':
                    digit = dp.get_precision('Point Of Sale')(cr)
                    digit = digit and digit[1] or 2
                    res = round(res, digit)
        else:
            res = tmpl_line.value
        return res

    def _default_model_id(self, cr, uid, context=None):
        model_ids = self.pool.get('ir.model').search(
            cr, uid, [('model', '=', 'pos.mall.report.line')], context=context)
        model_id = model_ids[0] if model_ids else None
        return model_id

    _defaults = {
        'model_id': _default_model_id
    }

