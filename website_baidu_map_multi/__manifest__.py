# 2016-2019 Elico Corp (https://www.elico-corp.com).
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Website Baidu Map Multi',
    'version': '12.0.1.0.0',
    'category': 'Hidden',
    'depends': ['website', 'base', 'website_baidu_map'],
    'author': 'Elico-Corp,Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'website': 'https://www.elico-corp.com',
    'data': [
        'views/company_shop_view.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',
    ],
    'installable': True,
    'application': False
}
