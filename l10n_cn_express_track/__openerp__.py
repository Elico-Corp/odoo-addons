# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'l10n_cn_express_track',
    'version': '7.0.1.0.0',
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'summary': '',
    'description' : """
        Chinese Express Track
        * Track your Express Delivery (快递/"kuaidi") in China with OpenERP. More than 100 companies supported (DHL, SF, UPS, EMS, etc...)!

        * With this module, users can get a link directly in the OpenERP by entering tracking numbers and track the real-time delivery status by clicking this link.

        * To install this module, module web_url is needed, available here: http://www.emiprotechnologies.com/openerp/module7/

        * Next version will include a full API with state management.

    """,
    'depends': ['web_url','base'],
    'category': '',
    'sequence': 10,
    'demo': [],
    'data': [
        'express_view.xml',
        'security/ir.model.access.csv'
        ],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css' : [],
}


