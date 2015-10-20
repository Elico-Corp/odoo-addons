# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (c) 2010-2015 Elico Corp.
#    Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as publishe
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public Licens
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{'name': 'Contact Form CAPTCHA',
 'version': '1.0',
 'category': 'Website',
 'depends': ['website_crm', 'website_captcha_nogoogle'],
 'author': 'Elico Corp,Odoo Community Association (OCA)',
 # 'license': 'LGPL-3',
 'website': 'https://www.elico-corp.com',
 'currency': 'EUR',
 'price': 4.9,
 'data': [
     'views/website_crm.xml',
 ],
 'installable': True,
 'auto_install': False}
