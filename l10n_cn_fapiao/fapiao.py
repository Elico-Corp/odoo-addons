# -*- coding: utf-8 -*-
# © 2004-2010 Tiny SPRL (http://tiny.be)
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import orm, fields


class fapiao(orm.Model):
    _name = "fapiao"
    _inherit = ['mail.thread']
    _order = "fapiao_date desc"

    _columns = {
        'fapiao_type': fields.selection(
            [('customer', 'Customer'), ('supplier', 'Supplier'),
             ('customer_credit_note', 'Customer Credit note'),
             ('customer_credit_note', 'Customer Credit note')],
            'Fapiao Type', required=True),
        'tax_type': fields.selection(
            [('13%', '13%'), ('17%', '17%'),
             ('normal', 'normal'), ('no_tax', 'no tax')],
            'Tax Type', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'fapiao_number': fields.integer(string="Fapiao Number", required=True),
        'fapiao_date': fields.date(string="Fapiao Date", required=True),
        'reception_date': fields.date(string="Reception Date"),
        'amount_with_taxes': fields.float('Fapiao total amount',
                                          required=True),
        'invoice_ids': fields.many2many('account.invoice', string="Invoices"),
        'tag_ids': fields.many2many('fapiao_tag', string="Tags"),
        'notes': fields.text(string="Notes"),
    }

    _defaults = {
        'tax_type': 'normal',
    }


class fapiao_tag(orm.Model):
    _name = 'fapiao_tag'

    _columns = {
        'name': fields.char("Name"),
    }

