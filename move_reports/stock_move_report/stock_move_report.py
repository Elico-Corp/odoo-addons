# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
import time
from datetime import datetime
import pytz
import os,glob
import csv,xlwt
from xlsxwriter.workbook import Workbook
import shutil
import base64
from tools.translate import _

import logging
_logger = logging.getLogger(__name__)

import sys
reload(sys) 
sys.setdefaultencoding('utf-8')

class stock_move_report_wizard(osv.osv_memory):
    _name = 'stock.move.report.wizard'
    _description = 'Stock Move Report Wizard'

    _columns = {
        'start_date':   fields.datetime('Start Date'),
        'end_date':     fields.datetime('End Date'),
        'type':         fields.selection([('in','In'),('out','Out'),('internal','Internal'),('scrap','Scrap'),('consumption','Consumption'),('production','production'),('all','all')],string='Type',required=True),
    }

    _defaults = {
        'start_date': lambda *a: time.strftime('%Y-%m-%d 16:00:00'),
        'end_date': lambda *a: time.strftime('%Y-%m-%d 15:59:59'),
        'type': 'in',
    }
    
    def generate_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.browse(cr, uid, ids, context=context)[0]        
        context['start_date'] = data.start_date
        context['end_date'] = data.end_date
        context['type'] = data.type
        
        pi_obj = self.pool.get('stock.move.report')
        pi_obj.generate_report(cr, uid, context)

        mod_obj = self.pool.get('ir.model.data')

        res = mod_obj.get_object_reference(cr, uid, 'move_reports', 'view_move_report_tree')
        res_id = res and res[1] or False,

        return {
            'name': _('Stock Move Report'),
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': res_id,
            'res_model': 'stock.move.report',
            'context': "{}",
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': False,
        }
stock_move_report_wizard()


class stock_move_report(osv.osv):
    _name = 'stock.move.report'
    _description = 'Stock Move Report'
    _rec_name = "move_id"
    _order = 'date desc'
    
    
    _create_sql = """
                INSERT INTO stock_move_report
                    (
                        create_uid,
                        write_uid,
                        create_date,
                        write_date,
                        move_id,
                        date,
                        date_expected,
                        origin,
                        picking_id,
                        picking_name,
                        type,
                        pick_return,
                        partner_ref,
                        partner_id,
                        partner_name,
                        stock_type_id,
                        stock_type_name,
                        category_id,
                        category_name,
                        product_sku,
                        product_id,
                        product_name,
                        move_qty,
                        product_qty,
                        uom_id,
                        uom_name,
                        product_uom_name,
                        uom_factor,
                        product_price,
                        price_unit,
                        cost_total,
                        po_price,
                        amount_total,
                        loc_name,
                        loc_dest_name,
                        return_reason
                    )
                SELECT %d, %d, now() AT TIME ZONE 'UTC', now() AT TIME ZONE 'UTC',
                        m.id as move_id, m.date, m.date_expected, m.origin,
                        p.id as picking_id, p.name as picking_name, 
                        p.type as type, p.return as pick_return,
                        rp.ref as partner_ref, rp.id as partner_id, rp.name as partner_name,
                        st.id as stock_type_id , st.name as stock_type_name,
                        c.id as category_id, cp.name || ' / ' || c.name as category_name,
                        m.product_code as product_sku, pp.id as product_id, pt.name as product_name,
                        m.product_qty as move_qty, m.product_qty * pu.factor / u.factor as product_qty,
                        u.id as uom_id, u.name as uom_name, pu.name as product_uom_name, pu.factor / u.factor as uom_facotr,
                        m.price_unit / pu.factor * u.factor as product_price, m.price_unit as price_unit, round(m.product_qty * pu.factor / u.factor*m.price_unit, 4) as cost_total,
                        m.po_price as po_price, m.amount_total as amount_total,
                        sl.complete_name as location_name,
                        sld.complete_name as location_dest_name,
                        srr.code as return_reason
                    from stock_move m
                        left join stock_picking p on p.id = m.picking_id
                        left join product_product pp on pp.id = m.product_id
                        left join product_template pt on pt.id = pp.product_tmpl_id
                        left join product_category c on c.id = pt.categ_id
                        left join product_category cp on cp.id = c.parent_id
                        left join product_stock_type st on st.id = pt.stock_type_id
                        left join product_uom u on u.id = m.product_uom
                        left join product_uom pu on pu.id = pt.uom_id
                        left join res_partner rp on rp.id = m.partner_id
                        left join stock_location sl on sl.id = m.location_id
                        left join stock_location sld on sld.id = m.location_dest_id
                        left join stock_return_reason srr on srr.id = m.return_reason_id
                        
                    where  %s 
                    order by m.id
                    """#uid,uid,domain
    _reverse_sql = """
                INSERT INTO stock_move_report
                    (
                        create_uid,
                        write_uid,
                        create_date,
                        write_date,
                        move_id,
                        date,
                        date_expected,
                        origin,
                        picking_id,
                        picking_name,
                        type,
                        pick_return,
                        partner_ref,
                        partner_id,
                        partner_name,
                        stock_type_id,
                        stock_type_name,
                        category_id,
                        category_name,
                        product_sku,
                        product_id,
                        product_name,
                        move_qty,
                        product_qty,
                        uom_id,
                        uom_name,
                        product_uom_name,
                        uom_factor,
                        product_price,
                        price_unit,
                        cost_total,
                        po_price,
                        amount_total,
                        loc_name,
                        loc_dest_name,
                        return_reason
                    )
                SELECT %d, %d, now() AT TIME ZONE 'UTC', now() AT TIME ZONE 'UTC',
                        m.id as move_id, m.date, m.date_expected, m.origin,
                        p.id as picking_id, p.name as picking_name, 
                        p.type as type, p.return as pick_return,
                        rp.ref as partner_ref, rp.id as partner_id, rp.name as partner_name,
                        st.id as stock_type_id , st.name as stock_type_name,
                        c.id as category_id, cp.name || ' / ' || c.name as category_name,
                        m.product_code as product_sku, pp.id as product_id, pt.name as product_name,
                        -m.product_qty as product_qty, -m.product_qty * pu.factor / u.factor,
                        u.id as uom_id, u.name as uom_name, pu.name as product_uom_name, pu.factor / u.factor as uom_facotr,
                        m.price_unit / pu.factor * u.factor as product_price, m.price_unit as price_unit, round(-m.product_qty * pu.factor / u.factor *m.price_unit,4) as cost_total,
                        m.po_price as po_price, m.amount_total as amount_total,
                        sl.complete_name as location_name,
                        sld.complete_name as location_dest_name,
                        srr.code as return_reason
                    from stock_move m
                        left join stock_picking p on p.id = m.picking_id
                        left join product_product pp on pp.id = m.product_id
                        left join product_template pt on pt.id = pp.product_tmpl_id
                        left join product_category c on c.id = pt.categ_id
                        left join product_category cp on cp.id = c.parent_id
                        left join product_stock_type st on st.id = pt.stock_type_id
                        left join product_uom u on u.id = m.product_uom
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        left join res_partner rp on rp.id = m.partner_id
                        left join stock_location sl on sl.id = m.location_id
                        left join stock_location sld on sld.id = m.location_dest_id
                        left join stock_return_reason srr on srr.id = m.return_reason_id
                    WHERE  %s 
                    ORDER BY m.id;
                    """#uid,uid,domain
    _in_header = " date, origin, picking_name, type, pick_return, partner_ref, partner_name, stock_type_name, category_name, product_sku, product_name, move_qty, product_qty, uom_name, product_uom_name, product_price, po_price, amount_total, loc_name, loc_dest_name, return_reason"
    _out_header = " date, origin, picking_name, type, pick_return, partner_ref, partner_name, stock_type_name, category_name, product_sku, product_name, move_qty, product_qty, uom_name, product_uom_name, uom_factor, product_price, price_unit, cost_total, loc_name, loc_dest_name, return_reason"
    _read_header = " date, origin, picking_name, type, pick_return, partner_ref, partner_name, stock_type_name, category_name, product_sku, product_name, move_qty, product_qty, uom_name, product_uom_name, uom_factor, product_price, price_unit, cost_total, loc_name, loc_dest_name, return_reason"
    _read_sql = """
        SELECT %s FROM stock_move_report;
        """
    
    def _get_table_data(self, cr, uid, type, context=None):
        #print "==============#LY %s"% self._read_sql
        if type == "in":
            header = self._in_header
        elif type== "out":
            header = self._out_header
        else:
            header = self._read_header
        
        sql = self._read_sql%header
        cr.execute(sql)
        content = cr.fetchall()
        header = header.split(',')
        return header, content
    
    def _get_warehouse_group(self, cr, uid, name="Warehouse"):
        group_ids = self.pool.get('mail.group').search(cr, uid, [('name', 'ilike', name)])
        return group_ids and group_ids[0] or False
    
    def _prepare_filter(self, cr, uid, context=None):
        if not context:
            context={}
        
        start_date = context.get('start_date','2013-03-31 16:00:00') #timezone 'CST' to 'UTC'
        end_date = context.get('end_date','2013-04-30 15:59:59')# timezone 'CST' to 'UTC'
        type = context.get('type','in')
        res="""
            m.date >= '%s'
                        and m.date <= '%s'
                        and m.state = 'done'
            """%(start_date, end_date)
        if type == 'in':
            res += """AND (p.type = 'in' and p.return='none')
                    """
        elif type == 'out':
            res += """AND (p.type = 'out' and p.return='none')
                    """
        elif type == 'internal':
            res += """and p.type = 'internal'
                    """
        elif type == 'scrap':
            res += """AND m.location_id IN (SELECT id FROM stock_location WHERE usage='inventory')
                        AND m.location_dest_id NOT IN (SELECT id FROM stock_location WHERE usage='inventory')
                    """
        elif type == 'consumption':
            res += """AND m.production_id IS NULL
                        AND m.location_id NOT IN (SELECT id FROM stock_location WHERE usage='production')
                        AND m.location_dest_id IN (SELECT id FROM stock_location WHERE usage='production')
                    """
        elif type == 'production':
            res += """AND m.production_id IS NOT NULL
                        AND m.location_id IN (SELECT id FROM stock_location WHERE usage='production')
                        AND m.location_dest_id NOT IN (SELECT id FROM stock_location WHERE usage='production')
                    """
        return res
    
    def _reverse_filter(self, cr, uid, context=None):
        if not context:
            context={}
        
        start_date = context.get('start_date','2013-03-31 16:00:00') #timezone 'CST' to 'UTC'
        end_date = context.get('end_date','2013-04-30 15:59:59')# timezone 'CST' to 'UTC'
        type = context.get('type','in')
        res="""
            m.date >= '%s'
                        AND m.date <= '%s'
                        AND m.state = 'done'
            """%(start_date, end_date)
        
        if type == 'in':
            res += """AND (p.type = 'out' AND p.return='supplier')
                    """
        elif type == 'out':
            res += """AND (p.type = 'in' AND p.return='customer')
                    """
        elif type == 'scrap':
            res += """AND m.location_id NOT IN (SELECT id FROM stock_location WHERE usage='inventory')
                        AND m.location_dest_id IN (SELECT id FROM stock_location WHERE usage='inventory')
                    """
#         elif type == 'consumption':
#             res += """AND m.production_id IS NULL
#                         AND m.location_id NOT IN (SELECT id FROM stock_location WHERE usage='production')
#                         AND m.location_dest_id IN (SELECT id FROM stock_location WHERE usage='production')
#                     """
#         elif type == 'production':
#             res += """AND m.production_id IS NOT NULL
#                         AND m.location_id NOT IN (SELECT id FROM stock_location WHERE usage='production')
#                         AND m.location_dest_id IN (SELECT id FROM stock_location WHERE usage='production')
#                     """
        else:
            res="False"
        return res
    
    def _create_message(self, cr, uid, attachment_ids=None,context=None):
        mess_pool = self.pool.get('mail.message')
        partner_ids = [uid]
        if uid != 1:
            partner_ids.append(1)
        
        tz = pytz.timezone(context.get('tz','Asia/Shanghai'))
        tznow = pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
        message_id = mess_pool.create(cr, uid, {
                'type': 'notification',
                'partner_ids': partner_ids,
                'subject': 'Your Move Report has been generated %s'%tznow,
                'body': 'Your Move Report has been generated %s'%tznow,
                'subtype_id': 1,
                'res_id': self._get_warehouse_group(cr, uid),
                'model': 'mail.group',
                'record_name': 'Stock Move Report',
                'attachment_ids': attachment_ids
            })
        mess_pool.set_message_starred(cr, uid, [message_id], True)
        return message_id
    
    _columns = {
        'move_id':          fields.many2one('stock.move', 'Stock Move', required=True),
        'date_expected':    fields.datetime('Date Expected'),
        'date':             fields.datetime('Date'),
        'origin':           fields.char('Origin', size=32),
        'picking_id':       fields.many2one('stock.picking', 'Stock Picking'),
        'picking_name':     fields.char('Picking Name', size=64),
        'type':             fields.char('Type', size=16),
        'pick_return':      fields.char('Return', size=16),
        'return_reason':    fields.char('Return Reason', size=16),
        'partner_ref':      fields.char('Partner Ref', size=16),
        'partner_name':     fields.char('Partner Name', size=128),
        'partner_id':       fields.many2one('res.partner', 'Partner'),
        'stock_type_id':    fields.many2one('product.stock_type',string='Stock Type'),
        'stock_type_name':  fields.char('Stock Type Name', size=128),
        'category_id':      fields.many2one('product.category',string='Category'),
        'category_name':    fields.char('Category Name', size=128),
        'product_sku':      fields.char('SKU', size=16),
        'product_name':     fields.char('Product Name', size=1024),
        'product_id':       fields.many2one('product.product', 'Product'),
        'move_qty':         fields.float("Move Quantity", digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_qty':      fields.float("Product Quantity", digits_compute=dp.get_precision('Product Unit of Measure')),
        'uom_id':           fields.many2one('product.uom',string='UoM'),
        'uom_factor':       fields.float('Uom Ratio' ,digits=(12, 12),
                                    help='How much bigger or smaller this unit is compared to the reference Unit of Measure for this category:\n'\
                                        '1 * (reference unit) = ratio * (this unit)'),
        'uom_name':         fields.char('UoM Name', size=32),
        'product_uom_name': fields.char('Product UoM', size=32),
        'loc_name':         fields.char('Source Location Name', size=256),
        'loc_dest_name':    fields.char('Dest Location Name', size=256),
        'po_price':         fields.float("PO Price", digits_compute=dp.get_precision('Account')),
        'product_price':    fields.float("Product Price", digits_compute=dp.get_precision('Account')),
        'price_unit':       fields.float("Price Unit", digits_compute=dp.get_precision('Account')),
        'amount_total':     fields.float("Purchase total", digits_compute=dp.get_precision('Account')),
        'cost_total':         fields.float("Cost Total", digits_compute=dp.get_precision('Account')),
    }
    _defaults = {
    }    
    
    
    def generate_report(self, cr, uid, context=None):
        cr.execute("""TRUNCATE TABLE stock_move_report""")
        
        filter = self._prepare_filter(cr, uid, context)
        #create sql
        sql = self._create_sql%(uid, uid, filter)
        cr.execute(sql)
        #reverse sql
        type = context.get('type','in')
        if type not in ('consumption','production'):
            filter = self._reverse_filter(cr, uid, context)
            sql = self._reverse_sql%(uid, uid, filter)
            if sql:
                cr.execute(sql)
        #create fold
        if not os.path.exists('/tmp/oe-report/'):
            os.mkdir('/tmp/oe-report')
        filelist = glob.glob("/tmp/oe-report/*.xlsx")
        for f in filelist:
            os.remove(f)
        os.chmod('/tmp/oe-report',0777)#check rights  
        #TODO
        
        header, content = self._get_table_data(cr, uid, type, context)
        
        csv_file = '/tmp/stock.move.report.csv'
        with open(csv_file, "wb") as f:
            fileWriter = csv.writer(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
            fileWriter.writerow(header)
            fileWriter.writerows(content)
        #cr.execute("COPY stock_move_in_report TO '/tmp/oe-report/stock.move.report.csv' WITH CSV HEADER NULL AS '' DELIMITER ';'")
        
        #create message
        message_id = self._create_message(cr, uid,context=context)
        
        attachment_pool = self.pool.get('ir.attachment')
        
        def convert_time(time):
            tz = pytz.timezone('Asia/Shanghai')
            time = pytz.utc.localize(datetime.strptime(time,'%Y-%m-%d %H:%M:%S')).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
            return time
        period = "%s~%s"%(convert_time(context.get('start_date','2013-03-31 16:00:00')),convert_time(context.get('end_date','2013-03-31 16:00:00')))
        
        xlsfile = '/tmp/oe-report/stock.move.report.%s[%s].xlsx'%(type,period)
        #print xlsfile
        w = Workbook(xlsfile)
        ws = w.add_worksheet('Stock Moves')
        
        ufile = open(csv_file,'r')
        spamreader = csv.reader(ufile, delimiter=',', quotechar='"')
        #line = 0
        for rowx, row in enumerate(spamreader):
            for colx, cell in enumerate(row):
                ws.write(rowx, colx, unicode(cell, 'utf-8'))
#         for row in spamreader:
#             print ', '.join(row)
#             col=0
#             for cell in row:
#                 ws.write(line,col,unicode(cell, 'utf-8'))
#                 col += 1
#             line +=1
        w.close()
        shutil.make_archive("/tmp/stock_move_report_%s[%s]"%(type,period), "zip", "/tmp/oe-report")
        
        zipfile = open('/tmp/stock_move_report_%s[%s].zip'%(type,period),'r')
         
        attachment_id = attachment_pool.create(cr, uid, {
            'name': "stock.move.report.%s[%s].zip"%(type,period),
            'datas': base64.encodestring(zipfile.read()),
            'datas_fname': "stock.move.report.%s[%s].zip"%(type,period),
            'res_model': 'mail.message',
            'res_id': message_id,
        })
        cr.execute("""
            INSERT INTO message_attachment_rel(
                message_id, attachment_id)
                VALUES (%s, %s);
                """, (message_id, attachment_id))
                
        return True

stock_move_report()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
