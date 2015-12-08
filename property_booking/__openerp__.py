# -*- coding: utf-8 -*-
############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-Today Serpent Consulting Services PVT LTD
#    (<http://www.serpentcs.com>)
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
############################################################################
{
    'name': 'Property Booking',
    'version': '2.0',
    'category': 'Real Estate',
    'description': """
Property Management System
=========================
This module gives the features for create property with gross value, number of towers, ground rent etc.
also create sub property. where you can mentions Parent Property,number of floors , properties per floor,etc.
and show sub property status either it's available or booked or any other states.
     """,
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'depends': ['property_management', 'web_o2m_multi_delete'],
    'demo': ['views/property_booking_data.xml'],
    'data': ['security/ir.model.access.csv',
            'wizard/merge_property_wizard_view.xml',
            'wizard/property_book_wizard.xml',
            "views/property_booking_view.xml"],
    'auto_install': False,
    'installable': True,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
