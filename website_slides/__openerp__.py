# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Slides',
    'version': '8.0.1.0.0',
    'summary': 'Share and Publish Videos, Presentations and Documents',
    'category': 'website',
    'author': "Odoo SA, "
              "Incaser Informatica - Sergio Teruel, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/website',
    'depends': [
        'website',
        'website_mail',
    ],
    'data': [
        'view/res_config.xml',
        'view/website_slides.xml',
        'view/website_slides_embed.xml',
        'view/website_slides_backend.xml',
        'view/website_templates.xml',
        'data/website_slides_data.xml',
        'security/ir.model.access.csv',
        'security/website_slides_security.xml'
    ],
    'demo': [
        'data/website_slides_demo.xml'
    ],
    'installable': True,
}
