# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2014 Serpent Consulting Services Pvt. Ltd.
#                                        (<http://serpentcs.com>).
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
    'name': 'Delete Multiple o2m Records ',
    'version': '1.0',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'description':
        """
        This module is developed to extend the functionality of list view.
        There are certain occasions where you need to delete multiple one2many records in list view.
        This module fills the gap at certain extent by allowing to delete multiple one2many records in
        list view.
        """,
    'data':[
            'view/templates.xml',
            ],
    'depends': ['web'],
    'qweb' : [
        "static/src/xml/web_o2m_multi_delete.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
