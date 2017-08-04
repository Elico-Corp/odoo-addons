# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


from openerp.osv import osv
from openerp.addons.account_anglo_saxon.invoice import (
    account_invoice_line)


# monkey patch, rewrite the old function
# can not remove the incorrect value from old module
def move_line_get_new(self, cr, uid, invoice_id, context=None):
    res = super(account_invoice_line,self).move_line_get(cr, uid, invoice_id, context=context)
    inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
    company_currency = inv.company_id.currency_id.id

    #rewrite get price based on _compute_purchase_price
    def get_price(cr, uid, inv, company_currency,i_line):
        cur_obj = self.pool.get('res.currency')
        product_obj = self.pool.get('product.product')
        standard_price = product_obj._compute_purchase_price(cr, uid, [i_line.product_id.id])[i_line.product_id.id]
        if inv.currency_id.id != company_currency:
            price = cur_obj.compute(cr, uid, company_currency, inv.currency_id.id, standard_price * i_line.quantity, context={'date': inv.date_invoice})
        else:
            price = standard_price * i_line.quantity
        return price

    if inv.type in ('out_invoice','out_refund'):
        for i_line in inv.invoice_line:
            if i_line.product_id and i_line.product_id.valuation == 'real_time':
                if inv.type == 'out_invoice':
                    # debit account dacc will be the output account
                    # first check the product, if empty check the category
                    dacc = i_line.product_id.property_stock_account_output and i_line.product_id.property_stock_account_output.id
                    if not dacc:
                        dacc = i_line.product_id.categ_id.property_stock_account_output_categ and i_line.product_id.categ_id.property_stock_account_output_categ.id
                else:
                    # = out_refund
                    # debit account dacc will be the input account
                    # first check the product, if empty check the category
                    dacc = i_line.product_id.property_stock_account_input and i_line.product_id.property_stock_account_input.id
                    if not dacc:
                        dacc = i_line.product_id.categ_id.property_stock_account_input_categ and i_line.product_id.categ_id.property_stock_account_input_categ.id
                # in both cases the credit account cacc will be the expense account
                # first check the product, if empty check the category
                cacc = i_line.product_id.property_account_expense and i_line.product_id.property_account_expense.id
                if not cacc:
                    cacc = i_line.product_id.categ_id.property_account_expense_categ and i_line.product_id.categ_id.property_account_expense_categ.id
                if dacc and cacc:
                    res.append({
                        'type':'src',
                        'name': i_line.name[:64],
                        'price_unit':i_line.product_id.standard_price,
                        'quantity':i_line.quantity,
                        'price':get_price(cr, uid, inv, company_currency, i_line),
                        'account_id':dacc,
                        'product_id':i_line.product_id.id,
                        'uos_id':i_line.uos_id.id,
                        'account_analytic_id': False,
                        'taxes':i_line.invoice_line_tax_id,
                        })

                    res.append({
                        'type':'src',
                        'name': i_line.name[:64],
                        'price_unit':i_line.product_id.standard_price,
                        'quantity':i_line.quantity,
                        'price': -1 * get_price(cr, uid, inv, company_currency, i_line),
                        'account_id':cacc,
                        'product_id':i_line.product_id.id,
                        'uos_id':i_line.uos_id.id,
                        'account_analytic_id': False,
                        'taxes':i_line.invoice_line_tax_id,
                        })
    elif inv.type in ('in_invoice','in_refund'):
        for i_line in inv.invoice_line:
            if i_line.product_id and i_line.product_id.valuation == 'real_time':
                if i_line.product_id.type != 'service':
                    # get the price difference account at the product
                    acc = i_line.product_id.property_account_creditor_price_difference and i_line.product_id.property_account_creditor_price_difference.id
                    if not acc:
                        # if not found on the product get the price difference account at the category
                        acc = i_line.product_id.categ_id.property_account_creditor_price_difference_categ and i_line.product_id.categ_id.property_account_creditor_price_difference_categ.id
                    a = None
                    if inv.type == 'in_invoice':
                        # oa will be the stock input account
                        # first check the product, if empty check the category
                        oa = i_line.product_id.property_stock_account_input and i_line.product_id.property_stock_account_input.id
                        if not oa:
                            oa = i_line.product_id.categ_id.property_stock_account_input_categ and i_line.product_id.categ_id.property_stock_account_input_categ.id
                    else:
                        # = in_refund
                        # oa will be the stock output account
                        # first check the product, if empty check the category
                        oa = i_line.product_id.property_stock_account_output and i_line.product_id.property_stock_account_output.id
                        if not oa:
                            oa = i_line.product_id.categ_id.property_stock_account_output_categ and i_line.product_id.categ_id.property_stock_account_output_categ.id
                    if oa:
                        # get the fiscal position
                        fpos = i_line.invoice_id.fiscal_position or False
                        a = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, oa)
                    diff_res = []
                    # calculate and write down the possible price difference between invoice price and product price
                    for line in res:
                        if a == line['account_id'] and i_line.product_id.id == line['product_id']:
                            uom = i_line.product_id.uos_id or i_line.product_id.uom_id
                            standard_price = self.pool.get('product.uom')._compute_price(cr, uid, uom.id, i_line.product_id.standard_price, i_line.uos_id.id)
                            if standard_price != i_line.price_unit and line['price_unit'] == i_line.price_unit and acc:
                                price_diff = i_line.price_unit - standard_price
                                line.update({'price':standard_price * line['quantity']})
                                diff_res.append({
                                    'type':'src',
                                    'name': i_line.name[:64],
                                    'price_unit':price_diff,
                                    'quantity':line['quantity'],
                                    'price': price_diff * line['quantity'],
                                    'account_id':acc,
                                    'product_id':line['product_id'],
                                    'uos_id':line['uos_id'],
                                    'account_analytic_id':line['account_analytic_id'],
                                    'taxes':line.get('taxes',[]),
                                    })
                    res += diff_res
    return res

account_invoice_line.move_line_get = move_line_get_new

