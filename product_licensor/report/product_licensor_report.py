# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm, fields
from openerp import tools


class ProductLicensorReport(orm.Model):
    _name = 'product.licensor.report'
    _description = "Product Licensor Report"
    _table = 'product_licensor_report'
    _auto = False
    _columns = {
        'licensor_id': fields.many2one('res.partner', 'Licensor'),
        'product_id': fields.many2one('product.product', 'Product'),
        'product_uom': fields.many2one(
            'product.uom', 'Reference Unit of Measure', required=True),
        'qty': fields.integer('Received quantity'),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'date': fields.date('Receipt Date', readonly=True),
        'year': fields.char('Year', size=64, required=False, readonly=True),
        'day': fields.char('Day', size=128, readonly=True),
        'month': fields.selection(
            [('01', 'January'), ('02', 'February'), ('03', 'March'),
                ('04', 'April'), ('05', 'May'), ('06', 'June'),
                ('07', 'July'), ('08', 'August'), ('09', 'September'),
                ('10', 'October'), ('11', 'November'), ('12', 'December')],
            'Month', readonly=True),
    }

    # TODO
    _order = 'licensor_id desc'

    def init(self, cr):
        # deal with uom conversion
        # set up the ID for this model.
        tools.sql.drop_view_if_exists(cr, 'product_licensor_report')
        cr.execute("""
            create or replace view product_licensor_report
            as (
                select
                    (concat(l.id, pl.licensor_id))::integer as id,
                    pl.licensor_id as licensor_id,
                    l.product_id as product_id,
                    sum(l.product_qty/u.factor*u2.factor) as qty,
                    t.uom_id as product_uom,
                    l.company_id as company_id,
                    l.date as date,
                    to_char(l.date, 'YYYY') as year,
                    to_char(l.date, 'MM') as month,
                    to_char(l.date, 'YYYY-MM-DD') as day
                from stock_move l
                    left join stock_picking sp on (
                        l.picking_id = sp.id)
                    left join product_licensor_rel pl on (
                        pl.product_id = l.product_id)
                    left join product_template t on (pl.product_id = t.id)
                    left join product_uom u on (u.id = l.product_uom)
                    left join product_uom u2 on (u2.id = t.uom_id)
                where
                    l.product_id in (
                        select distinct product_id from product_licensor_rel)
                    and
                        sp.type = 'in'
                    and
                        l.state = 'done'
                group by
                    l.product_id,
                    pl.licensor_id,
                    t.uom_id,
                    l.id,
                    l.company_id,
                    l.product_qty,
                    l.date)
            """)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
