# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Stock Batch Track',
    'version': '7.0.1.0.0',
    'category': 'Generic Modules/Stock',
    'description': """
        Batch Process:
            * Set Pack
            * Cancel Availability
            * Check Availability
            * Force Availability
            * Auto Process to finish
    """,
    'author': 'Elico Corp.',
    'website': 'https://www.elico-corp.com',
    'depends': ['stock'],
    'update_xml': ['wizard/stock_batch_track_view.xml',
        'stock_batch_track_report_view.xml'],
    'installable': True,
}
