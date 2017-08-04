# -*- coding: utf-8 -*-
# © 2014 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or later(http://www.gnu.org/licenses/agpl.html)


{
    'name': 'MRP Wave Scheduler',
    'version': '7.0.1.0.0',
    'category': 'Stock',
    'sequence': 19,
    'summary': 'MRP Wave Scheduler',
    'description': """
        Stock Big Scheduler + AUTO/FORCE MO (For bundle products with BOM)
        ==================================================
        * Calculate scheduler based on DTS, PTS.
        * During scheulder, create and validate mo based on product definition.
        * Create  & Update Scheduler Staus message with message group 'scheduler'.
        * Launch scheduler in threads when a scheduler is not started.
        * Option to stop / kill the scheduler threads.
    """,
    'author': 'Elico Corp',
    'website': 'https://www.elico-corp.com',
    'images' : [],
    'depends': ['product','stock','delivery_plan'],
    'data': [
        'wizard/scheduler.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}


