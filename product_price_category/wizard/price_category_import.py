# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Qiao Lei <Qiao.lei@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#nk
#    This program is distrisbuted in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
import decimal_precision as dp

import re
from tools.translate import _

class product_template(osv.osv):
    _inherit = 'product.template'
        
    def _auto_init(self, cr, context=None):
        super(product_template, self)._auto_init(cr, context)
        cr.execute("update product_template set pricecategory_id = 1 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = '12000' OR c.name = '12000X778' OR c.name = '13000' OR c.name = '11000' OR c.name = '13000X778' )") 
        cr.execute("update product_template set pricecategory_id = 2 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'TG')") 
        cr.execute("update product_template set pricecategory_id = 3 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'NK' OR c.name = 'NK series Assembled in Wujin')") 
        cr.execute("update product_template set pricecategory_id = 4 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'IA')") 
        cr.execute("update product_template set pricecategory_id = 5 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'IB-IS' OR c.name = 'IP' OR c.name = 'IC' OR c.name = 'IL' OR c.name = 'IM' OR c.name = 'IR' OR c.name = 'IZ' OR c.name = 'IH' OR c.name = 'IQ' OR c.name = 'IB/IS series Assembled in Wujin' OR c.name = 'IP series Assembled in Wujin')") 
        cr.execute("update product_template set pricecategory_id = 6 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name='IKN series Assembled in Wujin')") 
        cr.execute("update product_template set pricecategory_id = 7 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'JD')") 
        cr.execute("update product_template set pricecategory_id = 8 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'Sealing Boots')") 
        cr.execute("update product_template set pricecategory_id = 9 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'DA-DP-DS' OR c.name = 'IKD-IKE-IKH-IKN')") 
        cr.execute("update product_template set pricecategory_id = 10 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'CR65' OR c.name = 'CR36' )") 
        cr.execute("update product_template set pricecategory_id = 11 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'PBA')") 
        cr.execute("update product_template set pricecategory_id = 12 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'CP')") 
        cr.execute("update product_template set pricecategory_id = 13 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'PLK-PLR')") 
        cr.execute("update product_template set pricecategory_id = 14 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'D162' OR c.name = 'PHAP33' OR c.name = 'PHAP40' )") 
        cr.execute("update product_template set pricecategory_id = 15 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = '5000' OR c.name = '55000' OR c.name = '5000 series Assembled in Wujin')") 
        cr.execute("update product_template set pricecategory_id = 16 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'MP')") 
        cr.execute("update product_template set pricecategory_id = 17 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'ES')") 
        cr.execute("update product_template set pricecategory_id = 18 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'CG')") 
        cr.execute("update product_template set pricecategory_id = 20 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = '7000' OR c.name = '8000' OR c.name = 'KI' OR c.name = '9000' OR c.name = '10400' OR c.name = '10600' OR c.name = '18000 series Assembled in Wujin' OR c.name = '18000' OR c.name = '21000N' OR c.name = '25000 series Assembled in Wujin' OR c.name = '25000N' OR c.name = '8000 series Assembled in Wujin' OR c.name = '9000 series Assembled in Wujin' OR c.name = 'AS' OR c.name = 'AS series Assembled in Wujin' OR c.name = 'GH series Assembled in Wujin' OR c.name = 'G' OR c.name = 'IF' OR c.name = 'RT4-Others' OR c.name = 'S Rocker' OR c.name = 'S series Assembled in Wujin' OR c.name = 'S Toggle' OR c.name = 'SF' OR c.name = 'SP' OR c.name = 'SR' OR c.name = 'TL' OR c.name = 'TP' OR c.name = 'TR' OR c.name = 'VL' OR c.name = 'ZL' OR c.name = 'ZP' OR c.name = 'TT series Assembled in Wujin' OR c.name = 'Z series Assembled in Wujin' OR c.name = 'P36')") 
        cr.execute("update product_template set pricecategory_id = 21 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'CAP')") 
        cr.execute("update product_template set pricecategory_id = 22 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'Security Caps' OR c.name = 'ACCESS')") 
        cr.execute("update product_template set pricecategory_id = 23 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'KR' OR c.name = 'KI' OR c.name = 'KL' OR c.name = 'KR Rockers' OR c.name = 'KR series Assembled in Wujin')") 
        cr.execute("update product_template set pricecategory_id = 24 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'FM')") 
        cr.execute("update product_template set pricecategory_id = 25 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'AV')") 
        cr.execute("update product_template set pricecategory_id = 26 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'LPI')") 
        cr.execute("update product_template set pricecategory_id = 27 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = '2600'OR c.name = '1200' OR c.name = '6000' OR c.name = '1000' OR c.name = '1500' OR c.name = '1600' OR c.name = '2200' OR c.name = '3500' OR c.name = '1400N' OR c.name = '3500YT' OR c.name = '3600NF' OR c.name = '3600NFYT' OR c.name = '4100-4600' OR c.name = '4700-4800' OR c.name = '600 series Assembled in Wujin' OR c.name = '600NH' OR c.name = 'B series Terminal Posts' OR c.name = 'IT' OR c.name = 'KG' OR c.name = 'KS CANBus Module')") 
        cr.execute("update product_template set pricecategory_id = 28 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'FP')") 
        cr.execute("update product_template set pricecategory_id = 29 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.name = 'CT' OR c.name = 'CTYT')") 
        
        cr.execute("update product_template set pricecategory_id = 27 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.id = '230' OR c.id = '228' OR c.id = '226' OR c.id = '221' OR c.id = '232' OR c.id = '219' OR c.id = '223' OR c.id = '209' OR c.id = '259' OR c.id = '266' OR c.id = '2' OR c.id = '46')") 
        cr.execute("update product_template set pricecategory_id = 20 where product_template.id in (select t.id from product_template t JOIN product_category c on t.categ_id  = c.id where c.id = '220' OR c.id = '233' OR c.id = '229' OR c.id = '227' OR c.id = '224')") 
    

product_template()



