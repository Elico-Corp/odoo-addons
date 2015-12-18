# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, tools


class SaleReportCost(models.Model):
    _inherit = "sale.report"

    total_cost = fields.Float(string="Total Cost")

    def _select(self):
        select_str = """
             SELECT min(l.id) as id,
                    l.product_id as product_id,
                    t.uom_id as product_uom,
                    sum(l.product_uom_qty / u.factor * u2.factor)
                        as product_uom_qty,
                    sum(l.product_uom_qty * l.price_unit *
                        (100.0-l.discount) / 100.0) as price_total,
                    count(*) as nbr,
                    s.date_order as date,
                    s.date_confirm as date_confirm,
                    s.partner_id as partner_id,
                    s.user_id as user_id,
                    s.company_id as company_id,
                    extract(epoch from avg(date_trunc('day',s.date_confirm)-
                        date_trunc('day',s.create_date)))/(24*60*60)
                            ::decimal(16,2) as delay,
                    l.state,
                    t.categ_id as categ_id,
                    s.pricelist_id as pricelist_id,
                    s.project_id as analytic_account_id,
                    s.section_id as section_id,
                    i.value_float * sum(l.product_uom_qty /
                        u.factor * u2.factor) as total_cost
        """
        return select_str

    def _from(self):
        from_str = """
                sale_order_line l
                      join sale_order s on (l.order_id = s.id)
                        left join product_product p on (l.product_id = p.id)
                            left join product_template t on
                                (p.product_tmpl_id = t.id)
                    left join product_uom u on (u.id = l.product_uom)
                    left join product_uom u2 on (u2.id = t.uom_id)
                    left join (
                        select cast(substring(res_id from 18 for 10)
                            as integer) as product_template_id,
                                value_float, company_id
                                from ir_property where name = 'standard_price'
                    ) as i on (t.id = i.product_template_id and
                        s.company_id = i.company_id)
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY l.product_id,
                    l.order_id,
                    t.uom_id,
                    t.categ_id,
                    s.date_order,
                    s.date_confirm,
                    s.partner_id,
                    s.user_id,
                    s.company_id,
                    l.state,
                    s.pricelist_id,
                    s.project_id,
                    s.section_id,
                    i.value_float
        """
        return group_by_str

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s )""" % (
            self._table, self._select(), self._from(),
            self._group_by())
        )


class AccountInvoiceCost(models.Model):
    _inherit = "account.invoice.report"

    total_cost = fields.Float(string="Total Cost")

    def _select(self):
        return super(AccountInvoiceCost, self)._select() + \
            ", sub.total_cost as total_cost"

    def _sub_select(self):
        return super(AccountInvoiceCost, self)._sub_select() + \
            """, SUM(CASE
                         WHEN ai.type::text = ANY (ARRAY['out_refund'::
                                character varying::text, 'in_invoice'::
                                character varying::text])
                            THEN (- ail.quantity) / u.factor * u2.factor
                            ELSE ail.quantity / u.factor * u2.factor
                        END) *i.value_float as total_cost"""

    def _from(self):
        from_str = """
                FROM account_invoice_line ail
                JOIN account_invoice ai ON ai.id = ail.invoice_id
                JOIN res_partner partner ON
                 ai.commercial_partner_id = partner.id
                LEFT JOIN product_product pr ON pr.id = ail.product_id
                left JOIN product_template pt ON pt.id = pr.product_tmpl_id
                LEFT JOIN product_uom u ON u.id = ail.uos_id
                LEFT JOIN product_uom u2 ON u2.id = pt.uom_id
                left join (
                    select cast(substring(res_id from 18 for 10)
                        as integer) as product_template_id,
                            value_float, company_id
                            from ir_property where name = 'standard_price'
                ) as i on (pt.id = i.product_template_id and
                    i.company_id = ai.company_id)
        """
        return from_str

    def _group_by(self):
        return super(AccountInvoiceCost, self)._group_by() + ", i.value_float"

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            WITH currency_rate (currency_id, rate, date_start, date_end) AS (
                SELECT r.currency_id, r.rate, r.name AS date_start,
                    (SELECT name FROM res_currency_rate r2
                     WHERE r2.name > r.name AND
                           r2.currency_id = r.currency_id
                     ORDER BY r2.name ASC
                     LIMIT 1) AS date_end
                FROM res_currency_rate r
            )
            %s
            FROM (
                %s %s %s
            ) AS sub
            JOIN currency_rate cr ON
                (cr.currency_id = sub.currency_id AND
                 cr.date_start <= COALESCE(sub.date, NOW()) AND
                 (cr.date_end IS NULL OR cr.date_end > COALESCE(
                    sub.date, NOW())))
        )""" % (self._table,
                self._select(), self._sub_select(), self._from(),
                self._group_by()))


class PointOfSaleCost(models.Model):
    _inherit = "report.pos.order"

    total_cost = fields.Float(string="Total Cost")

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_pos_order')
        cr.execute("""
            create or replace view report_pos_order as (
                select
                    min(l.id) as id,
                    count(*) as nbr,
                    s.date_order as date,
                    sum(l.qty * u.factor) as product_qty,
                    sum(l.qty * l.price_unit) as price_total,
                    sum((l.qty * l.price_unit) * (l.discount / 100))
                        as total_discount,
                    (sum(l.qty*l.price_unit)/sum(l.qty * u.factor))::decimal
                        as average_price,
                    sum(cast(to_char(date_trunc('day',s.date_order) -
                        date_trunc('day',s.create_date),'DD') as int))
                            as delay_validation,
                    s.partner_id as partner_id,
                    s.state as state,
                    s.user_id as user_id,
                    s.location_id as location_id,
                    s.company_id as company_id,
                    s.sale_journal as journal_id,
                    l.product_id as product_id,
                    pt.categ_id as product_categ_id,
                    i.value_float * sum(l.qty * u.factor) as total_cost
                from pos_order_line as l
                    left join pos_order s on (s.id = l.order_id)
                    left join product_product p on (p.id = l.product_id)
                    left join product_template pt
                        on (pt.id = p.product_tmpl_id)
                    left join product_uom u on (u.id = pt.uom_id)
                    left join (
                        select cast(substring(res_id from 18 for 10)
                            as integer) as product_template_id, value_float,
                            company_id
                                from ir_property where name = 'standard_price'
                    ) as i on (pt.id = i.product_template_id and
                        s.company_id = i.company_id)
                group by
                    s.date_order, s.partner_id,s.state, pt.categ_id,
                    s.user_id,s.location_id,s.company_id,s.sale_journal,l.product_id,s.create_date,
                    i.value_float
                having
                    sum(l.qty * u.factor) != 0)""")
