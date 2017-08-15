# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-Till Today Serpent Consulting Services PVT LTD (<http://www.serpentcs.com>)
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
    'name': 'Property Management System',
    'description': 'This module will help you to manage your real estate portfolio with Property valuation, Maintenance, Insurance, Utilities and Rent management with reminders for each KPIs.',
    'category': 'Website',
    'version': '1.25',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'depends': ['property_management','website','crm'],
    'data': [
        'views/property_list_view.xml',
        'views/templates.xml',
        'data/website_data.xml',
        'views/homepage.xml',
        'views/registration.xml',
        'views/website_settings.xml',
        'views/favourite_property.xml',
    ],
    'application': True,
    "oauth2": {
               'client_id': "868460361498-9kfl39ultph238npnbnleohafe9nfg5q.apps.googleusercontent.com",
               'scopes': ['https://www.googleapis.com/auth/drive']
    },
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
