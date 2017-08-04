# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from osv import osv, fields
import openerp.addons.decimal_precision as dp
import time, pytz
from datetime import datetime


class product_template(osv.osv):
    _inherit = 'product.template'
    _name    = 'product.template'
    
    
    def _get_product_price_history(self, cr, uid, template_id, date, limit=40, context=None):
        if context is None:
            context = {}
        cr.execute("""SELECT standard_price FROM product_price_history WHERE template_id = %s AND date < '%s' ORDER BY date DESC LIMIT %s"""%(template_id, date, limit))
        return cr.fetchone()
     
    def _get_product_price(self, cr, uid, ids, name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        tz = pytz.timezone(context.get('tz','Asia/Shanghai'))
        for p in self.browse(cr, uid, ids, context=context):
            template_id = p.id
            date = pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
            prices = self._get_product_price_history(cr, uid, template_id, date )
            res[template_id] = prices and prices[0] or 0.0
        return res
    
    def _put_product_price(self, cr, uid, id, name, value, arg, context=None):
        if value:
            cr.execute("INSERT INTO product_price_history (date, template_id, standard_price) VALUES(CURRENT_TIMESTAMP at time zone 'UTC', %s, %s)" % (id, value))
            #print cr.fetchone()
        return
    
    _columns = {
        'standard_price': fields.function(_get_product_price, fnct_inv=_put_product_price, type='float', digits_compute=dp.get_precision('Product Price'), store=True
                                          ,help="Cost price of the product used for standard stock valuation in accounting and used as a base price on purchase orders.", groups="base.group_user"),
    }
    _defaults = {    
        'standard_price': 0.0,
    }
    
    def _auto_init(self, cr, context=None):
        super(product_template, self)._auto_init(cr, context=context)
        # Table with standard_price history
        cr.execute("SELECT table_name FROM information_schema.tables WHERE table_name = 'product_price_history'")
        if not cr.fetchone():
            cr.execute("""CREATE TABLE product_price_history
                        (
                          date timestamp without time zone,
                          template_id integer,
                          standard_price numeric
                        )""")
            cr.execute("""INSERT INTO product_price_history(date, template_id, standard_price) SELECT CURRENT_TIMESTAMP at time zone 'UTC', id, standard_price FROM product_template""")
        
        # DROP FUNCTION if exists
        cr.execute("""  DROP FUNCTION IF EXISTS set_product_price_history() CASCADE; """)
        cr.execute("""DROP TRIGGER IF EXISTS trigger_product_price_history on product_template CASCADE;""")
        
        # Function which update standard_price history
#         cr.execute("SELECT proname FROM pg_catalog.pg_proc WHERE proname = 'set_product_price_history'")
#         if not cr.fetchone():
#             cr.execute("""  CREATE OR REPLACE FUNCTION set_product_price_history() RETURNS TRIGGER AS $set_product_price_history$
#                             BEGIN
#                                 IF (TG_OP = 'UPDATE') THEN
#                                     INSERT INTO product_price_history VALUES(now() at time zone 'UTC' , OLD.id, NEW.standard_price);
#                                     RETURN NEW;
#                                 ELSIF (TG_OP = 'INSERT') THEN
#                                     INSERT INTO product_price_history VALUES(now() at time zone 'UTC', NEW.id, NEW.standard_price);
#                                     RETURN NEW;
#                                 END IF;
#                                 RETURN NULL;
#                             END;
#                             $set_product_price_history$ language plpgsql;""")
#         
#         # Trigger which run the function which update standard_price history
#         cr.execute("SELECT trigger_name FROM information_schema.triggers WHERE trigger_name = 'trigger_product_price_history'")
#         if not cr.fetchone():
#             cr.execute("""CREATE TRIGGER trigger_product_price_history
#                             AFTER INSERT OR UPDATE ON product_template
#                             FOR EACH ROW EXECUTE PROCEDURE set_product_price_history();""")

product_template()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
