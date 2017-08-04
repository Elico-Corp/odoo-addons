# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


import tools
from osv import fields, osv

class sale_report(osv.osv):
    _name = "sale.report2"
    _description = "Sales Orders Statistics"
    _auto = False
    _rec_name = 'date'
    _inherit = 'sale.report2'

    _columns = {
        'date': fields.date('Date Order', readonly=True),
        'date_confirm': fields.date('Date Confirm', readonly=True),
        'shipped': fields.boolean('Shipped', readonly=True),
        'shipped_qty_1': fields.integer('Shipped Qty', readonly=True),
        'year': fields.char('Year', size=4, readonly=True),
        'month': fields.selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
            ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'),
            ('10', 'October'), ('11', 'November'), ('12', 'December')], 'Month', readonly=True),
        'day': fields.char('Day', size=128, readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'uom_name': fields.char('Reference UoM', size=128, readonly=True),
        'product_uom_qty': fields.float('# of Qty', readonly=True),

        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'shop_id': fields.many2one('sale.shop', 'Shop', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'user_id': fields.many2one('res.users', 'Salesman', readonly=True),
        'price_total': fields.float('Total Price', readonly=True),
        'delay': fields.float('Commitment Delay', digits=(16,2), readonly=True),
        'categ_id': fields.many2one('product.category','Category of Product', readonly=True),
        'nbr': fields.integer('# of Lines', readonly=True),
        'file_number': fields.many2one('crm.lead','File Number',readonly=True),
        'state': fields.selection([
            ('draft', 'Quotation'),
            ('q_lost', 'Quote Lost'),
            ('q_converted', 'Quote Converted'),
            ('waiting_date', 'Waiting Schedule'),
            ('manual', 'Manual In Progress'),
            ('progress', 'In Progress'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
            ], 'Order State', readonly=True),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', readonly=True),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account', readonly=True),
        'name': fields.char('Order Reference', size=64, readonly=True),
        'currency': fields.char('Currency', size=16, readonly=True),
        'categ1_id': fields.many2one('product.category','Product Category 1', readonly=True),
        'categ2_id': fields.many2one('product.category','Product Category 2', readonly=True),
        'level1_id': fields.many2one('res.partner.category', 'Partner Level 1',readonly=True),
        'level2_id': fields.many2one('res.partner.category', 'Partner Level 2',readonly=True),
    }
    _order = 'date desc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'sale_report2')
        cr.execute("""
            create or replace view sale_report2 as (
                select el.*,
                   -- (select count(1) from sale_order_line where order_id = s.id) as nbr,
                    (select 1) as nbr,
                     s.date_order as date,
                     s.date_confirm as date_confirm,
                     to_char(s.date_order, 'YYYY') as year,
                     to_char(s.date_order, 'MM') as month,
                     to_char(s.date_order, 'YYYY-MM-DD') as day,
                     s.partner_id as partner_id,
                     s.user_id as user_id,
                     s.shop_id as shop_id,
                     s.company_id as company_id,
                     extract(epoch from avg(date_trunc('day',s.date_confirm)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
                     s.state,
                     s.file_number as file_number,
                     s.shipped,
                     s.shipped::integer as shipped_qty_1,
                     s.pricelist_id as pricelist_id,
                     s.project_id as analytic_account_id,
                     s.name,
                     c.name as currency,
                     rp.level1_id,
                     rp.level2_id
                from
                sale_order s, product_pricelist pl, res_currency c,res_partner rp,
                    (
                    select l.id as id,
                        l.product_id as product_id,
                        (case when u.uom_type not in ('reference') then
                            (select name from product_uom where uom_type='reference' and category_id=u.category_id and active LIMIT 1)
                        else
                            u.name
                        end) as uom_name,
                        sum(l.product_uom_qty * u.factor) as product_uom_qty,
                        sum(l.product_uom_qty * l.price_unit) as price_total,
                        pt.categ_id, l.order_id,
                        pt.categ1_id, pt.categ2_id
                    from
                     sale_order_line l ,product_uom u, product_product p, product_template pt 
                     where u.id = l.product_uom
                     and pt.id = p.product_tmpl_id
                     and p.id = l.product_id
                      group by l.id, l.order_id, l.product_id, u.name, pt.categ_id, u.uom_type, u.category_id, pt.categ1_id, pt.categ2_id) el
                where s.id = el.order_id
                    and rp.id=s.partner_id
                    and pl.id=s.pricelist_id
                    and c.id=pl.currency_id
                group by el.id,
                    el.product_id,
                    el.uom_name,
                    el.product_uom_qty,
                    el.price_total,
                    el.categ_id,
                    el.categ1_id,
                    el.categ2_id,
                    el.order_id,
                    s.date_order,
                    s.date_confirm,
                    s.partner_id,
                    s.user_id,
                    s.shop_id,
                    s.company_id,
                    s.state,
                    s.file_number,
                    s.shipped,
                    s.pricelist_id,
                    s.project_id,
                    s.name,
                    c.name,
                    rp.level1_id,
                    rp.level2_id
            )
        """)

