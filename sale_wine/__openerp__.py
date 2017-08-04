# -*-coding:utf-8-*-
# © 2016 Elico Corp (https://www.elico-corp.com)
# Licence AGPL-3.0 or Later(http://www.gnu.org/licenses/agpl.html)

{
    'name': "Wine",
    'category': "Sales",
    'version': "7.0.1.0.0",
    'depends': ['product', 'product_custom_attributes',
                'base_custom_attributes'],
    'authors': "Chen Puyu",

    'description': """
   """,
    'data': [
        'security/ir.model.access.csv',
        'product_view.xml',
        'wine_view.xml'
    ]
}
