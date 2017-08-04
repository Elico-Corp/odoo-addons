# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

import threading
import time
from openerp import netsvc
from openerp import pooler
from openerp import tools
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from osv import osv, fields
from datetime import datetime
from dateutil.relativedelta import relativedelta
import math
import pytz
import logging
logger = logging.getLogger(__name__)


class product_product(osv.osv):
    _inherit = 'product.product'    

    _columns = {
        'auto_mo':  fields.boolean(_('Validate Automatic MO ?'), help="Indicates whether the MO for this product are automatically processed when Raw Materials quantities are enough."),
        'force_mo': fields.boolean(_('Force Availability MO ?'), help="Indicates whether the MO for this product are automatically processed regardless of the Raw Materials quantities."),
        'mpq':      fields.float(_('Minimum Produce Quantity'), digits=(12,3)),
    }
    _defaults = {
        'auto_mo':  lambda *a: False,
        'force_mo': lambda *a: False,
        'mpq':      lambda *a: 0,
    }
product_product()



class mrp_production_scheduler(osv.osv_memory):
    _name = 'mrp.production.scheduler'
    _description = 'Compute auto MO scheduler'

    def _init_pts_id(self, cr, uid, context=None):
        now = datetime.now()
        ids = self.pool.get('delivery.time').search(cr, uid, [('type', '=', 'pts'), ('active', '=', True), ('name', 'ilike', datetime.strftime(now, '%y%m%d') + '%')])
        return ids and ids[0] or False

    _columns = {
        'shop':   fields.many2one('sale.shop', 'Shop', required=True),
        'pts_id': fields.many2one('delivery.time', 'Preparation Time', select=True, domain=[('type', '=', 'pts'), ('active', '=', True)]),
    }
    _defaults = {
        'shop':   lambda *a: 1,
        'pts_id': lambda self, cr, uid, context: self._init_pts_id(cr, uid, context=context),
    }

    def _mrp_production_calculation_all(self, cr, uid, shop_ids, pts_id=False, context=None):
        """
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        """
        mo_pool = self.pool.get('mrp.production')
        procurement_pool = self.pool.get('procurement.order')
        move_lines_obj = self.pool.get('stock.move')
        logger.info('>>>>>>>>>>>>>>> AUTO MO start <<<<<<<<<<<<<<<')
        #As this function is in a new thread, need to open a new cursor because the old one may be closed
        new_cr = pooler.get_db(cr.dbname).cursor()
        
        loc_ids = []
        for shop in self.pool.get('sale.shop').browse(new_cr, uid, shop_ids):
            loc_ids.append(shop.warehouse_id.lot_stock_id.id) 
            #loc_ids.append(shop.warehouse_id.lot_input_id.id)
            #loc_ids.append(shop.warehouse_id.lot_output_id.id)
        
        
        #Force MO
        args = [('state', 'in', ['confirmed', 'ready']), ('location_dest_id', 'in', loc_ids), ('product_id.auto_mo', '=', True), ('product_id.force_mo', '=', True)]
        if pts_id:
            args.append(('pts_id', '=', pts_id))
        mo_ids = mo_pool.search(new_cr, uid, args)
        for mo in mo_pool.browse(new_cr, uid, mo_ids):
            try:
                done = 0.0
                for move in mo.move_created_ids2:
                    if move.product_id == mo.product_id:
                        if not move.scrapped:
                            done += move.product_qty
                product_qty = (mo.product_qty - done) or mo.product_qty
                count = 0
                while count<5:
                    try:
                        mo_pool.action_produce(new_cr, uid, mo.id, product_qty, 'consume_produce', context=context)
                        new_cr.commit()
                        break
                    except:
                        count+=1
                        time.sleep(0.5)
                        continue
                if count==5:
                    logger.debug('==== #LY FORCE MO failed in 5 times %s===='%mo.id)
            except Exception as err:
                logger.warning('######### /!\ FORCE MO %s : %s \t(lock ?) /!\ '%(mo.id,err))
        
        
        #Auto MO
        products_ids = self.pool.get('product.product').search(new_cr, uid, [('auto_mo', '=', True), ('force_mo', '=', False)])
        #logger.debug("======= products_ids %s"%(products_ids))
        if products_ids:
            args = [('state', 'in', ['confirmed', 'ready']), ('location_dest_id', 'in', loc_ids), ('product_id', 'in', products_ids)]
            if pts_id:
                args.append(('pts_id', '=', pts_id))
            mo_ids = mo_pool.search(new_cr, uid, args)
            #logger.debug("======= mo_ids %s"%(mo_ids))
            if mo_ids:
                wf_service = netsvc.LocalService("workflow")
                for production in mo_pool.browse(new_cr, uid, mo_ids):
                    try:
                        produce_rate = 1
                        error_raw_nostock = ''
                        error_raw_done = production.move_lines2
                        error_pdt_done = production.move_created_ids2
                        if error_raw_done or error_pdt_done:
                            produce_rate = 0
                            #logger.debug("======= raw done %s - finished %s"%(error_raw_done, error_pdt_done))
                        else:
                            # For each Raw Materials, check availability
                            for scheduled in production.move_lines:
                                qty_available = float(scheduled.product_id.qty_available * scheduled.product_id.uom_id.factor)
                                qty_requested = float(scheduled.product_qty * scheduled.product_uom.factor)
                                #logger.debug("======= %s: %s ok - need %s"%(scheduled.product_id.default_code, qty_available, qty_requested))
                                if qty_available <= 0 or (qty_available < (qty_requested / production.product_qty)):
                                    produce_rate = 0
                                    error_raw_nostock += str(scheduled.product_id.default_code or scheduled.product_id.name_sort_en) + '\n'
                                elif qty_available < qty_requested:
                                    new_produce_rate = qty_available / qty_requested
                                    if new_produce_rate < produce_rate:
                                        produce_rate = new_produce_rate
                        
                        if produce_rate == 1:#Enough of each Raw Materials
                            if production.state == 'confirmed':
                                if production.picking_id:
                                    moves = map(lambda x: x.id, production.picking_id.move_lines)
                                    if moves:
                                        procurement_ids = procurement_pool.search(new_cr, uid, [('move_id','in',moves),('state','not in',['draft','done','cancel'])])
                                        for procurement in procurement_pool.browse(new_cr, uid, procurement_ids):
                                            try:
                                                if procurement.state=='exception':
                                                    wf_service.trg_validate(uid, 'procurement.order', procurement.id, 'button_restart', new_cr)
                                                    new_cr.commit()
                                                wf_service.trg_validate(uid, 'procurement.order', procurement.id, 'button_check', new_cr)
                                                new_cr.commit()
                                            except Exception as err:
                                                logger.info('>>> Error during Running Procurement %s : %s' % (procurement.id, err))
                                
                                mo_pool.force_production(new_cr, uid, [production.id])
                            wf_service.trg_validate(uid, 'mrp.production', production.id, 'button_produce', new_cr)
                            try:
                                mo_pool.action_produce(new_cr, uid, production.id, production.product_qty, 'consume_produce', context=context)
                                new_cr.commit()
                            except Exception as err:
                                logger.info('>>> Error during Producing %s : %s' % (production.id, err))
                        elif produce_rate > 0:#Partial
                            if production.state == 'confirmed':
                                if production.picking_id:
                                    moves = map(lambda x: x.id, production.picking_id.move_lines)
                                    if moves:
                                        procurement_ids = procurement_pool.search(new_cr, uid, [('move_id','in',moves),('state','not in',['draft','done','cancel'])])
                                        for procurement in procurement_pool.browse(new_cr, uid, procurement_ids):
                                            try:
                                                if procurement.state=='exception':
                                                    wf_service.trg_validate(uid, 'procurement.order', procurement.id, 'button_restart', new_cr)
                                                    new_cr.commit()
                                                wf_service.trg_validate(uid, 'procurement.order', procurement.id, 'button_check', new_cr)
                                                new_cr.commit()
                                            except Exception as err:
                                                logger.info('>>> Error during Running Procurement %s : %s' % (procurement.id, err))
                                    
                                product_qty_todo = production.product_qty * produce_rate
                                product_qty_todo = (math.floor(product_qty_todo / production.product_id.uom_id.rounding)) * production.product_id.uom_id.rounding
                                product_qty_left = production.product_qty - product_qty_todo
                                produce_rate = float(product_qty_left) / float(production.product_qty)
                                #logger.debug("======= %s ok - left %s"%(product_qty_todo, product_qty_left))
                                # Copy MO with available quantities to produce + confirm it + action_produce
                                default_val = {
                                    'product_qty': product_qty_todo,
                                    'state': 'draft',
                                }
                                new_mo_id = mo_pool.copy(new_cr, uid, production.id, default_val)
                                # New MO : add move_lines, product_lines, etc...
                                wf_service.trg_validate(uid, 'mrp.production', new_mo_id, 'button_confirm', new_cr)
                                wf_service.trg_validate(uid, 'mrp.production', new_mo_id, 'button_produce', new_cr)
                                new_cr.commit()
                                try:
                                    mo_pool.action_produce(new_cr, uid, new_mo_id, product_qty_todo, 'consume_produce', context=context)
                                    new_cr.commit()
                                except Exception as err:
                                    logger.info('>>> Error during Producing %s : %s' % (new_mo_id, err))
                                #logger.debug("======= new_mo_id %s"%(new_mo_id))
                                
                                # Original MO : change product_qty + change qty for stock.move
                                mo_pool.write(new_cr, uid, [production.id], {'product_qty': product_qty_left}, context)
                                
                                for move_line in  production.move_lines:
                                    move_lines_obj.write(new_cr, uid, [move_line.id], {'product_qty' : move_line.product_qty * produce_rate})
                                
                                if production.picking_id:
                                    for move_line in  production.picking_id.move_lines:
                                        move_lines_obj.write(new_cr, uid, [move_line.id], {'product_qty' : move_line.product_qty * produce_rate})
                                    
                                for move_line in  production.move_created_ids:
                                    move_lines_obj.write(new_cr, uid, [move_line.id], {'product_qty' : move_line.product_qty * produce_rate})
                                
                                mo_line_obj = self.pool.get('mrp.production.product.line')
                                for mo_line in  production.product_lines:
                                    mo_line_obj.write(new_cr, uid, [mo_line.id], {'product_qty' : mo_line.product_qty * produce_rate})
                                new_cr.commit()
                        else:
                            error_message = ''
                            if error_raw_nostock:
                                error_message = 'Not enough stock of Raw Material : ' + error_raw_nostock
                            if error_raw_done:
                                error_message = 'Raw Material moves are already in Done State.'
                            if error_pdt_done:
                                error_message = 'Finished Goods move is already in Done State.'
                            error_message += '\nImpossible to automatically confirm the MO.'
                            mo_pool.write(new_cr, uid, production.id, {'last_exception':error_message})
                        new_cr.commit()
                    except Exception as err:
                        mo_pool.write(new_cr, uid, production.id, {'last_exception':'Error %s' % err})
                        new_cr.commit()
                        logger.warning('######### /!\ AUTO MO %s : %s \t(lock ?) /!\ '%(production.id,err))
        #close the new cursor
        new_cr.commit()
        new_cr.close()
        logger.info('>>>>>>>>>>>>>>> AUTO MO DONE <<<<<<<<<<<<<<<')
        return {}
    
    
    def run_mo_scheduler(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        """
        shop_ids = []
        pts_id = []
        datas = self.read(cr, uid, ids, context=context)
        for data in datas:
            if data['shop'][0] not in shop_ids:
                shop_ids.append(data['shop'][0])
            pts_id = data['pts_id'] and data['pts_id'][0] or False
        threaded_calculation = threading.Thread(target=self._mrp_production_calculation_all, name='mo_scheduler', args=(cr, uid, shop_ids, pts_id, context))
        threaded_calculation.start()
        return {'type': 'ir.actions.act_window_close'}

mrp_production_scheduler()


class procurement_order(osv.osv):
    _inherit = 'procurement.order'
    
    def run_scheduler(self, cr, uid, automatic=False, use_new_cursor=False, cancel_mo=True, context=None):
        ''' Runs through scheduler.
        @param use_new_cursor: False or the dbname
        '''
        mess_pool = self.pool.get('mail.message')
        mo_pool = self.pool.get('mrp.production')
        pick_pool = self.pool.get('stock.picking')
        move_pool = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        tz = pytz.timezone('Asia/Shanghai')
        
        partner_ids = [uid]
        if uid != 1:
            partner_ids.append(1)
        
        cr2  = pooler.get_db(cr.dbname).cursor()
        
        header = '<p>PO Scheduler has started at ' + pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S') + ' with options:<br />'
        header += 'Automatic Order Points ? ' + str(automatic) + '<br />'
        header += 'Cancel MO ? ' + str(cancel_mo) + '</p>'
        body = ''
        
        message_id = mess_pool.create(cr2, uid, {
            'type': 'comment',
            'partner_ids': partner_ids,
            'subject': 'PO Scheduler started at ' + pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M'),
            'body': header,
            'subtype_id': 1,
            'res_id': self._get_warehouse_group(cr2, uid),
            'model': 'mail.group',
            'record_name': 'PO Scheduler',
        })
        cr2.commit()
        
        logger.info('>>>>>>>>>>>>>>> PROC SCHEDULER STARTS')
        self._procure_confirm(cr, uid, use_new_cursor=use_new_cursor, context=context)
        logger.info('>>>>>>>>>>>>>>> PROC CONFIRMED')
        self._procure_orderpoint_confirm(cr, uid, automatic=automatic, use_new_cursor=use_new_cursor, context=context)
        logger.info('>>>>>>>>>>>>>>> OP CONFIRMED')
        
        # Delete all MOs created by the Scheduler and with no pts_id
        if cancel_mo:
            mo_ids = mo_pool.search(cr2, uid, [('state', 'not in', ['cancel', 'done']), ('pts_id', '=', False), ('origin', '=', 'SCHEDULER')]) or []
            for mo in mo_pool.read(cr2, uid, mo_ids, ['name','picking_id','move_prod_id']):
                try:
                    if mo['picking_id'] and mo['picking_id'][0]:
                        pick_pool.action_cancel(cr2, uid, [mo['picking_id'][0]], context=context)
                        cr2.commit()
                    if mo['move_prod_id'] and mo['move_prod_id'][0]:
                        move_pool.action_cancel(cr2, uid, [mo['move_prod_id'][0]], context=context)
                        cr2.commit()
                    wf_service.trg_validate(uid, 'mrp.production', mo['id'], 'button_cancel', cr2)
                except Exception as err:
                    logger.info('>>> Error during Canceling MO %s : %s' % (mo['name'], err))
            cr2.commit()
            logger.info('>>>>>>>>>>>>>>> CANCELING MO DONE')
            body = '<p>Generated Manufacturing Orders have been canceled at ' + pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S') + '</p>' + body
            mess_pool.write(cr2, 1, message_id, {'body': header + body, })
        
        body = '<p>Scheduler finished at ' + pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S') + '</p>' + body
        mess_pool.write(cr2, 1, message_id, {'body': header + body, })
        cr2.commit()
        cr2.close()
        logger.info('>>>>>>>>>>>>>>> PO Scheduler DONE')
    
    
    def _get_warehouse_group(self, cr, uid, name="Warehouse"):
        group_ids = self.pool.get('mail.group').search(cr, uid, [('name', 'ilike', name)])
        return group_ids and group_ids[0] or False
    
    
    def _cron_scheduler(self, cr, uid, slot_start, context=None):
        tz = pytz.timezone('Asia/Shanghai')
        delivery_pool = self.pool.get('delivery.time')
        slot_ids = self.pool.get('delivery.time.slot').search(cr, uid, [('start_time', '=', slot_start), ('type', '=', 'pts')])
        if slot_ids:
            name_pts = pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%y%m%d') + '%'
            pts_ids = delivery_pool.search(cr, uid, [('name', 'ilike', name_pts), ('slot_id', '=', slot_ids[0])])
            if pts_ids:
                pts_id = delivery_pool.read(cr, uid, [pts_ids[0]], ['name','id'])[0]
                pts_id = pts_id['id'],pts_id['name']
                shop_ids = self.pool.get('sale.shop').search(cr, uid, [])
                if shop_ids:
                    shop_id = self.pool.get('sale.shop').read(cr, uid, [shop_ids[0]], ['name','id'])[0]
                    shop_id = shop_id['id'],shop_id['name']
                    #LY 0515
                    cr.execute('SELECT running FROM delivery_scheduler_running')
                    if cr.fetchone()[0]:
                        # add stop thread maybe.
                        logger.info('>>>>>>>>>> ######## CRON for Preparation Scheduler PTS %s FAILED- Scheduler Already Running ######## <<<<<<<<<<' % (slot_start))
                        raise osv.except_osv(_('Error'), _('the Preparation Scheduler is already RUNNING !'))
                    else:
                        #LY END
                        self.run_big_scheduler(cr, uid, automatic=True, use_new_cursor=cr.dbname, run_check=True, cancel_mo=True, auto_mo=True, pts_id=pts_id, shop_id=shop_id, context=context)
                else:
                    logger.info('>>>>>>>>>> ######## CRON for Preparation Scheduler PTS %s - No shop found ######## <<<<<<<<<<' % (slot_start))
            else:
                logger.info('>>>>>>>>>> ######## CRON for Preparation Scheduler PTS %s - No PTS found for this slot today ######## <<<<<<<<<<' % (slot_start))
        else:
            logger.info('>>>>>>>>>> ######## CRON for Preparation Scheduler PTS %s - No such slot ######## <<<<<<<<<<' % (slot_start))
    
    

    def run_big_scheduler(self, cr, uid, automatic=False, use_new_cursor=False, run_check=False, cancel_mo=True, auto_mo=False, pts_id=False, shop_id=False, context=None):
        #move cursor outside if for closed cursor issue
        #logger.debug('>>>>>>>>>>>>>>> #LY scheduler thread start 2 in run_big_scheduler <<<<<<<<<<<<<<<')
        cr2 = pooler.get_db(cr.dbname).cursor()
        if use_new_cursor:
            cr = pooler.get_db(use_new_cursor).cursor()
        cr.execute('SELECT running FROM delivery_scheduler_running')
        if cr.fetchone()[0]:
            logger.warning('>>>>>>>>>> ######## /!\ Preparation Scheduler already RUNNING /!\ ######## <<<<<<<<<<')
        else:
            mess_pool  = self.pool.get('mail.message')
            type_pool  = self.pool.get('product.stock_type')
            prdt_pool  = self.pool.get('product.product')
            mo_pool    = self.pool.get('mrp.production')
            pick_pool  = self.pool.get('stock.picking')
            move_pool  = self.pool.get('stock.move')
            shop_pool  = self.pool.get('sale.shop')
            wf_service = netsvc.LocalService("workflow")
            tz = pytz.timezone('Asia/Shanghai')
            
            
            
            partner_ids = [uid]
            if uid != 1:
                partner_ids.append(1)
            
            
            #logger.info( "======== 1111 time : %s"%(datetime.now()))
            #logger.info(" ======== 1111datetime : %s"%(pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')))
            logger.info('>>>>>>>>>> ########  Scheduler START ######## <<<<<<<<<<')
            cr.execute('UPDATE delivery_scheduler_running SET running=TRUE')
            cr.commit()
            header = '<p>Scheduler has started at ' + pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S') + ' with options:<br />'
            header += 'Shop : ' + str(shop_id and shop_id[1] or False) + '<br />'
            header += 'Preparation Time : ' + str(pts_id and pts_id[1] or False) + '<br />'
            header += 'Automatic Order Points ? ' + str(automatic) + '<br />'
            header += 'Check Picking Availability ? ' + str(run_check) + '<br />'
            header += 'Validate Automatic MO ? ' + str(auto_mo) + '</p>'
            body = ''
            
            message_id = mess_pool.create(cr, uid, {
                'type': 'comment',
                'partner_ids': partner_ids,
                'subject': 'Scheduler started at ' + pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M'),
                'body': header,
                'subtype_id': 1,
                'res_id': self._get_warehouse_group(cr, uid),
                'model': 'mail.group',
                'record_name': 'Preparation Scheduler',
            })
            cr.commit()
            
            pts_id = pts_id and pts_id[0] or False 
            shop_id = shop_id and shop_id[0] or False
            
            try:
                self._procure_confirm(cr, uid, use_new_cursor=use_new_cursor, context=context)
                body = '<p>Procurements have been confirmed at ' + pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S') + '</p>' + body
                mess_pool.write(cr, 1, message_id, {'body': header + body, })
                cr.commit()
                
                if not pts_id:# Purchase Orders
                    self._procure_orderpoint_confirm(cr, uid, automatic=automatic, use_new_cursor=use_new_cursor, context=context)
                    body = '<p>Orderpoints have been confirmed at ' + pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S') + '</p>' + body
                    mess_pool.write(cr, 1, message_id, {'body': header + body, })
                    cr.commit()
                
                    # Delete all MOs created by the Scheduler and with no pts_id
                    if cancel_mo:
                        mo_ids = mo_pool.search(cr2, uid, [('state', 'not in', ['cancel', 'done']), ('pts_id', '=', False), ('origin', '=', 'SCHEDULER')]) or []
                        for mo in mo_pool.read(cr2, uid, mo_ids, ['name','picking_id','move_prod_id']):
                            try:
                                if mo['picking_id'] and mo['picking_id'][0]:
                                    pick_pool.action_cancel(cr2, uid, [mo['picking_id'][0]], context=context)
                                    cr2.commit()
                                if mo['move_prod_id'] and mo['move_prod_id'][0]:
                                    move_pool.action_cancel(cr2, uid, [mo['move_prod_id'][0]], context=context)
                                    cr2.commit()
                                wf_service.trg_validate(uid, 'mrp.production', mo['id'], 'button_cancel', cr2)
                            except Exception as err:
                                logger.info('>>> Error during Canceling MO %s : %s' % (mo['name'], err))
                        cr2.commit()
                        logger.info('>>>>>>>>>>>>>>> CANCELING MO DONE <<<<<<<<<<<<<<<')
                        body = '<p>Generated Manufacturing Orders have been canceled at ' + pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S') + '</p>' + body
                        mess_pool.write(cr, 1, message_id, {'body': header + body, })
                
                else:# Manufacturing Orders
                    bom_obj = self.pool.get('mrp.bom')
                    shop = shop_pool.browse(cr, uid, shop_id, context=context)
        
                    pdt_ids = prdt_pool.search(cr, uid, [('supply_method', '=', 'produce')], context=context)
                    pdt_ids.append(0)
                    pdt_ids = str(pdt_ids).replace('[', '(').replace(']', ')')
                    cr.execute("SELECT distinct(product_id) FROM procurement_order WHERE state='exception' AND pts_id = %s AND product_id IN %s" % (pts_id, pdt_ids))
                    products_ids = map(lambda x: x[0], cr.fetchall())
                    for product in prdt_pool.browse(cr, uid, products_ids, context=context):
                        try:
                            stock_available = 0
                            cr.execute("SELECT coalesce(sum(p.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as product_qty FROM procurement_order p LEFT JOIN product_product pp ON (p.product_id=pp.id) LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id) LEFT JOIN product_uom pu ON (pt.uom_id=pu.id) LEFT JOIN product_uom pu2 ON (p.product_uom=pu2.id) WHERE p.location_id=%s AND p.product_id=%s AND p.state='exception' AND p.pts_id=%s" % (shop.warehouse_id.lot_stock_id.id, product.id, pts_id))
                            result = cr.fetchone()
                            cr.execute("SELECT coalesce(sum(p.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as product_qty FROM mrp_production p LEFT JOIN product_product pp ON (p.product_id=pp.id) LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id) LEFT JOIN product_uom pu ON (pt.uom_id=pu.id) LEFT JOIN product_uom pu2 ON (p.product_uom=pu2.id) WHERE p.product_id=%s AND p.state NOT IN ('draft','cancel','done') AND p.pts_id=%s" % (product.id, pts_id))
                            result2 = cr.fetchone()
                            stock_available = result2[0] - result[0]
                            
                            #print ">>>>>>>>>> stock in MO product%s, quantity %s - %s"% (product.default_code,result2[0], result[0])
                            
                            if stock_available >= 0.0:
                                continue
                            stock_available = (math.ceil(stock_available / product.uom_id.rounding)) * product.uom_id.rounding
                            mpq = -1 * (math.ceil(product.mpq / product.uom_id.rounding)) * product.uom_id.rounding
                            stock_available = min(stock_available, mpq)
                            
                            if product.supply_method == 'produce':
                                location_id = shop.warehouse_id.lot_stock_id.id
                            else:
                                continue
                            routing_id = False
                            bom_id = bom_obj._bom_find(cr, uid, product.id, product.uom_id and product.uom_id.id, [])
                            if bom_id:
                                bom_point = bom_obj.read(cr, uid, [bom_id], ['routing_id'], context=context)[0]
                                routing_id = bom_point['routing_id'] and bom_point['routing_id'][0] or False
                            
                            mo_id = mo_pool.create(cr, uid, {
                                'origin': 'MO SCHEDULER',
                                'product_id': product.id,
                                'product_qty':-stock_available,
                                'product_uom': product.uom_id.id,
                                'pts_id': pts_id,
                                'date_planned': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'location_src_id': shop.warehouse_id.lot_stock_id.id,
                                'location_dest_id': shop.warehouse_id.lot_stock_id.id,
                                'company_id': shop.company_id.id,
                                'bom_id': bom_id,
                                'routing_id': routing_id,
                            }, context=context)
                            wf_service.trg_validate(uid, 'mrp.production', mo_id, 'button_confirm', cr)
                            cr.commit()
                        except Exception as err:
                            logger.warning('######### /!\ MO generation for product %s : %s \t(lock ?) /!\ '%(product.id,err))
                    logger.info('>>>>>>>>>>>>>>> MO GENERATION DONE <<<<<<<<<<<<<<<')
                    body = '<p>Manufacturing Orders have been generated at ' + pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S') + '</p>' + body
                    mess_pool.write(cr, 1, message_id, {'body': header + body, })
                    cr.commit()
                
                
                if auto_mo:
                    shop_ids = shop_id and [shop_id] or shop_pool.search(cr, uid, [])
                    self.pool.get('mrp.production.scheduler')._mrp_production_calculation_all(cr, uid, shop_ids, pts_id, context=context)
                    logger.info('>>>>>>>>>>>>>>> MOs CONFIRMED <<<<<<<<<<<<<<<')
                    body = '<p>Auto MOs have been confirmed at ' + pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S') + '</p>' + body
                    mess_pool.write(cr, 1, message_id, {'body': header + body, })
                    cr.commit()
                
                
                ###############################
                ## 2-step moves in warehouse ##
                ###############################
#                try:
#                    pts  = self.pool.get('delivery.time').browse(cr, uid, pts_id)
#                    shop = shop_pool.browse(cr, uid, shop_id)
#                    lot_out   = shop.warehouse_id.lot_output_id.id
#                    lot_stock = shop.warehouse_id.lot_stock_id.id
#                    
#                    # Get Stock Type
#                    type_ids = type_pool.search(cr, uid, [])
#                    type_ids.append(False) #For product with no stock_type_id defined
#                    for stock_type_id in type_ids:
#                        if stock_type_id:
#                            stock_type_name = type_pool.read(cr, uid, [stock_type_id], ['name'])[0]['name']
#                        else:
#                            stock_type_name = 'Unknown Type'
#                        # Get Move ids for this Stock Type, this PTS which and this OUT location
#                        move_ids = move_pool.search(cr, uid, [('product_id.stock_type_id','=',stock_type_id),('location_id','=',lot_out),('pts_id','=',pts_id)])
#                        if move_ids:
#                            # Create Picking for this Stock Type, this PTS which and this OUT location
#                            pick_id = pick_pool.create(cr, uid, {'origin': 'PS:' + stock_type_name, 
#                                                                 #'location_id': lot_stock, 'location_dest_id': lot_out,
#                                                                 'partner_id': False, 'type': 'internal',
#                                                                 'pts_id': pts_id, 'dts_id': pts and pts.dts_id and pts.dts_id.id or False,})
#                            cr.commit()
#                            
#                            # Amongst those moves, group by Product than UoM (which actually should be the same)
#                            cr.execute('SELECT product_id as product_id, product_uom as product_uom, sum(product_qty) as product_qty FROM stock_move WHERE id IN %s GROUP BY product_id, product_uom', (tuple(move_ids),))
#                            for grouped_move in cr.fetchall():
#                                product_name = prdt_pool.read(cr, uid, [grouped_move[0]], ['name'])[0]['name']
#                                move_pool.create(cr, uid, {'name': product_name, 'origin': 'PS:' + stock_type_name, 
#                                                         'location_id': lot_stock, 'location_dest_id': lot_out,
#                                                         'picking_id': pick_id, 'partner_id': False,
#                                                         'pts_id': pts_id, 'dts_id': pts and pts.dts_id and pts.dts_id.id or False,
#                                                         'product_id': grouped_move[0], 'product_uom': grouped_move[1], 'product_qty': grouped_move[2],})
#                            cr.commit()
#                    
#                    logger.info('>>>>>>>>>>>>>>> Preparation Pickings CREATED <<<<<<<<<<<<<<<')
#                    body = '<p>Preparation Pickings have been created at ' + pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S') + '</p>' + body
#                    mess_pool.write(cr, 1, message_id, {'body': header + body, })
#                    cr.commit()
#                except Exception as err:
#                    logger.error('>>>>>>>>>>>>>>> Preparation Pickings FAILED: %s <<<<<<<<<<<<<<<'%(err))
                ###############################
                
#                #VERSION USING MOVES
#                if False and run_check:
#                    moves_pool = self.pool.get('stock.move')
##                    if shop_id:
##                        shop = shop_pool.browse(cr, uid, shop_id, context=context)
##                        loc_ids = [shop.warehouse_id.lot_output_id.id]
##                    else:
##                        loc_ids  = [0]
##                        shop_ids = shop_pool.search(cr, uid, [], context=context)
##                        for shop in shop_pool.browse(cr, uid, shop_ids, context=context):
##                            loc_ids.append(shop.warehouse_id.lot_output_id.id)
#                    
#                    if pts_id:
#                        cr.execute("SELECT DISTINCT m.id FROM stock_move m LEFT JOIN stock_picking p ON m.picking_id=p.id LEFT JOIN stock_location l ON m.location_dest_id=l.id WHERE m.pts_id=%s AND m.product_supply_method IN ('M','A') AND m.state NOT IN ('cancel', 'done') AND ((m.picking_id IS NULL AND l.usage='customer') OR (m.picking_id IS NOT NULL AND p.type='out'))",(pts_id,))
#                    else:
#                        cr.execute("SELECT DISTINCT m.id FROM stock_move m LEFT JOIN stock_picking p ON m.picking_id=p.id LEFT JOIN stock_location l ON m.location_dest_id=l.id WHERE m.product_supply_method IN ('M','A') AND m.state NOT IN ('cancel', 'done') AND ((m.picking_id IS NULL AND l.usage='customer') OR (m.picking_id IS NOT NULL AND p.type='out'))")
#                    move_ids = map(lambda x: x[0], cr.fetchall()) or []
#                    cpt = 0
#                    for move_id in move_ids:
#                        try:
#                            moves_pool.action_assign(cr, uid, [move_id])
#                            cr.commit()
#                        except Exception as err:
#                            logger.warning('######### /!\ Availability for Move %s : %s \t(lock ?) /!\ '%(move_id,err))
#                            pass
#                        cpt += 1
#                        if cpt >= 20:
#                            cpt=0
#                            cr.commit()
#                    logger.info('>>>>>>>>>>>>>>> Check Availability Moves DONE <<<<<<<<<<<<<<<')
#                    body = '<p>Check Availability on Moves has been done at ' + pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S') + '</p>' + body
#                    mess_pool.write(cr, 1, message_id, {'body': header + body, })
#                    cr.commit()
                
                
                #VERSION USING PICKINGS
                if run_check:
                    picking_pool = self.pool.get('stock.picking')
                    args = [('state', 'not in', ['cancel', 'done'])]#LY assigned
                    if pts_id:
                        args.append(('pts_id', '=', pts_id))
                    picking_ids = picking_pool.search(cr, uid, args, context=context) or []
                    for picking_id in picking_ids:
                        try:
                            picking_pool.action_assign(cr, uid, [picking_id])
                            cr.commit()
                        except Exception as err:
                            logger.warning('######### /!\ Availability with pts_id %s for Picking %s : %s \t(lock ?) /!\ '%(pts_id, picking_id,err))
                            pass
                    logger.info('>>>>>>>>>>>>>>> Check Availability Picking DONE <<<<<<<<<<<<<<<')
                    body = '<p>Check Availability on Picking has been done at ' + pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S') + '</p>' + body
                    mess_pool.write(cr, 1, message_id, {'body': header + body, })
                
                
                logger.info('>>>>>>>>>> ########  Scheduler DONE ######## <<<<<<<<<<')
                body = '<p>Scheduler finished at ' + pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S') + '</p>' + body
                mess_pool.write(cr, 1, message_id, {'body': header + body, })
                cr.execute('UPDATE delivery_scheduler_running SET running=FALSE')
                #move cursor to outside
            except Exception as err:
                cr2.execute('UPDATE delivery_scheduler_running SET running=FALSE')
                logger.error('>>>>>>>>>> ########  Scheduler FAILED: %s ######## <<<<<<<<<<'%(err))
                body = '<p>Scheduler FAILED at ' + pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S') + '</p>' + body
                mess_pool.write(cr, 1, message_id, {'body': header + body, })
        #logger.debug('>>>>>>>>>>>>>>> #LY scheduler 2.2 end run_big_scheduler <<<<<<<<<<<<<<<')
        if use_new_cursor:
            cr.commit()
            cr.close()
        cr2.commit()
        cr2.close()
    
    
    def _procure_confirm(self, cr, uid, ids=None, use_new_cursor=False, context=None):
        '''
        Call the scheduler to check the procurement order

        @param self: The object pointer
        @param cr: The current row, from the database cursor,
        @param uid: The current user ID for security checks
        @param ids: List of selected IDs
        @param use_new_cursor: False or the dbname
        @param context: A standard dictionary for contextual values
        @return:  Dictionary of values
        '''
        if context is None:
            context = {}
        pts_id = context.get('force_pts_id', False)
        try:
            if use_new_cursor:
                cr = pooler.get_db(use_new_cursor).cursor()
            wf_service = netsvc.LocalService("workflow")
            procurement_obj = self.pool.get('procurement.order')
            
            if pts_id:
                product_ids = self.pool.get('product.product').search(cr, uid, [('supply_method', '=', 'produce')])
            
            if not ids:
                args = [('state', '=', 'exception')]
                if pts_id:
                    args.extend([('pts_id', '=', pts_id), ('product_id', 'in', product_ids)])
                ids = procurement_obj.search(cr, uid, args, order="date_planned")
            for id in ids:
                wf_service.trg_validate(uid, 'procurement.order', id, 'button_restart', cr)
            if use_new_cursor:
                cr.commit()
            company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
            maxdate = (datetime.today() + relativedelta(days=company.schedule_range)).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
#            start_date = fields.datetime.now()
            offset = 0
#            report = []
#            report_total = 0
#            report_except = 0
#            report_later = 0
            while True:
                args = [('state', '=', 'confirmed'), ('procure_method', '=', 'make_to_order')]
                if pts_id:
                    args.extend([('pts_id', '=', pts_id), ('product_id', 'in', product_ids)])
                ids = procurement_obj.search(cr, uid, args, offset=offset, limit=500, order='priority, date_planned', context=context)
                for proc in procurement_obj.browse(cr, uid, ids, context=context):
                    if maxdate >= proc.date_planned:
                        wf_service.trg_validate(uid, 'procurement.order', proc.id, 'button_check', cr)
                    else:
                        offset += 1
#                        report_later += 1
#
#                    if proc.state == 'exception':
#                        report.append(_('PROC %d: on order - %3.2f %-5s - %s') % (proc.id, proc.product_qty, proc.product_uom.name, proc.product_id.name))
#                        report_except += 1
#                    report_total += 1
                if use_new_cursor:
                    cr.commit()
                if not ids:
                    break
            offset = 0
            ids = []
            while True:
#                report_ids = []
                args = [('state', '=', 'confirmed'), ('procure_method', '=', 'make_to_stock')]
                if pts_id:
                    args.extend([('pts_id', '=', pts_id), ('product_id', 'in', product_ids)])
                ids = procurement_obj.search(cr, uid, args, offset=offset)
                for proc in procurement_obj.browse(cr, uid, ids):
                    if maxdate >= proc.date_planned:
                        wf_service.trg_validate(uid, 'procurement.order', proc.id, 'button_check', cr)
#                        report_ids.append(proc.id)
#                    else:
#                        report_later += 1
#                    report_total += 1
#
#                    if proc.state == 'exception':
#                        report.append(_('PROC %d: from stock - %3.2f %-5s - %s') % (proc.id, proc.product_qty, proc.product_uom.name, proc.product_id.name,))
#                        report_except += 1

                if use_new_cursor:
                    cr.commit()
                offset += len(ids)
                if not ids: break
#            end_date = fields.datetime.now()

            if use_new_cursor:
                cr.commit()
        except Exception as err:
            logger.warning('######### /!\ Proc Confirm : %s \t(lock ?) /!\ '%(err))
        finally:
            if use_new_cursor:
                try:
                    cr.close()
                except Exception:
                    pass
        logger.info('>>>>>>>>>>>>>>> PROCURE Confirm DONE <<<<<<<<<<<<<<<')
        return {}


    def _prepare_automatic_op_procurement(self, cr, uid, product, warehouse, location_id, product_qty, context=None):
        return {'name': _('Automatic OP: %s') % (product.name,),
                'origin': _('SCHEDULER'),
                'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'product_id': product.id,
                'product_qty':-product_qty,
                'product_uom': product.uom_id.id,
                'location_id': location_id,
                'pts_id': context and context.get('force_pts_id', False) or False,
                'company_id': warehouse.company_id.id,
                'procure_method': 'make_to_order', }


    def _prepare_orderpoint_procurement(self, cr, uid, orderpoint, product_qty, context=None):
        return {'name': orderpoint.name,
                'date_planned': self._get_orderpoint_date_planned(cr, uid, orderpoint, datetime.today(), context=context),
                'product_id': orderpoint.product_id.id,
                'product_qty': product_qty,
                'company_id': orderpoint.company_id.id,
                'product_uom': orderpoint.product_uom.id,
                'location_id': orderpoint.location_id.id,
                'pts_id': context and context.get('force_pts_id', False) or False,
                'procure_method': 'make_to_order',
                'origin': orderpoint.name}


    def create_automatic_op(self, cr, uid, context=None):
        """
        Create procurement of  virtual stock < 0

        @param self: The object pointer
        @param cr: The current row, from the database cursor,
        @param uid: The current user ID for security checks
        @param context: A standard dictionary for contextual values
        @return:  Dictionary of values
        """
        if context is None:
            context = {}
        pts_id = context.get('force_pts_id', False)
        product_obj = self.pool.get('product.product')
        proc_obj = self.pool.get('procurement.order')
        warehouse_obj = self.pool.get('stock.warehouse')
        wf_service = netsvc.LocalService("workflow")

        warehouse_ids = warehouse_obj.search(cr, uid, [], context=context)
        if pts_id:
            pdt_ids = product_obj.search(cr, uid, [('supply_method', '=', 'produce')], context=context)
            pdt_ids.append(0)
            pdt_ids = str(pdt_ids).replace('[', '(').replace(']', ')')
            cr.execute("SELECT distinct(product_id) FROM procurement_order WHERE state='exception' AND pts_id = %s AND product_id IN %s" % (pts_id, pdt_ids))
            products_ids = map(lambda x: x[0], cr.fetchall())
        else:
            products_ids = product_obj.search(cr, uid, ['|', ('purchase_ok', '=', True), ('supply_method', '=', 'produce')], context=context)

        for warehouse in warehouse_obj.browse(cr, uid, warehouse_ids, context=context):
            context['warehouse'] = warehouse
            if not pts_id:
                # Here we check products availability.
                # We use the method 'read' for performance reasons, because using the method 'browse' may crash the server.
                for product_read in product_obj.read(cr, uid, products_ids, ['virtual_available'], context=context):
                    try:
                        if product_read['virtual_available'] >= 0.0:
                            continue
        
                        product = product_obj.browse(cr, uid, [product_read['id']], context=context)[0]
                        if product.supply_method == 'buy':
                            location_id = warehouse.lot_input_id.id
                        elif product.supply_method == 'produce':
                            location_id = warehouse.lot_stock_id.id
                        else:
                            continue                    
                        proc_id = proc_obj.create(cr, uid, self._prepare_automatic_op_procurement(cr, uid, product, warehouse, location_id, product_read['virtual_available'], context=context), context=context)
                        wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)
                        #if not context.get('no_po', False) or product.supply_method == 'produce':
                        wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_check', cr)
                    except Exception as err:
                        logger.warning('######### /!\ OE Automatic OP for product %s : %s \t(lock ?) /!\ '%(product.id,err))
            else:
                for product in product_obj.browse(cr, uid, products_ids, context=context):
                    try:
                        stock_available = 0
    
                        cr.execute("SELECT coalesce(sum(p.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as product_qty FROM procurement_order p LEFT JOIN product_product pp ON (p.product_id=pp.id) LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id) LEFT JOIN product_uom pu ON (pt.uom_id=pu.id) LEFT JOIN product_uom pu2 ON (p.product_uom=pu2.id) WHERE p.location_id=%s AND p.product_id=%s AND p.state='exception' AND p.pts_id=%s" % (warehouse.lot_stock_id.id, product.id, pts_id))
                        result = cr.fetchone()
                        cr.execute("SELECT coalesce(sum(p.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as product_qty FROM mrp_production p LEFT JOIN product_product pp ON (p.product_id=pp.id) LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id) LEFT JOIN product_uom pu ON (pt.uom_id=pu.id) LEFT JOIN product_uom pu2 ON (p.product_uom=pu2.id) WHERE p.product_id=%s AND p.state NOT IN ('draft','cancel','done') AND p.pts_id=%s" % (product.id, pts_id))
                        result2 = cr.fetchone()
                        stock_available = result2[0] - result[0]                    
                        if stock_available >= 0.0:
                            continue
                        stock_available = (math.ceil(stock_available / product.uom_id.rounding)) * product.uom_id.rounding
                        
                        if product.supply_method == 'buy':
                            location_id = warehouse.lot_input_id.id
                        elif product.supply_method == 'produce':
                            location_id = warehouse.lot_stock_id.id
                        else:
                            continue
                        proc_id = proc_obj.create(cr, uid, self._prepare_automatic_op_procurement(cr, uid, product, warehouse, location_id, stock_available, context=context), context=context)
                        wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)
                        #if product.supply_method == 'produce':
                        wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_check', cr)
                    except Exception as err:
                        logger.warning('######### /!\ Automatic OP for product %s : %s \t(lock ?) /!\ '%(product.id,err))
        return True
    
    
    def _procure_orderpoint_confirm(self, cr, uid, automatic=False, use_new_cursor=False, context=None, user_id=False):
        '''
        Create procurement based on Orderpoint
        use_new_cursor: False or the dbname

        @param self: The object pointer
        @param cr: The current row, from the database cursor,
        @param user_id: The current user ID for security checks
        @param context: A standard dictionary for contextual values
        @param param: False or the dbname
        @return:  Dictionary of values
        '''
        if context is None:
            context = {}
        if use_new_cursor:
            cr = pooler.get_db(use_new_cursor).cursor()
        orderpoint_obj = self.pool.get('stock.warehouse.orderpoint')
        
        procurement_obj = self.pool.get('procurement.order')
        wf_service = netsvc.LocalService("workflow")
        offset = 0
        ids = [1]
        if automatic:
            self.create_automatic_op(cr, uid, context=context)
            logger.info('>>>>>>>>>>>>>>> create_automatic_op DONE <<<<<<<<<<<<<<<')
        while ids:
            ids = orderpoint_obj.search(cr, uid, [], offset=offset, limit=100)
            for op in orderpoint_obj.browse(cr, uid, ids, context=context):
                prods = self._product_virtual_get(cr, uid, op)
                if prods is None:
                    continue
                if prods < op.product_min_qty:
                    qty = max(op.product_min_qty, op.product_max_qty) - prods

                    reste = qty % op.qty_multiple
                    if reste > 0:
                        qty += op.qty_multiple - reste

                    if qty <= 0:
                        continue
                    if op.product_id.type not in ('consu'):
                        if op.procurement_draft_ids:
                        # Check draft procurement related to this order point
                            pro_ids = [x.id for x in op.procurement_draft_ids]
                            procure_datas = procurement_obj.read(cr, uid, pro_ids, ['id', 'product_qty'], context=context)
                            to_generate = qty
                            for proc_data in procure_datas:
                                if to_generate >= proc_data['product_qty']:
                                    wf_service.trg_validate(uid, 'procurement.order', proc_data['id'], 'button_confirm', cr)
                                    procurement_obj.write(cr, uid, [proc_data['id']], {'origin': op.name}, context=context)
                                    to_generate -= proc_data['product_qty']
                                if not to_generate:
                                    break
                            qty = to_generate

                    if qty:
                        proc_id = procurement_obj.create(cr, uid, self._prepare_orderpoint_procurement(cr, uid, op, qty, context=context), context=context)
                        wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)
                        wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_check', cr)
                        orderpoint_obj.write(cr, uid, [op.id], {'procurement_id': proc_id}, context=context)
            offset += len(ids)
            if use_new_cursor:
                cr.commit()
        if use_new_cursor:
            cr.commit()
            cr.close()
        logger.info('>>>>>>>>>>>>>>> ORDER POINT Confirm DONE <<<<<<<<<<<<<<<')
        return {}

procurement_order()


class procurement_compute_all(osv.osv_memory):
    _inherit = 'procurement.order.compute.all'
    _name = 'procurement.order.compute.all'

    _columns = {
        'cancel_mo': fields.boolean('Cancel generated MO ?'),
    }

    _defaults = {
         'cancel_mo': lambda *a: True,
    }

    def _procure_calculation_all(self, cr, uid, ids, context=None):
        """
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        """
        proc_obj = self.pool.get('procurement.order')
        #As this function is in a new thread, i need to open a new cursor, because the old one may be closed
        new_cr = pooler.get_db(cr.dbname).cursor()
        for proc in self.browse(new_cr, uid, ids, context=context):
            proc_obj.run_scheduler(new_cr, uid, automatic=proc.automatic, use_new_cursor=new_cr.dbname, cancel_mo=proc.cancel_mo, context=context)
        #close the new cursor
        new_cr.close()
        return {}

#    def procure_calculation(self, cr, uid, ids, context=None):
#        """
#        @param self: The object pointer.
#        @param cr: A database cursor
#        @param uid: ID of the user currently logged in
#        @param ids: List of IDs selected
#        @param context: A standard dictionary
#        """
#        threaded_calculation = threading.Thread(target=self._procure_calculation_all, name='procure_calculation', args=(cr, uid, ids, context))
#        threaded_calculation.start()
#        return {'type': 'ir.actions.act_window_close'}

procurement_compute_all()


class big_scheduler(osv.osv_memory):
    _name = 'big_scheduler'
    _description = ' Big scheduler'

    def _init_pts_id(self, cr, uid, context=None):
        now = datetime.now()
        ids = self.pool.get('delivery.time').search(cr, uid, [('type', '=', 'pts'), ('active', '=', True), ('name', 'ilike', datetime.strftime(now, '%y%m%d') + '%')])
        return ids and ids[0] or False

    _columns = {
        'automatic': fields.boolean('Automatic Order Points?', help="Create procurement of virtual stock < 0"),
        'run_check': fields.boolean('Check Picking Availability?'),
        'po_merge':  fields.boolean('Merge PO?'),
        'auto_mo':   fields.boolean('Validate Automatic MO ?'),
        'pts_id':    fields.many2one('delivery.time', 'Preparation Time', select=True, domain=[('type', '=', 'pts'), ('active', '=', True)], required=True),
        'shop_id':   fields.many2one('sale.shop', 'Shop', required=True),
    }
    _defaults = {
        'automatic': lambda *a: True,
        'run_check': lambda *a: True,
        'po_merge':  lambda *a: True,
        'auto_mo':   lambda *a: True,
        'pts_id':    lambda self, cr, uid, context: self._init_pts_id(cr, uid, context=context),
        'shop_id':   lambda *a: 1,
    }
    
    def run_scheduler(self, cr, uid, ids, context=None):
        #logger.info('>>>>>>>>>>>>>>> #LY scheduler button clicked <<<<<<<<<<<<<<<')
        context = context or {}
        use_new_cursor = cr.dbname
        datas = self.read(cr, uid, ids, context=context)
        for data in datas:
            pts_id = data['pts_id'] or False
            shop_id = data['shop_id'] or False
            automatic = data['automatic'] or False
            po_merge = data['po_merge'] or False
            run_check = data['run_check'] or False
            auto_mo = data['auto_mo'] or False
        if pts_id:
            context.update({'force_pts_id':pts_id[0]})
        
        cr.execute('SELECT running FROM delivery_scheduler_running')
        if cr.fetchone()[0]:
            raise osv.except_osv(_('Error'), _('the Preparation Scheduler is already RUNNING !'))
        else:
            cancel_mo = True
            threaded_calculation = threading.Thread(target=self.pool.get('procurement.order').run_big_scheduler, name='prep_scheduler', args=(cr, uid, automatic, use_new_cursor, run_check, cancel_mo, auto_mo, pts_id, shop_id, context))
            threaded_calculation.start()
            #logger.debug('>>>>>>>>>>>>>>> #LY scheduler thread start 1 <<<<<<<<<<<<<<<')
        return {'type': 'ir.actions.act_window_close'}
    
big_scheduler()


class stock_picking_check_availability(osv.osv_memory):
    _name = 'stock.picking.check_availability'
    _description = 'Stock Picking Check Availability Batch'

    def _init_pts_id(self, cr, uid, context=None):
        now = datetime.now()
        ids = self.pool.get('delivery.time').search(cr, uid, [('type', '=', 'pts'), ('active', '=', True), ('name', 'ilike', datetime.strftime(now, '%y%m%d') + '%')])
        return ids and ids[0] or False

    _columns = {
        'pts_id': fields.many2one('delivery.time', 'Preparation Time', select=True, domain=[('type', '=', 'pts'), ('active', '=', True)]),
    }
    _defaults = {
        'pts_id': lambda self, cr, uid, context: self._init_pts_id(cr, uid, context=context),
    }
    
    def run_scheduler(self, cr, uid, ids, context=None):
        context = context or {}
        picking_pool = self.pool.get('stock.picking')
        datas = self.read(cr, uid, ids, context=context)
        for data in datas:
            pts_id = data['pts_id'] and data['pts_id'][0] or False
            args = [('state', 'not in', ['cancel', 'done'])]
            if pts_id:
                args.append(('pts_id', '=', pts_id))
            picking_ids = picking_pool.search(cr, uid, args, context=context) or []
            for picking_id in picking_ids:
                try:
                    picking_pool.action_assign(cr, uid, [picking_id])
                    cr.commit()
                except Exception as err:
                    pass
        
        return {'type': 'ir.actions.act_window_close'}
    
stock_picking_check_availability()


class big_scheduler_stop(osv.osv_memory):
    _name = 'big_scheduler.stop'
    _description = 'Stop/Kill  Big scheduler'

    _columns = {
        'action': fields.selection([('stop','Stop'),('kill','Kill')], 'Action', required=True),
    }
    _defaults = {
        'action': 'stop',
    }
    
    def stop_scheduler(self, cr, uid, ids, context=None):
        context = context or {}
        datas = self.read(cr, uid, ids, context=context)
        for data in datas:
            if data['action'] == 'stop':
                cr.execute('UPDATE delivery_scheduler_running SET running=FALSE')
            else:
                for scheduler in threading.enumerate():
                    if scheduler.isAlive() and scheduler.getName()=='prep_scheduler':
                        try:
                            scheduler._Thread__stop()
                        except:
                            logger.warning(str(scheduler.getName()) + ' could not be terminated')
                cr.execute('UPDATE delivery_scheduler_running SET running=FALSE')
        
        return {'type': 'ir.actions.act_window_close'}
    
big_scheduler_stop()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
