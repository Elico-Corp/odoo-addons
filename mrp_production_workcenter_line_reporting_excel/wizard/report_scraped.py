# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class Reportscraped(models.TransientModel):
    _name = 'report.scraped'

    product_product = fields.Many2many(
        'product.product', string='Product'
    )
    partner_id = fields.Many2one('res.partner', 'Customer')
    sale_order = fields.Many2one('sale.order', 'Sale order')
    start_date = fields.Date('From')
    end_date = fields.Date('To')

    # This function join the below tabels:
    #   mrp_production
    #   mrp_production_workcenter_line
    #   mrp_workcenter_line_reporting
    #   res_users
    #   mrp_workcenter
    #   resource_resource
    #   sale_order
    #
    # It returns the records of total finished qty and scraped qty for each
    # sale order under current user's company
    #
    # Example:
    # sale_id | customer_id | product_name | process_name | scraped_qty | finished_qty
    #---------+-------------+--------------+--------------+-------------+--------------
    #      13 |          75 |          188 | C1           |           1 |           99
    #      13 |          75 |          188 | A1           |          20 |          100
    #      13 |          75 |          188 | B1           |          10 |          300
    #         |             |            4 | Assemble     |         889 |         1088
    #         |             |           10 | Assemble     |           2 |          200

    def _get_res_from_sql(self):
        user_id = self._context['uid']
        select_statement = """
            select s.id as sale_id,
                s.partner_id as customer_id,
                p.id as product_name,
                rr.name as process_name,
                sum(r.finished_qty) as finished_qty,
                sum(r.scraped_qty) as scraped_qty,
                rr.code as process_code
        """

        from_statement = """
            from mrp_production mo
                join mrp_production_workcenter_line wol
                    on mo.id = wol.production_id
                left join mrp_workcenter_line_reporting r
                    on wol.id = r.workcenter_line_id
                join product_product p
                    on mo.product_id = p.id
                join res_users u
                    on u.id = %s
                join mrp_workcenter mw
                    on mw.id = wol.workcenter_id
                join resource_resource rr
                    on mw.resource_id = rr.id
                left join sale_order s
                    on position(
                        s.name || ':' in mo.origin) > 0
        """ % user_id

        where_statement = 'where mo.company_id = u.company_id'
        if self.start_date and self.end_date:
            where_statement = """
                where
                    wol.date_start >= cast('%s' as date)
                    and wol.date_start <= cast('%s' as date)
                    and mo.company_id = u.company_id
            """ % (self.start_date, self.end_date)
        elif self.start_date and not self.end_date:
            where_statement = """
                where
                    wol.date_start >= cast('%s' as date)
                    and mo.company_id = u.company_id
            """ % self.start_date
        elif not self.start_date and self.end_date:
            where_statement = """
                where
                    wol.date_start <= cast('%s' as date)
                    and mo.company_id = u.company_id
            """ % self.end_date

        group_statement = """
            group by s.id,
                 s.partner_id,
                 p.id,
                 rr.name,
                 rr.code
        """

        order_statement = """
            order by
                sale_id, product_name, process_code, process_name
        """

        psql_statement = """
            select sale_id,
                   customer_id,
                   product_name,
                   process_name,
                   scraped_qty,
                   finished_qty,
                   process_code
            from
                (%s %s %s %s) as l
            where
                finished_qty + scraped_qty > 0
            %s;
        """ % (
            select_statement, from_statement, where_statement,
            group_statement, order_statement
        )

        self._cr.execute(psql_statement)

        return self._cr.fetchall()

    def _get_workcenters_name(self):
        workcenters = sorted(
            self.env['mrp.workcenter'].search([]),
            key=lambda rec: rec['code']
        )

        return [workcenter.name for workcenter in workcenters]

    def _is_product_id_not_in_ids(self, id):
        if self.product_product:
            for product in self.product_product:
                if product.id == id:
                    return False
            return True

        return False

    def _get_product_attributes(self, res, ids):
        if not res:
            return {}

        products = self.env['product.product'].search([('id', 'in', ids)])

        vals = {}
        for product in products:
            vals[product.id] = {
                'bottom': "",
                'inside': "",
                'outside': "",
            }
            for attribue_line_id in product.attribute_line_ids:
                if attribue_line_id.attribute_id:
                    if attribue_line_id.value_ids:
                        if attribue_line_id.attribute_id.name == u'底部پایین':
                            vals[product.id]['bottom'] = \
                                attribue_line_id.value_ids.name
                        if attribue_line_id.attribute_id.name == u'内涂توو':
                            vals[product.id]['inside'] = \
                                attribue_line_id.value_ids.name
                        if attribue_line_id.attribute_id.name == u'\
                        外涂پوشش داده شده':
                            vals[product.id]['outside'] = \
                                attribue_line_id.value_ids.name
        return vals

    def _get_lines_write_excel(self):
        res = self._get_res_from_sql()
        product_ids = list(set([line[2] for line in res]))
        attributes = self._get_product_attributes(res, product_ids)

        vals = {}
        for record in res:
            name = record[0] or False
            customer = record[1] or False
            product = record[2]
            process = record[3]
            scraped_qty = record[4] or 0
            finished_qty = record[5] or 0

            if self.sale_order and self.sale_order.id != name:
                continue

            if self.partner_id and self.partner_id.id != customer:
                continue

            if self._is_product_id_not_in_ids(product):
                continue

            if name:
                name = self.env['sale.order'].browse(name).name
            else:
                name = ""

            if customer:
                customer = self.env['res.partner'].browse(customer).name
            else:
                customer = ""

            product_name = self.env['product.product'].browse(product).name

            key = str(product) + ":" + name

            if key in vals.keys():
                if process in vals[key]['process']:
                    vals[key]['quantity'] += finished_qty
                    vals[key]['scraped_qty'][process] += scraped_qty
                    vals[key]['total_scraped'] += scraped_qty
                    pencertage = round(vals[key]['total_scraped'] / (
                        vals[key]['quantity'] + vals[key]['\
                        total_scraped']) * 100, 2)
                    vals[key]['scraped_percentage'] = pencertage
                else:
                    vals[key]['quantity'] = finished_qty
                    vals[key]['process'].append(process)
                    vals[key]['scraped_qty'][process] = scraped_qty
                    vals[key]['total_scraped'] += scraped_qty
                    pencertage = round(vals[key]['total_scraped'] / (
                        finished_qty + vals[key]['total_scraped']) * 100, 2)
                    vals[key]['scraped_percentage'] = pencertage
            else:
                pencertage = round(scraped_qty / (
                    scraped_qty + finished_qty) * 100, 2)
                vals[key] = {
                    'name': name,
                    'customer': customer,
                    'product': product_name,
                    'quantity': finished_qty,
                    'process': [process],
                    'scraped_qty': {
                        process: scraped_qty
                    },
                    'total_scraped': scraped_qty,
                    'scraped_percentage': pencertage
                }

                vals[key]['bottom'] = attributes[product]['bottom']
                vals[key]['inside'] = attributes[product]['inside']
                vals[key]['outside'] = attributes[product]['outside']

        return vals

    def _get_process_len(self, vals):
        length = 0

        for key, val in vals.items():
            if len(val['process']) > length:
                length = len(val['process'])

        return length

    def _get_table_titile(self, process_len):
        # save the format in col:title
        title = {
            u'0': u"销售订单سفارش فروش",
            u'1': u"客户مشتری",
            u'2': u"产品محصول",
            u'3': u"底部پایین",
            u'4': u"内涂توو",
            u'5': u"外涂پوشش داده شده",
            u'6': u"完成数量تعداد کامل",
            u'7': u"总报废量مقدار کل ضایعات",
            u'8': u"报废率نرخ قراضه"
        }

        index = 9

        for name in self._get_workcenters_name():
            title[index] = name
            index = index + 1

        return title

    @api.multi
    def print_report(self):
        vals = self._get_lines_write_excel()
        process_len = self._get_process_len(vals)
        title = self._get_table_titile(process_len)

        datas = {
            'model': 'report.scraped',
            'title': title,
            'records': vals
        }

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'mrp.scraped.xls',
            'datas': datas
        }
