# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Augustin Cisterne-Kaas
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
{
    'name': 'Paypal Credit card Acquirer',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: Paypal Credit card Implementation',
    'version': '1.0',
    'description': """Paypal Credit card Payment Acquirer""",
    'author': 'OpenERP SA',
    'depends': ['payment_paypal', 'website_sale'],
    'data': [
        'payment_view.xml',
        'data/payment.xml',
        'views/templates.xml'
    ],
    'installable': True,
}
