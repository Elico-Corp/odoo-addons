# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)

from openerp.osv import orm, fields


class sale_project(orm.Model):
    _name = 'sale.project'
    _description = 'Sale Project'

    def _get_name(self, cr, uid, ids, name, args, context=None):
        res = {}
        for p in self.browse(cr, uid, ids, context=context):
            res[p.id] = '%s-%s-%s' % (
                p.partner_id.name, p.project_partner.name, p.project_name)
        return res

    _columns = {
        'name': fields.function(
            _get_name,
            type='char',
            method=True,
            string='Full name',
            store=False),
        'partner_id': fields.many2one(
            'res.partner', 'Customer', required=True,
            domain="[('customer', '=', True)]"),
        'project_partner': fields.many2one(
            'res.partner', 'End User', required=True,
            domain="[('customer', '=', True)]"),
        'project_name': fields.char('Project Name', required=True),
        'property_product_pricelist': fields.property(
            'product.pricelist',
            type='many2one',
            relation='product.pricelist',
            domain=[('type', '=', 'sale')],
            string="Pricelist",
            method=True,
            view_load=True,
            help="This pricelist will be used, instead of the default one,\
                  for sales to the current partner"),
        'lead_ids': fields.one2many('crm.lead', 'sale_project_id', 'Leads')
    }

    def copy(self, cr, uid, record_id, default=None, context=None):
        if default is None:
            default = {}

        default.update({'lead_ids': []})

        return super(sale_project, self).copy(
            cr, uid, record_id, default, context)

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        res = {'value': {'property_product_pricelist': False}}
        if not part:
            return res

        part = self.pool.get('res.partner').browse(
            cr, uid, part, context=context)
        pricelist = part.property_product_pricelist and\
            part.property_product_pricelist.id or False
        if pricelist:
            res['value']['property_product_pricelist'] = pricelist
        return res
