# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Website remove Powered by Odoo',
    'version': '8.0.1.0.2',
    'category': 'website',
    'depends': ['website'],
    'author': 'Elico Corp',
    'license': 'AGPL-3',
    'description': """
        * This module allows you to remove Powered by Odoo from the website.
        * Note: This module interits the template from the webstie_sale. It may has conflict with certain themes.
        Please uninstall this module and update the website_sale if you failed to install the new theme.
        """,
    'website': 'https://www.elico-corp.com',
    'sequence': 1,
    'data': ['website_remove_powered_by_odoo.xml'],
    'installable': True,
    'application': False
}
